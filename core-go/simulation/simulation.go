package simulation

import (
	"context"
	"log"
	"math/big"
	"strings"
	
	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"
)

// ERC20 ABI for balanceOf
const erc20ABI = `[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]`

// TitanSimulationEngine validates liquidity and simulates trades
type TitanSimulationEngine struct {
	chainID  uint64
	provider *ethclient.Client
}

// New creates a new simulation engine
func New(chainID uint64, provider *ethclient.Client) *TitanSimulationEngine {
	return &TitanSimulationEngine{
		chainID:  chainID,
		provider: provider,
	}
}

// GetLenderTVL checks how deep the lender's pockets are
// Returns: Total Available Liquidity (raw units)
func (tse *TitanSimulationEngine) GetLenderTVL(
	ctx context.Context,
	tokenAddress common.Address,
	lenderAddress common.Address,
) (*big.Int, error) {
	return GetProviderTVL(tse.provider, tokenAddress, lenderAddress)
}

// IsConnected checks if provider is connected
func (tse *TitanSimulationEngine) IsConnected(ctx context.Context) bool {
	_, err := tse.provider.BlockNumber(ctx)
	return err == nil
}

// GetBlockNumber returns the current block number
func (tse *TitanSimulationEngine) GetBlockNumber(ctx context.Context) (uint64, error) {
	return tse.provider.BlockNumber(ctx)
}

// GetProviderTVL is a standalone function for checking provider liquidity
func GetProviderTVL(
	provider *ethclient.Client,
	tokenAddress common.Address,
	lenderAddress common.Address,
) (*big.Int, error) {
	// Parse the ABI
	parsedABI, err := abi.JSON(strings.NewReader(erc20ABI))
	if err != nil {
		log.Printf("Failed to parse ABI: %v", err)
		return big.NewInt(0), nil
	}

	// Pack the balanceOf call
	data, err := parsedABI.Pack("balanceOf", lenderAddress)
	if err != nil {
		log.Printf("Failed to pack balanceOf: %v", err)
		return big.NewInt(0), nil
	}

	// Make the call
	msg := ethereum.CallMsg{
		To:   &tokenAddress,
		Data: data,
	}

	result, err := provider.CallContract(context.Background(), msg, nil)
	if err != nil {
		log.Printf("Failed to call balanceOf: %v", err)
		return big.NewInt(0), nil
	}

	// Unpack the result
	var balance *big.Int
	err = parsedABI.UnpackIntoInterface(&balance, "balanceOf", result)
	if err != nil {
		log.Printf("Failed to unpack result: %v", err)
		return big.NewInt(0), nil
	}

	if balance != nil {
		log.Printf("TVL for token %s at lender %s: %s", tokenAddress.Hex(), lenderAddress.Hex(), balance.String())
		return balance, nil
	}

	return big.NewInt(0), nil
}
