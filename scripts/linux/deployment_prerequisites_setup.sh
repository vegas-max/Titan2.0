#!/bin/bash
# ==============================================================================
# 🚀 TITAN 2.0 - Interactive Deployment Prerequisites Setup Script
# ==============================================================================
# This script guides you through collecting all prerequisite variables needed
# for deploying TITAN 2.0 to any environment (Google Colab, Oracle Cloud, etc.)
#
# Usage: ./deployment_prerequisites_setup.sh
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Banner
print_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                   ║"
    echo "║          ████████╗██╗████████╗ █████╗ ███╗   ██╗                 ║"
    echo "║          ╚══██╔══╝██║╚══██╔══╝██╔══██╗████╗  ██║                 ║"
    echo "║             ██║   ██║   ██║   ███████║██╔██╗ ██║                 ║"
    echo "║             ██║   ██║   ██║   ██╔══██║██║╚██╗██║                 ║"
    echo "║             ██║   ██║   ██║   ██║  ██║██║ ╚████║                 ║"
    echo "║             ╚═╝   ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝                 ║"
    echo "║                                                                   ║"
    echo "║           Deployment Prerequisites Setup Wizard v1.0             ║"
    echo "║                                                                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# Function to print status messages
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

print_step() {
    echo -e "${PURPLE}[→]${NC} $1"
}

print_section() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to read user input with default value
read_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    local secret="${4:-false}"
    local value=""
    
    if [ "$secret" = "true" ]; then
        echo -ne "${BLUE}$prompt${NC}"
        if [ -n "$default" ]; then
            echo -ne " ${YELLOW}[default: $default]${NC}"
        fi
        echo -ne ": "
        read -s value
        echo ""
    else
        echo -ne "${BLUE}$prompt${NC}"
        if [ -n "$default" ]; then
            echo -ne " ${YELLOW}[default: $default]${NC}"
        fi
        echo -ne ": "
        read value
    fi
    
    if [ -z "$value" ] && [ -n "$default" ]; then
        value="$default"
    fi
    
    eval "$var_name='$value'"
    # Clear sensitive values from memory after assignment
    if [ "$secret" = "true" ]; then
        unset value
    fi
}

