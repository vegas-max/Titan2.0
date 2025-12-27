package config

import (
	"testing"
)

func TestLoadFromEnv(t *testing.T) {
	config, err := LoadFromEnv()
	if err != nil {
		t.Fatalf("Failed to load config: %v", err)
	}

	if len(config.Chains) < 5 {
		t.Errorf("Expected at least 5 chains, got %d", len(config.Chains))
	}

	if config.Chains[1].Name != "ethereum" {
		t.Errorf("Expected ethereum for chain 1, got %s", config.Chains[1].Name)
	}

	if config.Chains[137].Name != "polygon" {
		t.Errorf("Expected polygon for chain 137, got %s", config.Chains[137].Name)
	}
}

func TestGetChain(t *testing.T) {
	config, _ := LoadFromEnv()

	chain, ok := config.GetChain(1)
	if !ok {
		t.Error("Expected to find chain 1")
	}

	if chain.Name != "ethereum" {
		t.Errorf("Expected ethereum, got %s", chain.Name)
	}

	_, ok = config.GetChain(999999)
	if ok {
		t.Error("Expected not to find chain 999999")
	}
}

func TestIsChainSupported(t *testing.T) {
	config, _ := LoadFromEnv()

	if !config.IsChainSupported(1) {
		t.Error("Expected chain 1 to be supported")
	}

	if !config.IsChainSupported(137) {
		t.Error("Expected chain 137 to be supported")
	}

	if config.IsChainSupported(999999) {
		t.Error("Expected chain 999999 to not be supported")
	}
}

func TestBalancerV3Vault(t *testing.T) {
	if BalancerV3Vault != "0xbA1333333333a1BA1108E8412f11850A5C319bA9" {
		t.Errorf("Expected correct Balancer V3 Vault address, got %s", BalancerV3Vault)
	}
}
