// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/*//////////////////////////////////////////////////////////////
                    HFT EXECUTOR CONTRACT
    High-Frequency Trading optimized for direct pair swaps
    Designed for simple A->B arbitrage on V2 forks
//////////////////////////////////////////////////////////////*/

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
}

interface IUniswapV2Pair {
    function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) external;
    function token0() external view returns (address);
    function token1() external view returns (address);
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast);
}

interface IBalancerVault {
    function flashLoan(
        address recipient,
        IERC20[] memory tokens,
        uint256[] memory amounts,
        bytes memory userData
    ) external;
}

/*//////////////////////////////////////////////////////////////
                        HFT EXECUTOR
//////////////////////////////////////////////////////////////*/

contract HFTExecutor {
    /*//////////////////////////////////////////////////////////////
                            ERRORS
    //////////////////////////////////////////////////////////////*/
    
    error NotOwner();
    error NotVault();
    error InvalidPair();
    error InsufficientProfit();
    error FlashLoanFailed();
    
    /*//////////////////////////////////////////////////////////////
                        STATE VARIABLES
    //////////////////////////////////////////////////////////////*/
    
    address public immutable owner;
    IBalancerVault public immutable balancerVault;
    uint256 public minProfitWei;
    
    /*//////////////////////////////////////////////////////////////
                        CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/
    
    constructor(address _balancerVault, uint256 _minProfitWei) {
        owner = msg.sender;
        balancerVault = IBalancerVault(_balancerVault);
        minProfitWei = _minProfitWei;
    }
    
    /*//////////////////////////////////////////////////////////////
                        MODIFIERS
    //////////////////////////////////////////////////////////////*/
    
    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }
    
    modifier onlyVault() {
        if (msg.sender != address(balancerVault)) revert NotVault();
        _;
    }
    
    /*//////////////////////////////////////////////////////////////
                    ARBITRAGE EXECUTION
    //////////////////////////////////////////////////////////////*/
    
    /**
     * @notice Execute arbitrage between two V2 pairs
     * @param _poolA First Uniswap V2 pair address
     * @param _poolB Second Uniswap V2 pair address
     * @param _amount Flash loan amount in WEI
     */
    function startArbitrage(
        address _poolA,
        address _poolB,
        uint256 _amount
    ) external onlyOwner {
        // Validate inputs
        if (_poolA == address(0) || _poolB == address(0)) revert InvalidPair();
        
        // Get token from poolA
        address token = IUniswapV2Pair(_poolA).token0();
        
        // Prepare flash loan
        IERC20[] memory tokens = new IERC20[](1);
        tokens[0] = IERC20(token);
        
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = _amount;
        
        // Encode callback data
        bytes memory userData = abi.encode(_poolA, _poolB, _amount);
        
        // Execute flash loan
        balancerVault.flashLoan(address(this), tokens, amounts, userData);
    }
    
    /**
     * @notice Balancer flash loan callback
     */
    function receiveFlashLoan(
        IERC20[] memory tokens,
        uint256[] memory amounts,
        uint256[] memory feeAmounts,
        bytes memory userData
    ) external onlyVault {
        // Decode parameters
        (address poolA, address poolB, uint256 amount) = abi.decode(userData, (address, address, uint256));
        
        address token = address(tokens[0]);
        uint256 flashAmount = amounts[0];
        uint256 flashFee = feeAmounts[0];
        
        // Record initial balance
        uint256 balanceBefore = IERC20(token).balanceOf(address(this));
        
        // Execute swap on Pool A
        _executeV2Swap(poolA, token, flashAmount);
        
        // Execute swap on Pool B (reverse direction)
        uint256 intermediateBalance = IERC20(token).balanceOf(address(this));
        _executeV2Swap(poolB, token, intermediateBalance);
        
        // Check profit
        uint256 balanceAfter = IERC20(token).balanceOf(address(this));
        uint256 repayAmount = flashAmount + flashFee;
        
        if (balanceAfter < repayAmount) revert FlashLoanFailed();
        
        uint256 profit = balanceAfter - repayAmount;
        if (profit < minProfitWei) revert InsufficientProfit();
        
        // Repay flash loan
        IERC20(token).transfer(address(balancerVault), repayAmount);
        
        // Transfer profit to owner
        if (profit > 0) {
            IERC20(token).transfer(owner, profit);
        }
    }
    
    /**
     * @dev Execute swap on Uniswap V2 pair
     */
    function _executeV2Swap(address pair, address tokenIn, uint256 amountIn) internal {
        IUniswapV2Pair pool = IUniswapV2Pair(pair);
        
        address token0 = pool.token0();
        address token1 = pool.token1();
        
        (uint112 reserve0, uint112 reserve1,) = pool.getReserves();
        
        // Determine input/output tokens
        bool isToken0 = tokenIn == token0;
        
        // Calculate output amount (simplified, should use actual V2 formula)
        uint256 amountOut;
        if (isToken0) {
            amountOut = (amountIn * 997 * reserve1) / (reserve0 * 1000 + amountIn * 997);
        } else {
            amountOut = (amountIn * 997 * reserve0) / (reserve1 * 1000 + amountIn * 997);
        }
        
        // Transfer tokens to pair
        IERC20(tokenIn).transfer(pair, amountIn);
        
        // Execute swap
        if (isToken0) {
            pool.swap(0, amountOut, address(this), new bytes(0));
        } else {
            pool.swap(amountOut, 0, address(this), new bytes(0));
        }
    }
    
    /*//////////////////////////////////////////////////////////////
                        ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/
    
    /**
     * @notice Update minimum profit threshold
     */
    function setMinProfit(uint256 _minProfitWei) external onlyOwner {
        minProfitWei = _minProfitWei;
    }
    
    /**
     * @notice Emergency token withdrawal
     */
    function withdrawToken(address token, uint256 amount) external onlyOwner {
        IERC20(token).transfer(owner, amount);
    }
}
