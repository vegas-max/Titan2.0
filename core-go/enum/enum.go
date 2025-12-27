package enum

import (
	"context"
	"fmt"
	
	"github.com/ethereum/go-ethereum/ethclient"
)

// ChainID represents supported blockchain networks
type ChainID uint64

const (
	Ethereum ChainID = 1
	Polygon  ChainID = 137
	Arbitrum ChainID = 42161
	Optimism ChainID = 10
	Base     ChainID = 8453
	BSC      ChainID = 56
	Avalanche ChainID = 43114
	Fantom   ChainID = 250
	Linea    ChainID = 59144
	Scroll   ChainID = 534352
	Mantle   ChainID = 5000
	ZkSync   ChainID = 324
	Celo     ChainID = 42220
	OpBNB    ChainID = 204
)

// Name returns the chain name
func (c ChainID) Name() string {
	switch c {
	case Ethereum:
		return "ethereum"
	case Polygon:
		return "polygon"
	case Arbitrum:
		return "arbitrum"
	case Optimism:
		return "optimism"
	case Base:
		return "base"
	case BSC:
		return "bsc"
	case Avalanche:
		return "avalanche"
	case Fantom:
		return "fantom"
	case Linea:
		return "linea"
	case Scroll:
		return "scroll"
	case Mantle:
		return "mantle"
	case ZkSync:
		return "zksync"
	case Celo:
		return "celo"
	case OpBNB:
		return "opbnb"
	default:
		return "unknown"
	}
}

// FromU64 converts uint64 to ChainID
func FromU64(value uint64) (ChainID, error) {
	switch value {
	case 1, 137, 42161, 10, 8453, 56, 43114, 250, 59144, 534352, 5000, 324, 42220, 204:
		return ChainID(value), nil
	default:
		return 0, fmt.Errorf("unsupported chain ID: %d", value)
	}
}

// AllChains returns all supported chain IDs
func AllChains() []ChainID {
	return []ChainID{
		Ethereum, Polygon, Arbitrum, Optimism, Base,
		BSC, Avalanche, Fantom, Linea, Scroll,
		Mantle, ZkSync, Celo, OpBNB,
	}
}

// ProviderManager manages Web3 provider connections
type ProviderManager struct {
	providers map[uint64]*ethclient.Client
}

// NewProviderManager creates a new provider manager
func NewProviderManager() *ProviderManager {
	return &ProviderManager{
		providers: make(map[uint64]*ethclient.Client),
	}
}

// GetProvider returns a provider for the specified chain
func (pm *ProviderManager) GetProvider(chainID uint64, rpcURL string) (*ethclient.Client, error) {
	if provider, ok := pm.providers[chainID]; ok {
		return provider, nil
	}
	
	client, err := ethclient.Dial(rpcURL)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to chain %d: %w", chainID, err)
	}
	
	pm.providers[chainID] = client
	return client, nil
}

// TestConnection tests connection to a specific chain
func (pm *ProviderManager) TestConnection(ctx context.Context, chainID uint64, rpcURL string) (bool, error) {
	provider, err := pm.GetProvider(chainID, rpcURL)
	if err != nil {
		return false, err
	}
	
	blockNumber, err := provider.BlockNumber(ctx)
	if err != nil {
		fmt.Printf("❌ Chain %d: Connection failed | Error: %v\n", chainID, err)
		return false, err
	}
	
	fmt.Printf("✅ Chain %d: Connected | Block: %d\n", chainID, blockNumber)
	return true, nil
}

// GetAllProviders returns all active providers
func (pm *ProviderManager) GetAllProviders() map[uint64]*ethclient.Client {
	return pm.providers
}

// CloseAll closes all provider connections
func (pm *ProviderManager) CloseAll() {
	for _, provider := range pm.providers {
		provider.Close()
	}
	pm.providers = make(map[uint64]*ethclient.Client)
}
