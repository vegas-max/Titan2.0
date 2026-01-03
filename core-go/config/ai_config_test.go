package config

import (
	"os"
	"testing"
)

func TestAIConfig(t *testing.T) {
	// Set environment variables for testing
	os.Setenv("TAR_SCORING_ENABLED", "true")
	os.Setenv("AI_PREDICTION_ENABLED", "true")
	os.Setenv("AI_PREDICTION_MIN_CONFIDENCE", "0.8")
	os.Setenv("CATBOOST_MODEL_ENABLED", "true")
	os.Setenv("HF_CONFIDENCE_THRESHOLD", "0.8")
	os.Setenv("ML_CONFIDENCE_THRESHOLD", "0.75")
	os.Setenv("PUMP_PROBABILITY_THRESHOLD", "0.2")
	os.Setenv("SELF_LEARNING_ENABLED", "true")
	os.Setenv("ROUTE_INTELLIGENCE_ENABLED", "true")
	os.Setenv("REAL_TIME_DATA_ENABLED", "true")
	
	// Load config
	cfg := loadAIConfig()
	
	// Test boolean values
	if !cfg.TARScoringEnabled {
		t.Error("Expected TARScoringEnabled to be true")
	}
	
	if !cfg.AIPredictionEnabled {
		t.Error("Expected AIPredictionEnabled to be true")
	}
	
	if !cfg.CatBoostModelEnabled {
		t.Error("Expected CatBoostModelEnabled to be true")
	}
	
	if !cfg.SelfLearningEnabled {
		t.Error("Expected SelfLearningEnabled to be true")
	}
	
	if !cfg.RouteIntelligenceEnabled {
		t.Error("Expected RouteIntelligenceEnabled to be true")
	}
	
	if !cfg.RealTimeDataEnabled {
		t.Error("Expected RealTimeDataEnabled to be true")
	}
	
	// Test float values
	if cfg.AIPredictionMinConfidence != 0.8 {
		t.Errorf("Expected AIPredictionMinConfidence to be 0.8, got %f", cfg.AIPredictionMinConfidence)
	}
	
	if cfg.HFConfidenceThreshold != 0.8 {
		t.Errorf("Expected HFConfidenceThreshold to be 0.8, got %f", cfg.HFConfidenceThreshold)
	}
	
	if cfg.MLConfidenceThreshold != 0.75 {
		t.Errorf("Expected MLConfidenceThreshold to be 0.75, got %f", cfg.MLConfidenceThreshold)
	}
	
	if cfg.PumpProbabilityThreshold != 0.2 {
		t.Errorf("Expected PumpProbabilityThreshold to be 0.2, got %f", cfg.PumpProbabilityThreshold)
	}
}

func TestAIConfigDefaults(t *testing.T) {
	// Clear environment variables
	os.Unsetenv("TAR_SCORING_ENABLED")
	os.Unsetenv("AI_PREDICTION_ENABLED")
	os.Unsetenv("AI_PREDICTION_MIN_CONFIDENCE")
	os.Unsetenv("CATBOOST_MODEL_ENABLED")
	os.Unsetenv("HF_CONFIDENCE_THRESHOLD")
	os.Unsetenv("ML_CONFIDENCE_THRESHOLD")
	os.Unsetenv("PUMP_PROBABILITY_THRESHOLD")
	os.Unsetenv("SELF_LEARNING_ENABLED")
	os.Unsetenv("ROUTE_INTELLIGENCE_ENABLED")
	os.Unsetenv("REAL_TIME_DATA_ENABLED")
	
	// Load config with defaults
	cfg := loadAIConfig()
	
	// Test default values
	if !cfg.TARScoringEnabled {
		t.Error("Expected default TARScoringEnabled to be true")
	}
	
	if !cfg.AIPredictionEnabled {
		t.Error("Expected default AIPredictionEnabled to be true")
	}
	
	if cfg.AIPredictionMinConfidence != 0.8 {
		t.Errorf("Expected default AIPredictionMinConfidence to be 0.8, got %f", cfg.AIPredictionMinConfidence)
	}
	
	if !cfg.CatBoostModelEnabled {
		t.Error("Expected default CatBoostModelEnabled to be true")
	}
	
	if cfg.HFConfidenceThreshold != 0.8 {
		t.Errorf("Expected default HFConfidenceThreshold to be 0.8, got %f", cfg.HFConfidenceThreshold)
	}
	
	if cfg.MLConfidenceThreshold != 0.75 {
		t.Errorf("Expected default MLConfidenceThreshold to be 0.75, got %f", cfg.MLConfidenceThreshold)
	}
	
	if cfg.PumpProbabilityThreshold != 0.2 {
		t.Errorf("Expected default PumpProbabilityThreshold to be 0.2, got %f", cfg.PumpProbabilityThreshold)
	}
	
	if !cfg.SelfLearningEnabled {
		t.Error("Expected default SelfLearningEnabled to be true")
	}
	
	if !cfg.RouteIntelligenceEnabled {
		t.Error("Expected default RouteIntelligenceEnabled to be true")
	}
	
	if !cfg.RealTimeDataEnabled {
		t.Error("Expected default RealTimeDataEnabled to be true")
	}
}

func TestLoadConfigWithAI(t *testing.T) {
	// Set AI environment variables
	os.Setenv("TAR_SCORING_ENABLED", "true")
	os.Setenv("AI_PREDICTION_ENABLED", "true")
	
	// Load full config
	cfg, err := LoadFromEnv()
	if err != nil {
		t.Fatalf("LoadFromEnv failed: %v", err)
	}
	
	// Verify AI config is loaded
	if cfg.AI == nil {
		t.Fatal("Expected AI config to be loaded")
	}
	
	if !cfg.AI.TARScoringEnabled {
		t.Error("Expected AI.TARScoringEnabled to be true")
	}
	
	if !cfg.AI.AIPredictionEnabled {
		t.Error("Expected AI.AIPredictionEnabled to be true")
	}
}
