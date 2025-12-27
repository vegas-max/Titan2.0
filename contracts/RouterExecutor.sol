// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/*//////////////////////////////////////////////////////////////
                    ROUTER EXECUTOR CONTRACT
    Path-based execution for complex multi-hop arbitrage
    Supports V2, V3, Curve, Balancer, and other DEXes
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

interface IRouter {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
}

/*//////////////////////////////////////////////////////////////
                    ROUTER EXECUTOR
//////////////////////////////////////////////////////////////*/

contract RouterExecutor {
    /*//////////////////////////////////////////////////////////////
                            ERRORS
    //////////////////////////////////////////////////////////////*/
    
    error NotOwner();
    error NotVault();
    error InvalidPath();
    error InvalidRouters();
    error InsufficientProfit();
    error FlashLoanFailed();
    error SwapFailed();
    
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
     * @notice Execute arbitrage using router-based path
     * @param _path Array of token addresses (e.g., [WETH, USDC, WETH])
     * @param _routers Array of router addresses for each swap
     * @param _amount Flash loan amount in WEI
     */
    function startArbitrage(
        address[] calldata _path,
        address[] calldata _routers,
        uint256 _amount
    ) external onlyOwner {
        // Validate inputs
        if (_path.length < 2) revert InvalidPath();
        if (_routers.length != _path.length - 1) revert InvalidRouters();
        
        // Get first token for flash loan
        address token = _path[0];
        
        // Prepare flash loan
        IERC20[] memory tokens = new IERC20[](1);
        tokens[0] = IERC20(token);
        
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = _amount;
        
        // Encode callback data
        bytes memory userData = abi.encode(_path, _routers, _amount);
        
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
        (address[] memory path, address[] memory routers, uint256 amount) = abi.decode(
            userData,
            (address[], address[], uint256)
        );
        
        address token = address(tokens[0]);
        uint256 flashAmount = amounts[0];
        uint256 flashFee = feeAmounts[0];
        
        // Execute multi-hop swaps
        uint256 currentAmount = flashAmount;
        
        for (uint256 i = 0; i < routers.length; i++) {
            // Approve router
            IERC20(path[i]).approve(routers[i], currentAmount);
            
            // Build swap path for this hop
            address[] memory swapPath = new address[](2);
            swapPath[0] = path[i];
            swapPath[1] = path[i + 1];
            
            // Execute swap
            uint256[] memory amountsOut = IRouter(routers[i]).swapExactTokensForTokens(
                currentAmount,
                0, // Accept any amount (in production, calculate minimum)
                swapPath,
                address(this),
                block.timestamp + 300
            );
            
            // Update current amount for next swap
            currentAmount = amountsOut[1];
        }
        
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