# Function to validate private key format
# Note: This function removes the 0x prefix if present
# The cleaned key (without prefix) will be stored in the .env file
validate_private_key() {
    local key="$1"
    # Remove 0x prefix if present for validation and storage
    key="${key#0x}"
    # Check if it's 64 hex characters
    if [[ $key =~ ^[0-9a-fA-F]{64}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to show checklist
show_checklist() {
    print_section "PREREQUISITE CHECKLIST"
    
    echo -e "${YELLOW}Before starting, please ensure you have:${NC}"
    echo ""
    echo "  [ ] Google Account (for Colab access)"
    echo "  [ ] Wallet Private Key (dedicated test/trading wallet)"
    echo "  [ ] Infura Account & Project ID (free at https://infura.io)"
    echo ""
    echo -e "${CYAN}Recommended (but optional):${NC}"
    echo ""
    echo "  [ ] Alchemy Account & API Key (free at https://alchemy.com)"
    echo "  [ ] Li.Fi API Key (for cross-chain, free at https://li.fi)"
    echo "  [ ] CoinGecko API Key (for price feeds, free at https://coingecko.com)"
    echo ""
    echo -e "${GREEN}Optional for production:${NC}"
    echo ""
    echo "  [ ] Oracle Cloud Account (for free tier deployment)"
    echo "  [ ] BloxRoute Account (for MEV protection)"
    echo "  [ ] 1inch API Key (for DEX aggregation)"
    echo ""
    echo -e "${PURPLE}Press Enter when ready to continue...${NC}"
    read
}

# Initialize variables
declare -A config

# Main setup wizard
main() {
    print_banner
    
    echo -e "${CYAN}Welcome to the TITAN 2.0 Deployment Prerequisites Setup!${NC}"
    echo ""
    echo "This wizard will guide you through collecting all the necessary"
    echo "information to deploy TITAN 2.0 to any environment."
    echo ""
    echo "You can skip optional fields by pressing Enter."
    echo ""
    
    show_checklist
    
    # ============================================================================
    # SECTION 1: EXECUTION MODE
    # ============================================================================
    print_section "SECTION 1: EXECUTION MODE"
    
    print_info "Execution mode determines how TITAN operates:"
    echo "  • PAPER - Simulated trading with real market data (recommended for testing)"
    echo "  • LIVE  - Real blockchain trading with actual funds (requires capital)"
    echo ""
    
    while true; do
        read_with_default "Select execution mode (PAPER/LIVE)" "PAPER" "config[EXECUTION_MODE]"
        config[EXECUTION_MODE]=$(echo "${config[EXECUTION_MODE]}" | tr '[:lower:]' '[:upper:]')
        
        if [[ "${config[EXECUTION_MODE]}" == "PAPER" ]] || [[ "${config[EXECUTION_MODE]}" == "LIVE" ]]; then
            break
        else
            print_error "Invalid mode. Please enter PAPER or LIVE."
        fi
    done
    
    if [[ "${config[EXECUTION_MODE]}" == "LIVE" ]]; then
        print_warning "⚠️  LIVE mode will execute REAL transactions with REAL money!"
        print_warning "⚠️  Always test in PAPER mode first!"
        print_warning "⚠️  Only use funds you can afford to lose!"
        echo ""
        echo -ne "${YELLOW}Type 'I UNDERSTAND THE RISKS' to continue with LIVE mode: ${NC}"
        read confirmation
        if [[ "$confirmation" != "I UNDERSTAND THE RISKS" ]]; then
            print_error "Live mode not confirmed. Switching to PAPER mode."
            config[EXECUTION_MODE]="PAPER"
        fi
    fi
    
    print_status "Execution mode set to: ${config[EXECUTION_MODE]}"
    
    # ============================================================================
    # SECTION 2: WALLET CONFIGURATION
    # ============================================================================
    print_section "SECTION 2: WALLET CONFIGURATION"
    
    print_info "Your wallet will be used for:"
    echo "  • Paying gas fees for transactions"
    echo "  • Signing transactions"
    echo "  • Receiving arbitrage profits"
    echo ""
    print_warning "⚠️  SECURITY BEST PRACTICES:"
    echo "  • Use a DEDICATED wallet (NOT your main wallet)"
    echo "  • For PAPER mode: Can use a test wallet"
    echo "  • For LIVE mode: Use wallet with MINIMAL funds (just enough for gas)"
    echo "  • NEVER share your private key"
    echo "  • NEVER commit your private key to version control"
    echo ""
    
    while true; do
        read_with_default "Enter your wallet private key (without 0x prefix)" "" "config[PRIVATE_KEY]" "true"
        
        if validate_private_key "${config[PRIVATE_KEY]}"; then
            # Remove 0x prefix if present
            config[PRIVATE_KEY]="${config[PRIVATE_KEY]#0x}"
            print_status "Private key validated successfully"
            break
        else
            print_error "Invalid private key format. Must be 64 hexadecimal characters."
            echo ""
        fi
    done
    
    # ============================================================================
    # SECTION 3: RPC PROVIDERS (REQUIRED)
    # ============================================================================
    print_section "SECTION 3: RPC PROVIDERS (REQUIRED)"
    
    print_info "RPC providers give you access to blockchain networks."
    echo "You need at least one provider. Two providers recommended for failover."
    echo ""
    
    # Infura
    print_step "Infura Configuration"
    echo "  • Sign up free at: https://infura.io"
    echo "  • Create a new project"
    echo "  • Copy your Project ID"
    echo ""
    
    while true; do
        read_with_default "Enter your Infura Project ID" "" "config[INFURA_PROJECT_ID]"
        
        if [ -n "${config[INFURA_PROJECT_ID]}" ]; then
            print_status "Infura Project ID saved"
            break
        else
            print_error "Infura Project ID is required. Please enter a valid ID."
        fi
    done
    
    # Alchemy
    echo ""
    print_step "Alchemy Configuration (Optional but Recommended)"
    echo "  • Sign up free at: https://alchemy.com"
    echo "  • Create a new app"
    echo "  • Copy your API Key"
    echo "  • Used as backup RPC provider for reliability"
    echo ""
    
    read_with_default "Enter your Alchemy API Key (optional)" "" "config[ALCHEMY_API_KEY]"
    
    if [ -n "${config[ALCHEMY_API_KEY]}" ]; then
        print_status "Alchemy API Key saved"
    else
        print_info "Skipping Alchemy (will use Infura only)"
    fi
    
    # ============================================================================
    # SECTION 4: BRIDGE & DEX AGGREGATORS
    # ============================================================================
    print_section "SECTION 4: BRIDGE & DEX AGGREGATORS (OPTIONAL)"
    
    print_info "These services enhance TITAN's capabilities:"
    echo "  • Li.Fi: Cross-chain bridge aggregation (15+ protocols)"
    echo "  • 1inch: DEX aggregation and optimal routing"
    echo "  • 0x: Professional swap aggregation"
    echo ""
    
    # Li.Fi
    print_step "Li.Fi Configuration"
    echo "  • Get free API key at: https://li.fi"
    echo "  • Enables cross-chain arbitrage opportunities"
    echo "  • Aggregates 15+ bridge protocols (Stargate, Across, Hop, etc.)"
    echo ""
    
    read_with_default "Enter your Li.Fi API Key (optional)" "" "config[LIFI_API_KEY]"
    
    if [ -n "${config[LIFI_API_KEY]}" ]; then
        print_status "Li.Fi API Key saved - Cross-chain bridging enabled"
        config[ENABLE_CROSS_CHAIN]="true"
    else
        print_info "Skipping Li.Fi - Cross-chain bridging disabled"
        config[ENABLE_CROSS_CHAIN]="false"
    fi
    
    # 1inch
    echo ""
    print_step "1inch Configuration"
    echo "  • Get API key at: https://portal.1inch.dev/"
    echo "  • Enables DEX aggregation for better pricing"
    echo ""
    
    read_with_default "Enter your 1inch API Key (optional)" "" "config[ONEINCH_API_KEY]"
    
    if [ -n "${config[ONEINCH_API_KEY]}" ]; then
        print_status "1inch API Key saved"
    else
        print_info "Skipping 1inch"
    fi
    
    # 0x
    echo ""
    print_step "0x/Matcha Configuration"
    echo "  • Get API key at: https://0x.org/docs/introduction/getting-started"
    echo "  • Professional-grade swap aggregation"
    echo ""
    
    read_with_default "Enter your 0x API Key (optional)" "" "config[ZEROX_API_KEY]"
    
    if [ -n "${config[ZEROX_API_KEY]}" ]; then
        print_status "0x API Key saved"
    else
        print_info "Skipping 0x"
    fi
    
    # ============================================================================
    # SECTION 5: PRICE FEEDS & DATA
    # ============================================================================
    print_section "SECTION 5: PRICE FEEDS & DATA (OPTIONAL)"
    
    # CoinGecko
    print_step "CoinGecko Configuration"
    echo "  • Get free API key at: https://www.coingecko.com/en/api"
    echo "  • Provides reliable token price data"
    echo "  • Used as fallback for price feeds"
    echo ""
    
    read_with_default "Enter your CoinGecko API Key (optional)" "" "config[COINGECKO_API_KEY]"
    
    if [ -n "${config[COINGECKO_API_KEY]}" ]; then
        print_status "CoinGecko API Key saved"
    else
        print_info "Skipping CoinGecko - Will use default price sources"
    fi
    
    # ============================================================================
    # SECTION 6: MEV PROTECTION (OPTIONAL)
    # ============================================================================
    print_section "SECTION 6: MEV PROTECTION (OPTIONAL)"
    
    print_info "MEV (Maximal Extractable Value) protection prevents frontrunning."
    echo "  • BloxRoute: Private mempool submission"
    echo "  • Recommended for high-value trades (>$1000)"
    echo ""
    
    read_with_default "Enter your BloxRoute Auth Key (optional)" "" "config[BLOXROUTE_AUTH]"
    
    if [ -n "${config[BLOXROUTE_AUTH]}" ]; then
        print_status "BloxRoute Auth Key saved - MEV protection enabled"
        config[ENABLE_MEV_PROTECTION]="true"
    else
        print_info "Skipping BloxRoute - MEV protection disabled"
        config[ENABLE_MEV_PROTECTION]="false"
    fi
    
    # ============================================================================
    # SECTION 7: ADVANCED SETTINGS
    # ============================================================================
    print_section "SECTION 7: ADVANCED SETTINGS"
    
    print_info "Configure advanced parameters (or use defaults):"
    echo ""
    
    read_with_default "Minimum profit threshold in USD" "5.00" "config[MIN_PROFIT_USD]"
    read_with_default "Maximum slippage in basis points (50 = 0.5%)" "50" "config[MAX_SLIPPAGE_BPS]"
    read_with_default "Maximum priority fee in gwei" "50" "config[MAX_PRIORITY_FEE_GWEI]"
    read_with_default "Maximum base fee in gwei" "200" "config[MAX_BASE_FEE_GWEI]"
    
    # Set additional defaults
    config[REDIS_URL]="redis://localhost:6379"
    config[DASHBOARD_PORT]="8080"
    config[ENABLE_SIMULATION]="true"
    config[ENABLE_REALTIME_TRAINING]="true"
    config[LOG_LEVEL]="INFO"
    config[USE_REAL_DATA]="true"
    config[FLASH_LOAN_ENABLED]="true"
    config[FLASH_LOAN_PROVIDER]="1"
    config[ENFORCE_SIMULATION]="true"
    config[GAS_STRATEGY]="ADAPTIVE"
    
    # ============================================================================
    # SECTION 8: SUMMARY & CONFIRMATION
    # ============================================================================
    print_section "SECTION 8: CONFIGURATION SUMMARY"
    
    echo -e "${CYAN}Your configuration:${NC}"
    echo ""
    echo "  Execution Mode:     ${config[EXECUTION_MODE]}"
    # Show last 4 characters of private key safely
    local masked_key="${config[PRIVATE_KEY]}"
    echo "  Private Key:        ****...${masked_key: -4}"
    echo ""
    echo "  RPC Providers:"
    echo "    Infura:           ${config[INFURA_PROJECT_ID]:0:8}..."
    if [ -n "${config[ALCHEMY_API_KEY]}" ]; then
        echo "    Alchemy:          ${config[ALCHEMY_API_KEY]:0:8}..."
    else
        echo "    Alchemy:          Not configured"
    fi
    echo ""
    echo "  Bridge & DEX:"
    if [ -n "${config[LIFI_API_KEY]}" ]; then
        echo "    Li.Fi:            ✓ Configured"
    else
        echo "    Li.Fi:            ✗ Not configured"
    fi
    if [ -n "${config[ONEINCH_API_KEY]}" ]; then
        echo "    1inch:            ✓ Configured"
    else
        echo "    1inch:            ✗ Not configured"
    fi
    if [ -n "${config[ZEROX_API_KEY]}" ]; then
        echo "    0x:               ✓ Configured"
    else
        echo "    0x:               ✗ Not configured"
    fi
    echo ""
    echo "  Features:"
    echo "    Cross-chain:      ${config[ENABLE_CROSS_CHAIN]}"
    echo "    MEV Protection:   ${config[ENABLE_MEV_PROTECTION]}"
    echo "    Flash Loans:      ${config[FLASH_LOAN_ENABLED]}"
    echo ""
    echo "  Strategy:"
    echo "    Min Profit:       \$${config[MIN_PROFIT_USD]}"
    echo "    Max Slippage:     ${config[MAX_SLIPPAGE_BPS]} bps"
    echo "    Max Priority Fee: ${config[MAX_PRIORITY_FEE_GWEI]} gwei"
    echo ""
    
    echo -ne "${YELLOW}Save this configuration? (yes/no): ${NC}"
    read confirmation
    
    if [[ "$confirmation" != "yes" ]] && [[ "$confirmation" != "y" ]]; then
        print_error "Configuration not saved. Exiting."
        exit 1
    fi
    
    # ============================================================================
    # SECTION 9: GENERATE CONFIGURATION FILES
    # ============================================================================
    print_section "SECTION 9: GENERATING CONFIGURATION FILES"
    
    # Generate .env file
    ENV_FILE=".env"
    
    print_step "Creating $ENV_FILE file..."
    
    cat > "$ENV_FILE" << EOF
# ==============================================================================
# TITAN 2.0 - Deployment Configuration
# Generated by deployment_prerequisites_setup.sh on $(date)
# ==============================================================================

# --- EXECUTION MODE ---
EXECUTION_MODE=${config[EXECUTION_MODE]}

# --- WALLET CONFIGURATION ---
PRIVATE_KEY=${config[PRIVATE_KEY]}

# --- RPC PROVIDERS ---
INFURA_PROJECT_ID=${config[INFURA_PROJECT_ID]}
ALCHEMY_API_KEY=${config[ALCHEMY_API_KEY]:-}

# Generate RPC URLs from Infura Project ID
RPC_ETHEREUM=https://mainnet.infura.io/v3/${config[INFURA_PROJECT_ID]}
WSS_ETHEREUM=wss://mainnet.infura.io/ws/v3/${config[INFURA_PROJECT_ID]}
RPC_POLYGON=https://polygon-mainnet.infura.io/v3/${config[INFURA_PROJECT_ID]}
WSS_POLYGON=wss://polygon-mainnet.infura.io/ws/v3/${config[INFURA_PROJECT_ID]}
RPC_ARBITRUM=https://arbitrum-mainnet.infura.io/v3/${config[INFURA_PROJECT_ID]}
WSS_ARBITRUM=wss://arbitrum-mainnet.infura.io/ws/v3/${config[INFURA_PROJECT_ID]}
RPC_OPTIMISM=https://optimism-mainnet.infura.io/v3/${config[INFURA_PROJECT_ID]}
WSS_OPTIMISM=wss://optimism-mainnet.infura.io/ws/v3/${config[INFURA_PROJECT_ID]}
RPC_BASE=https://base-mainnet.infura.io/v3/${config[INFURA_PROJECT_ID]}
WSS_BASE=wss://base-mainnet.infura.io/ws/v3/${config[INFURA_PROJECT_ID]}

EOF
    
    # Add Alchemy if configured
    if [ -n "${config[ALCHEMY_API_KEY]}" ]; then
        cat >> "$ENV_FILE" << EOF
# Alchemy RPC endpoints (backup)
ALCHEMY_RPC_ETH=https://eth-mainnet.g.alchemy.com/v2/${config[ALCHEMY_API_KEY]}
ALCHEMY_WSS_ETH=wss://eth-mainnet.g.alchemy.com/v2/${config[ALCHEMY_API_KEY]}
ALCHEMY_RPC_POLY=https://polygon-mainnet.g.alchemy.com/v2/${config[ALCHEMY_API_KEY]}
ALCHEMY_WSS_POLY=wss://polygon-mainnet.g.alchemy.com/v2/${config[ALCHEMY_API_KEY]}
ALCHEMY_RPC_ARB=https://arb-mainnet.g.alchemy.com/v2/${config[ALCHEMY_API_KEY]}
ALCHEMY_WSS_ARB=wss://arb-mainnet.g.alchemy.com/v2/${config[ALCHEMY_API_KEY]}
ALCHEMY_RPC_OPT=https://opt-mainnet.g.alchemy.com/v2/${config[ALCHEMY_API_KEY]}
ALCHEMY_WSS_OPT=wss://opt-mainnet.g.alchemy.com/v2/${config[ALCHEMY_API_KEY]}

EOF
    fi
    
    # Add free RPC endpoints for other chains
    cat >> "$ENV_FILE" << EOF
# Free RPC endpoints for additional chains
RPC_BSC=https://bsc-dataseed.binance.org
WSS_BSC=wss://bsc-ws-node.nariox.org:443
RPC_AVALANCHE=https://api.avax.network/ext/bc/C/rpc
WSS_AVALANCHE=wss://api.avax.network/ext/bc/C/ws
RPC_FANTOM=https://rpc.ftm.tools
WSS_FANTOM=wss://wsapi.fantom.network

# --- BRIDGE & DEX AGGREGATORS ---
LIFI_API_KEY=${config[LIFI_API_KEY]:-}
ONEINCH_API_KEY=${config[ONEINCH_API_KEY]:-}
ZEROX_API_KEY=${config[ZEROX_API_KEY]:-}

# --- PRICE FEEDS ---
COINGECKO_API_KEY=${config[COINGECKO_API_KEY]:-}

# --- MEV PROTECTION ---
BLOXROUTE_AUTH=${config[BLOXROUTE_AUTH]:-}

# --- STRATEGY PARAMETERS ---
MIN_PROFIT_USD=${config[MIN_PROFIT_USD]}
MAX_SLIPPAGE_BPS=${config[MAX_SLIPPAGE_BPS]}
MAX_PRIORITY_FEE_GWEI=${config[MAX_PRIORITY_FEE_GWEI]}
MAX_BASE_FEE_GWEI=${config[MAX_BASE_FEE_GWEI]}
GAS_LIMIT_MULTIPLIER=1.2

# --- FLASH LOAN CONFIGURATION ---
FLASH_LOAN_ENABLED=${config[FLASH_LOAN_ENABLED]}
FLASH_LOAN_PROVIDER=${config[FLASH_LOAN_PROVIDER]}
ENFORCE_SIMULATION=${config[ENFORCE_SIMULATION]}

# --- SYSTEM CONFIGURATION ---
REDIS_URL=${config[REDIS_URL]}
DASHBOARD_PORT=${config[DASHBOARD_PORT]}
ENABLE_CROSS_CHAIN=${config[ENABLE_CROSS_CHAIN]}
ENABLE_MEV_PROTECTION=${config[ENABLE_MEV_PROTECTION]}
ENABLE_SIMULATION=${config[ENABLE_SIMULATION]}
ENABLE_REALTIME_TRAINING=${config[ENABLE_REALTIME_TRAINING]}
USE_REAL_DATA=${config[USE_REAL_DATA]}
LOG_LEVEL=${config[LOG_LEVEL]}
GAS_STRATEGY=${config[GAS_STRATEGY]}

# --- AI & ML FEATURES ---
ENABLE_ML_MODELS=true
TAR_SCORING_ENABLED=true
AI_PREDICTION_ENABLED=true
SELF_LEARNING_ENABLED=true
ROUTE_INTELLIGENCE_ENABLED=true

# --- ADDITIONAL SETTINGS ---
MAX_CONSECUTIVE_FAILURES=10
CIRCUIT_BREAKER_COOLDOWN=60
MAX_REQUESTS_PER_MINUTE=100
CACHE_TTL=300
CONFIRMATION_BLOCKS=2
EOF
    
    print_status ".env file created successfully!"
    
    # Generate deployment summary
    SUMMARY_FILE="deployment_config_summary.txt"
    
    print_step "Creating deployment summary..."
    
    cat > "$SUMMARY_FILE" << EOF
================================================================================
TITAN 2.0 - Deployment Configuration Summary
Generated: $(date)
================================================================================

EXECUTION MODE: ${config[EXECUTION_MODE]}

PREREQUISITES CHECKLIST:
  ✓ Wallet private key configured
  ✓ Infura Project ID configured
$([ -n "${config[ALCHEMY_API_KEY]}" ] && echo "  ✓ Alchemy API Key configured" || echo "  ✗ Alchemy API Key not configured (optional)")
$([ -n "${config[LIFI_API_KEY]}" ] && echo "  ✓ Li.Fi API Key configured" || echo "  ✗ Li.Fi API Key not configured (optional)")
$([ -n "${config[ONEINCH_API_KEY]}" ] && echo "  ✓ 1inch API Key configured" || echo "  ✗ 1inch API Key not configured (optional)")
$([ -n "${config[BLOXROUTE_AUTH]}" ] && echo "  ✓ BloxRoute configured" || echo "  ✗ BloxRoute not configured (optional)")

ENABLED FEATURES:
  • Flash Loans: ${config[FLASH_LOAN_ENABLED]}
  • Cross-chain: ${config[ENABLE_CROSS_CHAIN]}
  • MEV Protection: ${config[ENABLE_MEV_PROTECTION]}
  • Transaction Simulation: ${config[ENABLE_SIMULATION]}
  • Real-time Training: ${config[ENABLE_REALTIME_TRAINING]}

STRATEGY PARAMETERS:
  • Minimum Profit: \$${config[MIN_PROFIT_USD]}
  • Maximum Slippage: ${config[MAX_SLIPPAGE_BPS]} basis points (${config[MAX_SLIPPAGE_BPS]/100}%)
  • Maximum Priority Fee: ${config[MAX_PRIORITY_FEE_GWEI]} gwei
  • Maximum Base Fee: ${config[MAX_BASE_FEE_GWEI]} gwei
  • Gas Strategy: ${config[GAS_STRATEGY]}

NEXT STEPS:
  1. Review the generated .env file
  2. Copy .env to your deployment environment
  3. Start TITAN components:
     - Google Colab: Follow cells in Titan_Google_Colab.ipynb
     - Local: Run ./setup.sh && make start
     - Oracle Cloud: Run ./deploy_oracle_cloud.sh
  4. Access dashboard at http://localhost:${config[DASHBOARD_PORT]}
  5. Monitor system logs for opportunities

IMPORTANT SECURITY REMINDERS:
  ⚠️  NEVER commit .env file to version control
  ⚠️  Use a dedicated wallet (NOT your main wallet)
  ⚠️  Start with ${config[EXECUTION_MODE]} mode first
  $([ "${config[EXECUTION_MODE]}" == "LIVE" ] && echo "  ⚠️  Use MINIMAL funds in LIVE mode")
  ⚠️  Monitor gas prices and adjust limits as needed
  ⚠️  Enable MEV protection for high-value trades

SUPPORT:
  • Documentation: README.md, QUICKSTART.md
  • Google Colab Guide: GOOGLE_COLAB_GUIDE.md
  • Oracle Deployment: ORACLE_CLOUD_DEPLOYMENT.md
  • GitHub Issues: https://github.com/vegas-max/Titan2.0/issues

================================================================================
Configuration saved successfully! You're ready to deploy TITAN 2.0!
================================================================================
EOF
    
    print_status "Deployment summary created: $SUMMARY_FILE"
    
    # ============================================================================
    # FINAL OUTPUT
    # ============================================================================
    print_section "SETUP COMPLETE! 🎉"
    
    echo -e "${GREEN}Configuration files generated successfully!${NC}"
    echo ""
    echo "Generated files:"
    echo "  • .env - Environment configuration"
    echo "  • $SUMMARY_FILE - Deployment summary"
    echo ""
    
    print_info "View your configuration summary:"
    echo "  cat $SUMMARY_FILE"
    echo ""
    
    print_warning "IMPORTANT: Keep your .env file secure!"
    echo "  • Never commit it to version control"
    echo "  • Never share it publicly"
    echo "  • Use secure transfer methods for deployment"
    echo ""
    
    echo -e "${CYAN}Next steps based on your deployment target:${NC}"
    echo ""
    echo "  📓 Google Colab:"
    echo "     1. Upload Titan_Google_Colab.ipynb to Google Colab"
    echo "     2. Run the configuration cell and paste your values"
    echo "     3. Follow the step-by-step cells"
    echo ""
    echo "  💻 Local Development:"
    echo "     1. Run: ./setup.sh"
    echo "     2. Run: make start"
    echo "     3. Access dashboard: http://localhost:${config[DASHBOARD_PORT]}"
    echo ""
    echo "  ☁️  Oracle Cloud:"
    echo "     1. Copy .env to your Oracle instance"
    echo "     2. Run: ./deploy_oracle_cloud.sh"
    echo "     3. Follow the deployment wizard"
    echo ""
    
    print_status "Setup wizard completed successfully!"
    echo ""
    echo -e "${PURPLE}For detailed instructions, see:${NC}"
    echo "  • GOOGLE_COLAB_GUIDE.md - Google Colab setup"
    echo "  • QUICKSTART.md - Quick start guide"
    echo "  • README.md - Complete documentation"
    echo ""
    
}

# Run main function
main "$@"
