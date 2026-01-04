// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/*//////////////////////////////////////////////////////////////
                    PRODUCTION FLASH ARB EXECUTOR V2
                    (Enhanced Security Version)
//////////////////////////////////////////////////////////////*/

/*//////////////////////////////////////////////////////////////
                            INTERFACES
//////////////////////////////////////////////////////////////*/

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
}

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
                    ENHANCED FLASH ARB EXECUTOR
//////////////////////////////////////////////////////////////*/

contract FlashArbExecutorV2 {
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
    error InvalidDex(uint8 dexId);
    error NotVault();
    error NotPool();
    error Paused();
    error ReentrancyGuard();
    error InvalidAddress();
    error TooManySteps();

    /*//////////////////////////////////////////////////////////////
                            CONSTANTS
    //////////////////////////////////////////////////////////////*/

    uint8 internal constant PROVIDER_BALANCER = 1;
    uint8 internal constant PROVIDER_AAVE = 2;

    uint8 internal constant DEX_UNIV2_QUICKSWAP = 1;
    uint8 internal constant DEX_UNIV2_SUSHISWAP = 2;
    uint8 internal constant DEX_UNIV3 = 3;

    uint8 internal constant MAX_STEPS = 10; // Maximum steps to prevent gas issues
    uint256 internal constant DEADLINE_BUFFER = 300; // 5 minutes

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
    bool public paused;
    
    // Reentrancy guard
    uint256 private _status;
    uint256 private constant _NOT_ENTERED = 1;
    uint256 private constant _ENTERED = 2;

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

    event PausedStateChanged(bool isPaused);
    event MinProfitUpdated(uint256 newMinProfit);
    event DexRouterUpdated(uint8 dexId, address router);

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
        if (_balancerVault == address(0)) revert InvalidAddress();
        if (_aavePool == address(0)) revert InvalidAddress();
        
        owner = msg.sender;
        balancerVault = IBalancerVault(_balancerVault);
        aavePool = IAaveV3Pool(_aavePool);

        dexRouter[DEX_UNIV2_QUICKSWAP] = _quickswapRouter;
        dexRouter[DEX_UNIV2_SUSHISWAP] = _sushiswapRouter;
        dexRouter[DEX_UNIV3] = _uniswapV3Router;

        minProfitWei = _minProfitWei;
        _status = _NOT_ENTERED;
    }

    /*//////////////////////////////////////////////////////////////
                            MODIFIERS
    //////////////////////////////////////////////////////////////*/

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier whenNotPaused() {
        if (paused) revert Paused();
        _;
    }

    modifier nonReentrant() {
        if (_status == _ENTERED) revert ReentrancyGuard();
        _status = _ENTERED;
        _;
        _status = _NOT_ENTERED;
    }

    /*//////////////////////////////////////////////////////////////
                        MAIN ENTRY POINT
    //////////////////////////////////////////////////////////////*/

    function executeFlashArb(
        uint8 providerId,
        address loanToken,
        uint256 loanAmount,
        bytes calldata plan
    ) external onlyOwner whenNotPaused nonReentrant {
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
        uint256 minProfit;
        uint8 stepCount;

        assembly {
            let data := add(plan, 32)
            deadline := shr(216, mload(add(data, 2)))
            minProfit := mload(add(data, 27))
            stepCount := shr(248, mload(add(data, 59)))
        }

        if (block.timestamp > deadline) revert DeadlineExpired();
        if (stepCount > MAX_STEPS) revert TooManySteps();

        uint256 cursor = 60;
        for (uint8 i = 0; i < stepCount; i++) {
            cursor = _executeStep(plan, cursor, i);
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
        uint8 stepIndex
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
            auxData
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
        bytes memory auxData
    ) internal returns (uint256 amountOut) {
        if (dexId == DEX_UNIV2_QUICKSWAP || dexId == DEX_UNIV2_SUSHISWAP) {
            return _swapUniV2(dexId, tokenIn, tokenOut, amountIn, minOut, auxData);
        } else if (dexId == DEX_UNIV3) {
            return _swapUniV3(tokenIn, tokenOut, amountIn, minOut, auxData);
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
        bytes memory auxData
    ) internal returns (uint256 amountOut) {
        address router = dexRouter[dexId];
        if (router == address(0)) revert InvalidDex(dexId);

        address[] memory path = abi.decode(auxData, (address[]));
        if (path.length < 2) revert InvalidPlan();
        if (path[0] != tokenIn || path[path.length - 1] != tokenOut) revert InvalidPlan();

        IERC20(tokenIn).approve(router, amountIn);

        uint256[] memory amounts = IUniswapV2Router(router).swapExactTokensForTokens(
            amountIn,
            minOut,
            path,
            address(this),
            block.timestamp + DEADLINE_BUFFER
        );

        return amounts[amounts.length - 1];
    }

    function _swapUniV3(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minOut,
        bytes memory auxData
    ) internal returns (uint256 amountOut) {
        address router = dexRouter[DEX_UNIV3];
        if (router == address(0)) revert InvalidDex(DEX_UNIV3);

        (uint24 fee, uint160 sqrtPriceLimitX96) = abi.decode(auxData, (uint24, uint160));

        IERC20(tokenIn).approve(router, amountIn);

        IUniswapV3Router.ExactInputSingleParams memory params = IUniswapV3Router.ExactInputSingleParams({
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            fee: fee,
            recipient: address(this),
            deadline: block.timestamp + DEADLINE_BUFFER,
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
        if (token == address(0)) revert InvalidAddress();
        uint256 balance = IERC20(token).balanceOf(address(this));
        require(amount <= balance, "Amount exceeds balance");
        IERC20(token).transfer(owner, amount);
    }

    function withdrawAllToken(address token) external onlyOwner {
        if (token == address(0)) revert InvalidAddress();
        uint256 bal = IERC20(token).balanceOf(address(this));
        if (bal > 0) {
            IERC20(token).transfer(owner, bal);
        }
    }

    function setDexRouter(uint8 dexId, address router) external onlyOwner {
        if (router == address(0)) revert InvalidAddress();
        dexRouter[dexId] = router;
        emit DexRouterUpdated(dexId, router);
    }

    function setMinProfit(uint256 value) external onlyOwner {
        minProfitWei = value;
        emit MinProfitUpdated(value);
    }

    function setPaused(bool _paused) external onlyOwner {
        paused = _paused;
        emit PausedStateChanged(_paused);
    }

    function rescueETH() external onlyOwner {
        uint256 balance = address(this).balance;
        if (balance > 0) {
            (bool success, ) = payable(owner).call{value: balance}("");
            require(success, "ETH transfer failed");
        }
    }

    receive() external payable {}
}
