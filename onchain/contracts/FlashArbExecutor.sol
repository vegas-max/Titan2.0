// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/*//////////////////////////////////////////////////////////////
                            INTERFACES
//////////////////////////////////////////////////////////////*/

interface IBalancerVault {
    function flashLoan(
        address recipient,
        IERC20[] memory tokens,
        uint256[] memory amounts,
        bytes memory userData
    ) external;
}

interface IAaveV3Pool {
    function flashLoanSimple(
        address receiverAddress,
        address asset,
        uint256 amount,
        bytes calldata params,
        uint16 referralCode
    ) external;
}

interface IUniswapV2Router {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
}

interface IUniswapV3Router {
    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }

    function exactInputSingle(ExactInputSingleParams calldata params)
        external
        returns (uint256 amountOut);
}

/*//////////////////////////////////////////////////////////////
                    PRODUCTION FLASH ARB EXECUTOR
//////////////////////////////////////////////////////////////*/

contract FlashArbExecutor is ReentrancyGuard {
    using SafeERC20 for IERC20;
    /*//////////////////////////////////////////////////////////////
                                ERRORS
    //////////////////////////////////////////////////////////////*/

    error NotOwner();
    error InvalidProvider();
    error InvalidPlan();
    error DeadlineExpired();
    error ProfitTooLow(uint256 got, uint256 need);
    error FlashLoanFailed();
    error InsufficientRepayment();
    error StepFailed(uint8 stepIndex);
    error InvalidDex(uint8 dexId);
    error NotVault();
    error NotPool();
    error InvalidToken();
    error InvalidAmount();

    /*//////////////////////////////////////////////////////////////
                            CONSTANTS
    //////////////////////////////////////////////////////////////*/

    uint8 internal constant PROVIDER_BALANCER = 1;
    uint8 internal constant PROVIDER_AAVE = 2;

    uint8 internal constant DEX_UNIV2_QUICKSWAP = 1;
    uint8 internal constant DEX_UNIV2_SUSHISWAP = 2;
    uint8 internal constant DEX_UNIV3 = 3;

    /*//////////////////////////////////////////////////////////////
                            IMMUTABLES
    //////////////////////////////////////////////////////////////*/

    address public immutable owner;
    IBalancerVault public immutable balancerVault;
    IAaveV3Pool public immutable aavePool;

    /*//////////////////////////////////////////////////////////////
                            STORAGE
    //////////////////////////////////////////////////////////////*/

    mapping(uint8 => address) public dexRouter;
    uint256 public minProfitWei;

    /*//////////////////////////////////////////////////////////////
                            EVENTS
    //////////////////////////////////////////////////////////////*/

    event ArbExecuted(
        uint8 indexed provider,
        address indexed loanToken,
        uint256 loanAmount,
        uint256 profit
    );

    event StepExecuted(
        uint8 indexed stepIndex,
        uint8 indexed dexId,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOut
    );

    /*//////////////////////////////////////////////////////////////
                            CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/

    constructor(
        address _balancerVault,
        address _aavePool,
        address _quickswapRouter,
        address _sushiswapRouter,
        address _uniswapV3Router,
        uint256 _minProfitWei
    ) {
        owner = msg.sender;
        balancerVault = IBalancerVault(_balancerVault);
        aavePool = IAaveV3Pool(_aavePool);

        dexRouter[DEX_UNIV2_QUICKSWAP] = _quickswapRouter;
        dexRouter[DEX_UNIV2_SUSHISWAP] = _sushiswapRouter;
        dexRouter[DEX_UNIV3] = _uniswapV3Router;

        minProfitWei = _minProfitWei;
    }

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    /*//////////////////////////////////////////////////////////////
                        MAIN ENTRY POINT
    //////////////////////////////////////////////////////////////*/

    function executeFlashArb(
        uint8 providerId,
        address loanToken,
        uint256 loanAmount,
        bytes calldata plan
    ) external onlyOwner nonReentrant {
        // CRITICAL FIX #4: Pre-validate BEFORE taking flash loan
        if (loanToken == address(0)) revert InvalidToken();
        if (loanAmount == 0) revert InvalidAmount();
        if (plan.length < 60) revert InvalidPlan();

        if (providerId == PROVIDER_BALANCER) {
            _flashBalancer(loanToken, loanAmount, plan);
        } else if (providerId == PROVIDER_AAVE) {
            _flashAave(loanToken, loanAmount, plan);
        } else {
            revert InvalidProvider();
        }
    }

    /*//////////////////////////////////////////////////////////////
                    FLASH LOAN DISPATCHERS
    //////////////////////////////////////////////////////////////*/

    function _flashBalancer(
        address token,
        uint256 amount,
        bytes calldata plan
    ) internal {
        // FIX 1: Initialize the arrays properly
        IERC20[] memory tokens = new IERC20[](1);
        uint256[] memory amounts = new uint256[](1);

        tokens[0] = IERC20(token);
        amounts[0] = amount;

        balancerVault.flashLoan(
            address(this),
            tokens,
            amounts,
            abi.encode(token, amount, plan)
        );
    }

    function _flashAave(
        address token,
        uint256 amount,
        bytes calldata plan
    ) internal {
        aavePool.flashLoanSimple(
            address(this),
            token,
            amount,
            abi.encode(token, amount, plan),
            0
        );
    }

    /*//////////////////////////////////////////////////////////////
                BALANCER FLASH LOAN CALLBACK
    //////////////////////////////////////////////////////////////*/

    function receiveFlashLoan(
        IERC20[] memory tokens,
        uint256[] memory amounts,
        uint256[] memory feeAmounts,
        bytes memory userData
    ) external nonReentrant {
        // CRITICAL FIX #2: Add reentrancy protection
        if (msg.sender != address(balancerVault)) revert NotVault();
        if (tokens.length != 1 || amounts.length != 1 || feeAmounts.length != 1) revert FlashLoanFailed();

        (address loanToken, uint256 loanAmount, bytes memory plan) =
            abi.decode(userData, (address, uint256, bytes));

        if (loanToken != address(tokens[0]) || loanAmount != amounts[0]) revert FlashLoanFailed();

        uint256 profit = _executePlan(loanToken, loanAmount, feeAmounts[0], plan);

        uint256 repayment = amounts[0] + feeAmounts[0];
        uint256 bal = IERC20(loanToken).balanceOf(address(this));
        if (bal < repayment) revert InsufficientRepayment();

        IERC20(loanToken).approve(address(balancerVault), repayment);

        emit ArbExecuted(PROVIDER_BALANCER, loanToken, loanAmount, profit);
    }

    /*//////////////////////////////////////////////////////////////
                AAVE FLASH LOAN CALLBACK
    //////////////////////////////////////////////////////////////*/

    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external nonReentrant returns (bool) {
        // CRITICAL FIX #2: Add reentrancy protection
        if (msg.sender != address(aavePool)) revert NotPool();
        if (initiator != address(this)) revert FlashLoanFailed();

        (address loanToken, uint256 loanAmount, bytes memory plan) =
            abi.decode(params, (address, uint256, bytes));

        if (loanToken != asset || loanAmount != amount) revert FlashLoanFailed();

        uint256 profit = _executePlan(asset, amount, premium, plan);

        IERC20(asset).approve(address(aavePool), amount + premium);

        emit ArbExecuted(PROVIDER_AAVE, loanToken, loanAmount, profit);
        return true;
    }

    /*//////////////////////////////////////////////////////////////
                    CORE EXECUTION LOGIC
    //////////////////////////////////////////////////////////////*/

    function _executePlan(
        address loanToken,
        uint256 loanAmount,
        uint256 fee,
        bytes memory plan
    ) internal returns (uint256 profit) {
        
        // Header Parsing
        uint8 version = uint8(plan[0]);
        if (version != 1) revert InvalidPlan();

        uint40 deadline;
        address baseToken;
        uint256 minProfit;
        uint8 stepCount;

        assembly {
            let data := add(plan, 32)
            deadline := shr(216, mload(add(data, 2)))
            baseToken := shr(96, mload(add(data, 7)))
            minProfit := mload(add(data, 27))
            stepCount := shr(248, mload(add(data, 59)))
        }

        baseToken; // Silence warning

        // CRITICAL FIX #1: Check deadline BEFORE any swaps
        if (block.timestamp > deadline) revert DeadlineExpired();

        uint256 cursor = 60;
        for (uint8 i = 0; i < stepCount; i++) {
            cursor = _executeStep(plan, cursor, i, deadline);
        }

        uint256 endBal = IERC20(loanToken).balanceOf(address(this));
        uint256 totalCost = loanAmount + fee;

        if (endBal < totalCost) revert InsufficientRepayment();

        profit = endBal - totalCost;

        uint256 need = (minProfit > minProfitWei) ? minProfit : minProfitWei;
        if (profit < need) revert ProfitTooLow(profit, need);

        return profit;
    }

    /*//////////////////////////////////////////////////////////////
                        STEP EXECUTION
    //////////////////////////////////////////////////////////////*/

    function _executeStep(
        bytes memory plan,
        uint256 cursor,
        uint8 stepIndex,
        uint40 deadline  // CRITICAL FIX #1: Accept deadline parameter
    ) internal returns (uint256 newCursor) {
        if (cursor + 108 > plan.length) revert InvalidPlan();

        uint8 dexId;
        uint8 action;
        address tokenIn;
        address tokenOut;
        uint256 amountIn;
        uint256 minOut;
        uint16 auxLen;

        assembly {
            let ptr := add(add(plan, 32), cursor)
            dexId := shr(248, mload(ptr))
            
            ptr := add(ptr, 1)
            action := shr(248, mload(ptr))
            
            ptr := add(ptr, 1)
            tokenIn := shr(96, mload(ptr))
            
            ptr := add(ptr, 20)
            tokenOut := shr(96, mload(ptr))
            
            ptr := add(ptr, 20)
            amountIn := mload(ptr)
            
            ptr := add(ptr, 32)
            minOut := mload(ptr)
            
            ptr := add(ptr, 32)
            auxLen := shr(240, mload(ptr))
        }

        action; // Silence warning

        if (amountIn == 0) {
            amountIn = IERC20(tokenIn).balanceOf(address(this));
        }

        uint256 auxStart = cursor + 108;
        if (auxStart + auxLen > plan.length) revert InvalidPlan();

        bytes memory auxData = new bytes(auxLen);
        for (uint256 i = 0; i < auxLen; i++) {
            auxData[i] = plan[auxStart + i];
        }

        uint256 amountOut = _dispatchSwap(
            dexId,
            tokenIn,
            tokenOut,
            amountIn,
            minOut,
            auxData,
            deadline  // CRITICAL FIX #1: Pass deadline to swap functions
        );

        emit StepExecuted(stepIndex, dexId, tokenIn, tokenOut, amountIn, amountOut);

        return auxStart + auxLen;
    }

    /*//////////////////////////////////////////////////////////////
                        DEX DISPATCH
    //////////////////////////////////////////////////////////////*/

    function _dispatchSwap(
        uint8 dexId,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minOut,
        bytes memory auxData,
        uint40 deadline  // CRITICAL FIX #1: Accept deadline parameter
    ) internal returns (uint256 amountOut) {
        if (dexId == DEX_UNIV2_QUICKSWAP || dexId == DEX_UNIV2_SUSHISWAP) {
            return _swapUniV2(dexId, tokenIn, tokenOut, amountIn, minOut, auxData, deadline);
        } else if (dexId == DEX_UNIV3) {
            return _swapUniV3(tokenIn, tokenOut, amountIn, minOut, auxData, deadline);
        } else {
            revert InvalidDex(dexId);
        }
    }

    function _swapUniV2(
        uint8 dexId,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minOut,
        bytes memory auxData,
        uint40 deadline  // CRITICAL FIX #1: Accept deadline parameter
    ) internal returns (uint256 amountOut) {
        address router = dexRouter[dexId];
        if (router == address(0)) revert InvalidDex(dexId);

        address[] memory path = abi.decode(auxData, (address[]));
        if (path.length < 2) revert InvalidPlan();
        if (path[0] != tokenIn || path[path.length - 1] != tokenOut) revert InvalidPlan();

        // Use SafeERC20 for robust approval handling across all token types
        IERC20(tokenIn).forceApprove(router, amountIn);

        uint256[] memory amounts = IUniswapV2Router(router).swapExactTokensForTokens(
            amountIn,
            minOut,
            path,
            address(this),
            deadline  // Use plan deadline, not block.timestamp
        );

        return amounts[amounts.length - 1];
    }

    function _swapUniV3(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minOut,
        bytes memory auxData,
        uint40 deadline  // CRITICAL FIX #1: Accept deadline parameter
    ) internal returns (uint256 amountOut) {
        address router = dexRouter[DEX_UNIV3];
        if (router == address(0)) revert InvalidDex(DEX_UNIV3);

        (uint24 fee, uint160 sqrtPriceLimitX96) = abi.decode(auxData, (uint24, uint160));

        // Use SafeERC20 for robust approval handling across all token types
        IERC20(tokenIn).forceApprove(router, amountIn);

        IUniswapV3Router.ExactInputSingleParams memory params = IUniswapV3Router.ExactInputSingleParams({
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            fee: fee,
            recipient: address(this),
            deadline: deadline,  // CRITICAL FIX #1: Use plan deadline, not block.timestamp
            amountIn: amountIn,
            amountOutMinimum: minOut,
            sqrtPriceLimitX96: sqrtPriceLimitX96
        });

        amountOut = IUniswapV3Router(router).exactInputSingle(params);

        return amountOut;
    }

    /*//////////////////////////////////////////////////////////////
                        PROFIT & ADMIN
    //////////////////////////////////////////////////////////////*/

    function withdrawToken(address token, uint256 amount) external onlyOwner {
        IERC20(token).transfer(owner, amount);
    }

    function withdrawAllToken(address token) external onlyOwner {
        uint256 bal = IERC20(token).balanceOf(address(this));
        IERC20(token).transfer(owner, bal);
    }

    function setDexRouter(uint8 dexId, address router) external onlyOwner {
        dexRouter[dexId] = router;
    }

    function setMinProfit(uint256 value) external onlyOwner {
        minProfitWei = value;
    }

    function rescueETH() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }

    receive() external payable {}
}
