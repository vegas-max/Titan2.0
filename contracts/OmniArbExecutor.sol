// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

OmniArbExecutor.sol (Refactored with Custom Enum Logic)

- Reuses system-wide SwapHandler module for all swap operations
- Supports Aave V3 flashLoanSimple + Balancer V3 unlock transient debt
- Adds CUSTOM ENUM LOGIC for:
  * DEX registry (per-chain routers)
  * CHAIN identity (block.chainid -> Chain enum)
  * TOKEN registry with WRAPPED + BRIDGED variants
  * Optional registry-encoded routes (cleaner encoding)
*/

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./modules/SwapHandler.sol";
import "./interfaces/IB3.sol";
import "./interfaces/IAaveV3.sol";

/* ============================== CUSTOM ENUMS ============================== */

/**
 * @dev Chain identifiers mapped from block.chainid
 */
enum Chain {
    ETHEREUM,      // 1
    POLYGON,       // 137
    ARBITRUM,      // 42161
    OPTIMISM,      // 10
    BASE,          // 8453
    BSC,           // 56
    AVALANCHE,     // 43114
    FANTOM,        // 250
    LINEA,         // 59144
    SCROLL,        // 534352
    MANTLE,        // 5000
    ZKSYNC,        // 324
    BLAST,         // 81457
    CELO,          // 42220
    OPBNB          // 204
}

/**
 * @dev DEX identifiers (per-chain router registry)
 */
enum DEX {
    UNISWAP_V2,
    UNISWAP_V3,
    SUSHISWAP,
    QUICKSWAP,
    PANCAKESWAP,
    CURVE,
    BALANCER,
    TRADER_JOE,
    SPOOKYSWAP,
    AERODROME,
    VELODROME
}

/**
 * @dev Token identifiers with WRAPPED + BRIDGED variants
 * Format: TOKEN_VARIANT_CHAIN (where applicable)
 */
enum Token {
    // Native wrapped
    WETH,          // Wrapped ETH on Ethereum
    WMATIC,        // Wrapped MATIC on Polygon
    WBNB,          // Wrapped BNB on BSC
    WAVAX,         // Wrapped AVAX on Avalanche
    WFTM,          // Wrapped FTM on Fantom
    
    // Stablecoins (native)
    USDC,          // Native USDC on origin chains
    USDT,          // Native USDT on origin chains
    DAI,           // Native DAI on origin chains
    FRAX,          // Native FRAX
    
    // Bridged stablecoins on Polygon
    USDC_BRIDGED_POLYGON,
    USDT_BRIDGED_POLYGON,
    DAI_BRIDGED_POLYGON,
    
    // Bridged stablecoins on Arbitrum
    USDC_BRIDGED_ARBITRUM,
    USDT_BRIDGED_ARBITRUM,
    DAI_BRIDGED_ARBITRUM,
    
    // Bridged stablecoins on Optimism
    USDC_BRIDGED_OPTIMISM,
    USDT_BRIDGED_OPTIMISM,
    DAI_BRIDGED_OPTIMISM,
    
    // Bridged stablecoins on Base
    USDC_BRIDGED_BASE,
    
    // Bridged ETH variants
    WETH_BRIDGED_POLYGON,
    WETH_BRIDGED_ARBITRUM,
    WETH_BRIDGED_OPTIMISM,
    WETH_BRIDGED_BASE,
    WETH_BRIDGED_AVALANCHE,
    
    // Bridged BTC variants
    WBTC,
    WBTC_BRIDGED_POLYGON,
    WBTC_BRIDGED_ARBITRUM,
    
    // Other major tokens
    LINK,
    AAVE,
    CRV,
    BAL,
    SUSHI
}

/* ============================== MAIN CONTRACT ============================== */

/**
 * @title OmniArbExecutor
 * @notice Multi-chain arbitrage executor with flash loan support
 * @dev Reuses SwapHandler module (system-wide component) for all swaps
 */
