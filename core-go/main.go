// Package titancore provides the core functionality for the Titan arbitrage system
// This is the main entry point for the Go implementation
package main

import (
	"context"
	"fmt"
	"log"
	
	"github.com/joho/godotenv"
	"github.com/vegas-max/Titan2.0/core-go/config"
	"github.com/vegas-max/Titan2.0/core-go/enum"
	"github.com/vegas-max/Titan2.0/core-go/commander"
)

const version = "0.1.0"

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using system environment variables")
	}
	
	fmt.Printf("🚀 Titan Core (Go) v%s\n", version)
	fmt.Println("=" + string(make([]byte, 50)) + "=")
	
	// Load configuration
	cfg, err := config.LoadFromEnv()
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}
	
	fmt.Printf("✅ Configuration loaded: %d chains configured\n", len(cfg.Chains))
	fmt.Printf("✅ Balancer V3 Vault: %s\n", config.BalancerV3Vault)
	
	// Test chain connections
	fmt.Println("\n🔌 Testing Chain Connections...")
	testChainConnections(cfg)
	
	// Example: Initialize commander for Polygon
	if chainCfg, ok := cfg.GetChain(uint64(enum.Polygon)); ok && chainCfg.RPC != "" {
		fmt.Println("\n💼 Initializing Titan Commander for Polygon...")
		
		pm := enum.NewProviderManager()
		provider, err := pm.GetProvider(uint64(enum.Polygon), chainCfg.RPC)
		if err != nil {
			log.Printf("Failed to connect to Polygon: %v", err)
		} else {
			cmd := commander.New(uint64(enum.Polygon), provider)
			fmt.Printf("✅ Commander initialized for chain %d\n", cmd.ChainID())
			fmt.Printf("   Min Loan USD: $%d\n", cmd.MinLoanUSD)
			fmt.Printf("   Max TVL Share: %.1f%%\n", cmd.MaxTVLShare*100)
			fmt.Printf("   Slippage Tolerance: %.2f%%\n", (1-cmd.SlippageTolerance)*100)
		}
	}
	
	fmt.Println("\n✨ Titan Core (Go) initialization complete!")
}

func testChainConnections(cfg *config.Config) {
	pm := enum.NewProviderManager()
	ctx := context.Background()
	
	tested := 0
	successful := 0
	
	// Test first 5 chains
	for _, chain := range enum.AllChains()[:5] {
		chainID := uint64(chain)
		chainCfg, ok := cfg.GetChain(chainID)
		if !ok || chainCfg.RPC == "" {
			continue
		}
		
		tested++
		success, _ := pm.TestConnection(ctx, chainID, chainCfg.RPC)
		if success {
			successful++
		}
	}
	
	fmt.Printf("Connection Test Results: %d/%d successful\n", successful, tested)
}
