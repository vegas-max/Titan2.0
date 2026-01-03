package config

import (
	"os"
	"strconv"
	"strings"
)

// BalancerV3Vault is the deterministic Balancer V3 Vault address across all chains
const BalancerV3Vault = "0xbA1333333333a1BA1108E8412f11850A5C319bA9"

// ChainConfig represents configuration for a single blockchain
type ChainConfig struct {
	Name          string
	RPC           string
	WSS           string
	AavePool      string
	UniswapRouter string
	CurveRouter   string
	Native        string
}

// DexRouters represents DEX router addresses for a chain
type DexRouters map[string]string

// BridgeConfig represents configuration for a bridge protocol
type BridgeConfig struct {
	Name               string
	TypicalTimeSeconds uint32
	MaxTimeSeconds     uint32
	FeeRangeBps        []uint32
	Description        string
}

// AIConfig holds AI and scoring configuration
type AIConfig struct {
	TARScoringEnabled          bool
	AIPredictionEnabled        bool
	AIPredictionMinConfidence  float64
	CatBoostModelEnabled       bool
	HFConfidenceThreshold      float64
	MLConfidenceThreshold      float64
	PumpProbabilityThreshold   float64
	SelfLearningEnabled        bool
	RouteIntelligenceEnabled   bool
	RealTimeDataEnabled        bool
}

// Config holds all configuration for the Titan system
type Config struct {
	Chains               map[uint64]*ChainConfig
	DexRouters           map[uint64]DexRouters
	IntentBasedBridges   map[string]*BridgeConfig
	LifiSupportedChains  []uint64
	AI                   *AIConfig
}

// LoadFromEnv loads configuration from environment variables
func LoadFromEnv() (*Config, error) {
	config := &Config{
		Chains:              loadChains(),
		DexRouters:          loadDexRouters(),
		IntentBasedBridges:  loadBridges(),
		LifiSupportedChains: []uint64{1, 137, 42161, 10, 8453, 56, 43114, 250, 59144, 534352, 5000, 324, 81457, 42220, 204},
		AI:                  loadAIConfig(),
	}
	
	return config, nil
}

func loadChains() map[uint64]*ChainConfig {
	chains := make(map[uint64]*ChainConfig)
	
	// Ethereum Mainnet
	chains[1] = &ChainConfig{
		Name:          "ethereum",
		RPC:           getEnv("RPC_ETHEREUM", ""),
		WSS:           getEnv("WSS_ETHEREUM", ""),
		AavePool:      "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
		UniswapRouter: "0xE592427A0AEce92De3Edee1F18E0157C05861564",
		CurveRouter:   "0x99a58482BD75cbab83b27EC03CA68fF489b5788f",
		Native:        "ETH",
	}
	
	// Polygon
	chains[137] = &ChainConfig{
		Name:          "polygon",
		RPC:           getEnv("RPC_POLYGON", ""),
		WSS:           getEnv("WSS_POLYGON", ""),
		AavePool:      "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
		UniswapRouter: "0xE592427A0AEce92De3Edee1F18E0157C05861564",
		CurveRouter:   "0x445FE580eF8d70FF569aB36e80c647af338db351",
		Native:        "MATIC",
	}
	
	// Arbitrum
	chains[42161] = &ChainConfig{
		Name:          "arbitrum",
		RPC:           getEnv("RPC_ARBITRUM", ""),
		WSS:           getEnv("WSS_ARBITRUM", ""),
		AavePool:      "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
		UniswapRouter: "0xE592427A0AEce92De3Edee1F18E0157C05861564",
		CurveRouter:   "0x0000000000000000000000000000000000000000",
		Native:        "ETH",
	}
	
	// Optimism
	chains[10] = &ChainConfig{
		Name:          "optimism",
		RPC:           getEnv("RPC_OPTIMISM", ""),
		WSS:           getEnv("WSS_OPTIMISM", ""),
		AavePool:      "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
		UniswapRouter: "0xE592427A0AEce92De3Edee1F18E0157C05861564",
		CurveRouter:   "0x0000000000000000000000000000000000000000",
		Native:        "ETH",
	}
	
	// Base
	chains[8453] = &ChainConfig{
		Name:          "base",
		RPC:           getEnv("RPC_BASE", ""),
		WSS:           getEnv("WSS_BASE", ""),
		AavePool:      "0x0000000000000000000000000000000000000000",
		UniswapRouter: "0x2626664c2603336E57B271c5C0b26F421741e481",
		CurveRouter:   "0x0000000000000000000000000000000000000000",
		Native:        "ETH",
	}
	
	return chains
}