contract OmniArbExecutor is Ownable, ReentrancyGuard, SwapHandler, IFlashLoanSimpleReceiver {
    using SafeERC20 for IERC20;

    /* ========== STATE VARIABLES ========== */
    
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/IAaveV3.sol";
import "./interfaces/IB3.sol";
import "./interfaces/IUniV2.sol";
import "./interfaces/IUniV3.sol";
import "./interfaces/ICurve.sol";
import "./modules/SwapHandler.sol";

/**
 * @title OmniArbExecutor
 * @notice Refactored core executor for flashloan-based arbitrage with multi-DEX routing
 * @dev Supports Aave V3 and Balancer V3 flashloans with RAW_ADDRESSES and REGISTRY_ENUMS encoding
 */
contract OmniArbExecutor is Ownable, SwapHandler, IAaveFlashLoanSimpleReceiver {
    using SafeERC20 for IERC20;

    // ============================================
    // ENUMS
    // ============================================

    /**
     * @notice Route encoding format
     */
    enum RouteEncoding {
        RAW_ADDRESSES,    // 0: Explicit router + token addresses
        REGISTRY_ENUMS    // 1: DEX + Token enums resolved on-chain
    }

    /**
     * @notice DEX identifiers for registry-based routing
     */
    enum Dex {
        QUICKSWAP,    // 0
        UNIV3,        // 1
        CURVE,        // 2
        SUSHISWAP,    // 3
        BALANCER,     // 4
        PANCAKESWAP,  // 5
        TRADER_JOE    // 6
    }

    /**
     * @notice Token identifiers for registry-based routing
     */
    enum TokenId {
        USDC,         // 0
        USDT,         // 1
        DAI,          // 2
        WETH,         // 3
        WMATIC,       // 4
        WBTC,         // 5
        FRAX          // 6
    }

    /**
     * @notice Token type classification
     */
    enum TokenType {
        CANONICAL,    // 0: Native to the chain
        BRIDGED,      // 1: Bridged version (e.g., USDC.e)
        WRAPPED       // 2: Wrapped native (WETH, WMATIC, etc.)
    }

    // ============================================
    // STATE VARIABLES
    // ============================================

    IVaultV3 public immutable BALANCER_VAULT;
    IAavePoolV3 public immutable AAVE_POOL;
    
    uint256 public swapDeadline = 180; // Default 3 minutes

    // Registry mappings for REGISTRY_ENUMS encoding
    // Note: chainId uses actual chain IDs (e.g., 137 for Polygon, 1 for Ethereum)
    // not Chain enum ordinal values. The Chain enum is for reference only.
    // dexRouter[chainId][dexId] = router address (or pool address for Curve)
    mapping(uint256 => mapping(uint8 => address)) public dexRouter;
    
    // tokenRegistry[chainId][tokenId][tokenType] = token address
    mapping(uint256 => mapping(uint8 => mapping(uint8 => address))) public tokenRegistry;

    // ============================================
    // EVENTS
    // ============================================

    event RouteExecuted(
        address indexed loanToken,
        uint256 loanAmount,
        uint256 finalAmount,
        uint256 profit
    );

    event DexRouterSet(uint256 indexed chainId, uint8 indexed dexId, address router);
    event TokenSet(uint256 indexed chainId, uint8 indexed tokenId, uint8 indexed tokenType, address token);

    // ============================================
    // CONSTRUCTOR
    // ============================================

    constructor(address _balancer, address _aave) Ownable(msg.sender) {
        require(_balancer != address(0) && _aave != address(0), "Invalid addresses");
        BALANCER_VAULT = IVaultV3(_balancer);
        AAVE_POOL = IAavePoolV3(_aave);
    }

    // ============================================
    // CONFIGURATION
    // ============================================

    /**
     * @notice Set swap deadline for time-sensitive swaps
     */
    function setSwapDeadline(uint256 _seconds) external onlyOwner {
        require(_seconds >= 60 && _seconds <= 600, "Deadline must be 60-600 seconds");
        swapDeadline = _seconds;
        _swapDeadline = _seconds;  // Update SwapHandler's internal deadline
    }
    
    /**
     * @notice Register a token address for a specific chain
     */
    function registerToken(
        Chain _chain,
        Token _token,
        address _address
    ) external onlyOwner {
        require(_address != address(0), "Invalid address");
        tokenRegistry[_chain][_token] = _address;
        emit RegistryUpdated("token", uint256(_chain), uint256(_token), _address);
    }
    
    /**
     * @notice Register a DEX router address for a specific chain
     */
    function registerDEX(
        Chain _chain,
        DEX _dex,
        address _router
    ) external onlyOwner {
        require(_router != address(0), "Invalid router");
        dexRegistry[_chain][_dex] = _router;
        emit RegistryUpdated("dex", uint256(_chain), uint256(_dex), _router);
    }
    
    /**
     * @notice Batch register multiple tokens
     */
    function batchRegisterTokens(
        Chain _chain,
        Token[] calldata _tokens,
        address[] calldata _addresses
    ) external onlyOwner {
        require(_tokens.length == _addresses.length, "Length mismatch");
        for (uint256 i = 0; i < _tokens.length; i++) {
            require(_addresses[i] != address(0), "Invalid address");
            tokenRegistry[_chain][_tokens[i]] = _addresses[i];
            emit RegistryUpdated("token", uint256(_chain), uint256(_tokens[i]), _addresses[i]);
        }
    }
    
    /**
     * @notice Batch register multiple DEX routers
     */
    function batchRegisterDEXs(
        Chain _chain,
        DEX[] calldata _dexs,
        address[] calldata _routers
    ) external onlyOwner {
        require(_dexs.length == _routers.length, "Length mismatch");
        for (uint256 i = 0; i < _dexs.length; i++) {
            require(_routers[i] != address(0), "Invalid router");
            dexRegistry[_chain][_dexs[i]] = _routers[i];
            emit RegistryUpdated("dex", uint256(_chain), uint256(_dexs[i]), _routers[i]);
        }
    }
    
    /* ========== HELPER FUNCTIONS ========== */
    
    /**
     * @notice Get current chain enum from block.chainid
     */
    function getCurrentChain() public view returns (Chain) {
        return chainIdToChain[block.chainid];
    }
    
    /**
     * @notice Resolve token enum to address on current chain
     */
    function resolveToken(Token _token) public view returns (address) {
        address addr = tokenRegistry[getCurrentChain()][_token];
        require(addr != address(0), "Token not registered");
        return addr;
    }
    
    /**
     * @notice Resolve DEX enum to router address on current chain
     */
    function resolveDEX(DEX _dex) public view returns (address) {
        address router = dexRegistry[getCurrentChain()][_dex];
        require(router != address(0), "DEX not registered");
        return router;
    }

    /**
     * @notice Register a DEX router for a specific chain
     */
    function setDexRouter(uint256 chainId, uint8 dexId, address router) external onlyOwner {
        require(router != address(0), "Invalid router");
        dexRouter[chainId][dexId] = router;
        emit DexRouterSet(chainId, dexId, router);
    }

    /**
     * @notice Register a token for a specific chain, token ID, and token type
     */
    function setToken(uint256 chainId, uint8 tokenId, uint8 tokenType, address token) external onlyOwner {
        require(token != address(0), "Invalid token");
        tokenRegistry[chainId][tokenId][tokenType] = token;
        emit TokenSet(chainId, tokenId, tokenType, token);
    }

    /**
     * @notice Batch register multiple DEX routers
     */
    function batchSetDexRouters(
        uint256[] calldata chainIds,
        uint8[] calldata dexIds,
        address[] calldata routers
    ) external onlyOwner {
        require(chainIds.length == dexIds.length && dexIds.length == routers.length, "Length mismatch");
        for (uint i = 0; i < chainIds.length; i++) {
            require(routers[i] != address(0), "Invalid router");
            dexRouter[chainIds[i]][dexIds[i]] = routers[i];
            emit DexRouterSet(chainIds[i], dexIds[i], routers[i]);
        }
    }

    /**
     * @notice Batch register multiple tokens
     */
    function batchSetTokens(
        uint256[] calldata chainIds,
        uint8[] calldata tokenIds,
        uint8[] calldata tokenTypes,
        address[] calldata tokens
    ) external onlyOwner {
        require(
            chainIds.length == tokenIds.length && 
            tokenIds.length == tokenTypes.length && 
            tokenTypes.length == tokens.length,
            "Length mismatch"
        );
        for (uint i = 0; i < chainIds.length; i++) {
            require(tokens[i] != address(0), "Invalid token");
            tokenRegistry[chainIds[i]][tokenIds[i]][tokenTypes[i]] = tokens[i];
            emit TokenSet(chainIds[i], tokenIds[i], tokenTypes[i], tokens[i]);
        }
    }

    // ============================================
    // EXECUTION TRIGGER
    // ============================================

    /**
     * @notice Execute arbitrage with flashloan
     * @param flashSource 1=Balancer V3, 2=Aave V3
     * @param loanToken Token to borrow
     * @param loanAmount Amount to borrow
     * @param routeData Encoded route (RAW_ADDRESSES or REGISTRY_ENUMS)
     */
    function execute(
        uint8 flashSource,
        address loanToken,
        uint256 loanAmount,
        bytes calldata routeData
    ) external onlyOwner {
        if (flashSource == 1) {
            // Balancer V3: Unlock pattern
            bytes memory callbackData = abi.encode(loanToken, loanAmount, routeData);
            BALANCER_VAULT.unlock(abi.encodeWithSelector(this.onBalancerUnlock.selector, callbackData));
        } else if (flashSource == 2) {
            // Aave V3: Standard flashloan
            AAVE_POOL.flashLoanSimple(address(this), loanToken, loanAmount, routeData, 0);
        } else {
            revert("Invalid flash source");
        }
    }

    // ============================================
    // FLASHLOAN CALLBACKS
    // ============================================

    /**
     * @notice Balancer V3 unlock callback
     */
    function onBalancerUnlock(bytes calldata data) external returns (bytes memory) {
        require(msg.sender == address(BALANCER_VAULT), "Unauthorized");
        
        (address token, uint256 amount, bytes memory routeData) = abi.decode(
            data,
            (address, uint256, bytes)
        );

        // Take debt (V3 transient accounting)
        BALANCER_VAULT.sendTo(IERC20(token), address(this), amount);

        // Execute route
        uint256 finalAmount = _runRoute(token, amount, routeData);

        // Ensure route was at least break-even before repaying Balancer
        require(finalAmount >= amount, "Insufficient return");

        // Repay debt
        IERC20(token).safeTransfer(address(BALANCER_VAULT), amount);
        BALANCER_VAULT.settle(IERC20(token), amount);

        emit RouteExecuted(token, amount, finalAmount, finalAmount - amount);
        
        // Emit profit event
        if (finalAmount > amount) {
            emit ArbitrageExecuted(1, token, amount, finalAmount - amount);
        }
        
        return "";
    }

    /**
     * @notice Aave V3 flashloan callback
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address /* initiator */,
        bytes calldata routeData
    ) external override returns (bool) {
        require(msg.sender == address(AAVE_POOL), "Auth");
        
        uint256 finalAmount = _runRoute(asset, amount, routeData);

        // Approve repayment (loan + premium)
        uint256 owed = amount + premium;
        require(finalAmount >= owed, "Insufficient return");
        
        IERC20(asset).safeApprove(address(AAVE_POOL), owed);

        emit RouteExecuted(asset, amount, finalAmount, finalAmount - owed);
        
        return true;
    }

    // ============================================
    // ROUTE EXECUTION ENGINE
    // ============================================

    /**
     * @notice Execute multi-hop swap route
     * @param inputToken Starting token (loan token)
     * @param inputAmount Starting amount (loan amount)
     * @param routeData Encoded route data
     * @return finalAmount Final amount after all hops
     */
    function _runRoute(
        address inputToken,
        uint256 inputAmount,
        bytes memory routeData
    ) internal returns (uint256 finalAmount) {
        
        // Decode encoding type using ABI decoding (first tuple element)
        RouteEncoding encoding = abi.decode(routeData, (RouteEncoding));

        if (encoding == RouteEncoding.RAW_ADDRESSES) {
            return _runRouteRaw(inputToken, inputAmount, routeData);
        } else if (encoding == RouteEncoding.REGISTRY_ENUMS) {
            return _runRouteRegistry(inputToken, inputAmount, routeData);
        } else {
            revert("Invalid encoding");
        }
    }

    /**
     * @notice Execute route with RAW_ADDRESSES encoding
     */
    function _runRouteRaw(
        address inputToken,
        uint256 inputAmount,
        bytes memory routeData
    ) internal returns (uint256) {
        
        (
            RouteEncoding /* enc */,
            uint8[] memory protocols,
            address[] memory routersOrPools,
            address[] memory tokenOutPath,
            bytes[] memory extra
        ) = abi.decode(routeData, (RouteEncoding, uint8[], address[], address[], bytes[]));

        // Validate lengths
        require(protocols.length == routersOrPools.length, "len mismatch");
        require(protocols.length == tokenOutPath.length, "len mismatch");
        require(protocols.length == extra.length, "len mismatch");
        require(protocols.length > 0 && protocols.length <= 5, "Invalid route length");

        uint256 currentAmount = inputAmount;
        address currentToken = inputToken;

        for (uint i = 0; i < protocols.length; i++) {
            require(routersOrPools[i] != address(0), "Invalid router");
            require(tokenOutPath[i] != address(0), "Invalid token");
            require(currentAmount > 0, "Zero balance");

            currentAmount = _executeSwap(
                protocols[i],
                routersOrPools[i],
                currentToken,
                tokenOutPath[i],
                currentAmount,
                extra[i]
            );

            require(currentAmount > 0, "Swap returned zero");
            currentToken = tokenOutPath[i];
        }

        return currentAmount;
    }

    /**
     * @notice Execute route with REGISTRY_ENUMS encoding
     */
    function _runRouteRegistry(
        address inputToken,
        uint256 inputAmount,
        bytes memory routeData
    ) internal returns (uint256) {
        
        (
            RouteEncoding /* enc */,
            uint8[] memory protocols,
            uint8[] memory dexIds,
            uint8[] memory tokenOutIds,
            uint8[] memory tokenOutTypes,
            bytes[] memory extra
        ) = abi.decode(routeData, (RouteEncoding, uint8[], uint8[], uint8[], uint8[], bytes[]));

        // Validate lengths
        require(protocols.length == dexIds.length, "len mismatch");
        require(protocols.length == tokenOutIds.length, "len mismatch");
        require(protocols.length == tokenOutTypes.length, "len mismatch");
        require(protocols.length == extra.length, "len mismatch");
        require(protocols.length > 0 && protocols.length <= 5, "Invalid route length");

        uint256 chainId = block.chainid;
        uint256 currentAmount = inputAmount;
        address currentToken = inputToken;

        for (uint i = 0; i < protocols.length; i++) {
            // Resolve router from registry
            address routerOrPool = dexRouter[chainId][dexIds[i]];
            require(routerOrPool != address(0), "Router not registered");

            // Resolve tokenOut from registry
            address tokenOut = tokenRegistry[chainId][tokenOutIds[i]][tokenOutTypes[i]];
            require(tokenOut != address(0), "Token not registered");

            require(currentAmount > 0, "Zero balance");

            currentAmount = _executeSwap(
                protocols[i],
                routerOrPool,
                currentToken,
                tokenOut,
                currentAmount,
                extra[i]
            );

            require(currentAmount > 0, "Swap returned zero");
            currentToken = tokenOut;
        }

        return currentAmount;
    }

    // ============================================
    // EMERGENCY FUNCTIONS
    // ============================================

    /**
     * @notice Withdraw tokens from contract (emergency)
     */
    function withdraw(address token) external onlyOwner {
        IERC20(token).safeTransfer(msg.sender, IERC20(token).balanceOf(address(this)));
    }

    /**
     * @notice Withdraw native ETH/MATIC (emergency)
     */
    function withdrawNative() external onlyOwner {
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}("");
        require(success, "Native transfer failed");
    }

    /**
     * @notice Allow the contract to receive native ETH/MATIC
     * @dev This is intended for handling native refunds or unwrapped WETH from
     *      external protocols used in arbitrage flows. Any ETH accumulated here
     *      can be recovered by the owner via {withdrawNative}.
     */
    receive() external payable {}
}
