package commander

import (
	"log"
	"math/big"
	
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/vegas-max/Titan2.0/core-go/config"
	"github.com/vegas-max/Titan2.0/core-go/simulation"
)

// TitanCommander handles loan optimization and risk management
type TitanCommander struct {
	chainID            uint64
	provider           *ethclient.Client
	
	// Guardrails (Real Money Limits)
	MinLoanUSD         uint64
	MaxTVLShare        float64
	SlippageTolerance  float64
}

// New creates a new TitanCommander instance
func New(chainID uint64, provider *ethclient.Client) *TitanCommander {
	return &TitanCommander{
		chainID:           chainID,
		provider:          provider,
		MinLoanUSD:        10000,  // Minimum trade size ($10k)
		MaxTVLShare:       0.20,   // Max % of pool to borrow (20%)
		SlippageTolerance: 0.995,  // 0.5% max slippage
	}
}

// OptimizeLoanSize performs binary search to find the maximum safe loan amount
// Returns: Safe amount or 0 (abort)
func (tc *TitanCommander) OptimizeLoanSize(
	tokenAddress common.Address,
	targetAmountRaw *big.Int,
	decimals uint8,
) (*big.Int, error) {
	// Get lender address (Balancer V3 Vault)
	lenderAddress := common.HexToAddress(config.BalancerV3Vault)
	
	// Check TVL (Total Value Locked)
	poolLiquidity, err := simulation.GetProviderTVL(tc.provider, tokenAddress, lenderAddress)
	if err != nil || poolLiquidity.Cmp(big.NewInt(0)) == 0 {
		// In PAPER mode, skip vault checks
		return tc.validatePaperModeAmount(targetAmountRaw, decimals), nil
	}
	
	// Calculate caps
	maxCap := tc.calculateMaxCap(poolLiquidity)
	requestedAmount := new(big.Int).Set(targetAmountRaw)
	
	// GUARD 1: Liquidity Check
	if requestedAmount.Cmp(maxCap) > 0 {
		log.Printf("⚠️ Liquidity Constraint: Requested %s, Cap %s. Scaling down.", 
			requestedAmount.String(), maxCap.String())
		requestedAmount = maxCap
	}
	
	// GUARD 2: Floor Check
	minFloor := tc.calculateMinFloor(decimals)
	if requestedAmount.Cmp(minFloor) < 0 {
		log.Printf("❌ Trade too small for profitability (%s < %s). Aborting.",
			requestedAmount.String(), minFloor.String())
		return big.NewInt(0), nil
	}
	
	log.Printf("✅ Loan Sizing Optimized: %s (Cap: %s)", requestedAmount.String(), maxCap.String())
	return requestedAmount, nil
}

// validatePaperModeAmount validates amount in paper mode
func (tc *TitanCommander) validatePaperModeAmount(requestedAmount *big.Int, decimals uint8) *big.Int {
	minFloor := tc.calculateMinFloor(decimals)
	
	if requestedAmount.Cmp(minFloor) < 0 {
		log.Printf("Trade too small (%s < %s)", requestedAmount.String(), minFloor.String())
		return big.NewInt(0)
	}
	
	log.Printf("✅ PAPER MODE: Using requested amount %s", requestedAmount.String())
	return new(big.Int).Set(requestedAmount)
}

// calculateMaxCap calculates maximum cap based on TVL
func (tc *TitanCommander) calculateMaxCap(poolLiquidity *big.Int) *big.Int {
	// max_cap = pool_liquidity * MAX_TVL_SHARE
	multiplier := int64(tc.MaxTVLShare * 1000000)
	maxCap := new(big.Int).Mul(poolLiquidity, big.NewInt(multiplier))
	maxCap.Div(maxCap, big.NewInt(1000000))
	return maxCap
}

// calculateMinFloor calculates minimum floor based on decimals
func (tc *TitanCommander) calculateMinFloor(decimals uint8) *big.Int {
	// 500 units of stablecoin/ETH
	minFloor := big.NewInt(500)
	exp := new(big.Int).Exp(big.NewInt(10), big.NewInt(int64(decimals)), nil)
	minFloor.Mul(minFloor, exp)
	return minFloor
}

// ChainID returns the chain ID
func (tc *TitanCommander) ChainID() uint64 {
	return tc.chainID
}