func loadDexRouters() map[uint64]DexRouters {
	dexRouters := make(map[uint64]DexRouters)
	
	// Ethereum DEX routers
	dexRouters[1] = DexRouters{
		"UNIV2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
		"SUSHI": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
	}
	
	// Polygon DEX routers
	dexRouters[137] = DexRouters{
		"QUICKSWAP": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
		"SUSHI":     "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
		"APE":       "0xC0788A3aD43d79aa53B09c2EaCc313A787d1d607",
	}
	
	// Arbitrum DEX routers
	dexRouters[42161] = DexRouters{
		"CAMELOT": "0xc873fEcbd354f5A56E00E710B90EF4201db2448d",
		"SUSHI":   "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
	}
	
	return dexRouters
}

func loadBridges() map[string]*BridgeConfig {
	bridges := make(map[string]*BridgeConfig)
	
	bridges["across"] = &BridgeConfig{
		Name:               "Across Protocol",
		TypicalTimeSeconds: 30,
		MaxTimeSeconds:     180,
		FeeRangeBps:        []uint32{5, 30},
		Description:        "Fastest intent-based bridge using solver network",
	}
	
	bridges["stargate"] = &BridgeConfig{
		Name:               "Stargate Finance",
		TypicalTimeSeconds: 60,
		MaxTimeSeconds:     300,
		FeeRangeBps:        []uint32{6, 50},
		Description:        "Fast and reliable LayerZero-based bridge",
	}
	
	bridges["hop"] = &BridgeConfig{
		Name:               "Hop Protocol",
		TypicalTimeSeconds: 120,
		MaxTimeSeconds:     600,
		FeeRangeBps:        []uint32{10, 100},
		Description:        "Popular bridge with good liquidity",
	}
	
	return bridges
}

// GetChain returns configuration for a specific chain
func (c *Config) GetChain(chainID uint64) (*ChainConfig, bool) {
	chain, ok := c.Chains[chainID]
	return chain, ok
}

// IsChainSupported checks if a chain is supported
func (c *Config) IsChainSupported(chainID uint64) bool {
	_, ok := c.Chains[chainID]
	return ok
}

// getEnv retrieves an environment variable with a default value
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return strings.TrimSpace(value)
}

// getBoolEnv retrieves a boolean environment variable with a default value
func getBoolEnv(key string, defaultValue bool) bool {
	value := strings.ToLower(getEnv(key, ""))
	if value == "" {
		return defaultValue
	}
	return value == "true" || value == "1" || value == "yes"
}

// getFloatEnv retrieves a float environment variable with a default value
func getFloatEnv(key string, defaultValue float64) float64 {
	value := getEnv(key, "")
	if value == "" {
		return defaultValue
	}
	f, err := strconv.ParseFloat(value, 64)
	if err != nil {
		return defaultValue
	}
	return f
}

// loadAIConfig loads AI and scoring configuration from environment
func loadAIConfig() *AIConfig {
	return &AIConfig{
		TARScoringEnabled:         getBoolEnv("TAR_SCORING_ENABLED", true),
		AIPredictionEnabled:       getBoolEnv("AI_PREDICTION_ENABLED", true),
		AIPredictionMinConfidence: getFloatEnv("AI_PREDICTION_MIN_CONFIDENCE", 0.8),
		CatBoostModelEnabled:      getBoolEnv("CATBOOST_MODEL_ENABLED", true),
		HFConfidenceThreshold:     getFloatEnv("HF_CONFIDENCE_THRESHOLD", 0.8),
		MLConfidenceThreshold:     getFloatEnv("ML_CONFIDENCE_THRESHOLD", 0.75),
		PumpProbabilityThreshold:  getFloatEnv("PUMP_PROBABILITY_THRESHOLD", 0.2),
		SelfLearningEnabled:       getBoolEnv("SELF_LEARNING_ENABLED", true),
		RouteIntelligenceEnabled:  getBoolEnv("ROUTE_INTELLIGENCE_ENABLED", true),
		RealTimeDataEnabled:       getBoolEnv("REAL_TIME_DATA_ENABLED", true),
	}
}
