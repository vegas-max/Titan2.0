#!/bin/bash

# ==============================================================================
# 🔍 Oracle Cloud Free Tier Configuration Validation Script
# ==============================================================================
# This script validates that all Oracle Cloud deployment components are present
# and properly configured in the Titan 2.0 repository.
#
# Usage: ./validate_oracle_cloud_config.sh
# ==============================================================================

# Note: Not using 'set -e' so script continues checking all components

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_TOTAL=0

# Banner
echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Oracle Cloud Free Tier Configuration Validation          ║"
echo "║  Titan 2.0 - Deployment Readiness Check                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Helper functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
    ((CHECKS_TOTAL++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
    ((CHECKS_TOTAL++))
}

check_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

section_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 1. Check Documentation Files
section_header "📚 Documentation Files"

docs=(
    "ORACLE_CLOUD_DEPLOYMENT.md"
    "ORACLE_QUICKSTART.md"
    "ORACLE_DEPLOYMENT_CHECKLIST.md"
    "ORACLE_QUICK_REFERENCE.md"
    "ORACLE_TROUBLESHOOTING.md"
    "ORACLE_DEPLOYMENT_SUMMARY.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        LINES=$(wc -l < "$doc")
        check_pass "$doc exists ($LINES lines)"
    else
        check_fail "$doc is missing"
    fi
done

# 2. Check Deployment Scripts
section_header "🚀 Deployment Scripts"

scripts=(
    "deploy_oracle_cloud.sh"
    "start_oracle.sh"
    "stop_oracle.sh"
    "restart_oracle.sh"
    "status_oracle.sh"
    "oracle_health_check.sh"
)

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            check_pass "$script exists and is executable"
        else
            check_fail "$script exists but is NOT executable (run: chmod +x $script)"
        fi
        
        # Syntax check
        if bash -n "$script" 2>/dev/null; then
            check_pass "$script syntax is valid"
        else
            check_fail "$script has syntax errors"
        fi
    else
        check_fail "$script is missing"
    fi
done

# 3. Check Systemd Service Templates
section_header "⚙️ Systemd Service Templates"

if [ -d "systemd" ]; then
    check_pass "systemd/ directory exists"
    
    templates=(
        "systemd/titan-brain.service.template"
        "systemd/titan-executor.service.template"
        "systemd/titan-redis.service.template"
        "systemd/README.md"
    )
    
    for template in "${templates[@]}"; do
        if [ -f "$template" ]; then
            check_pass "$template exists"
            
            # Check for required placeholders in templates
            if [[ "$template" == *.template ]]; then
                if grep -q "REPLACE_WITH_USER\|REPLACE_WITH_WORKDIR" "$template" 2>/dev/null; then
                    check_pass "$template has required placeholders"
                elif [[ "$template" == *"redis"* ]]; then
                    check_pass "$template is Redis service (no placeholders needed)"
                else
                    check_fail "$template missing required placeholders"
                fi
            fi
        else
            check_fail "$template is missing"
        fi
    done
else
    check_fail "systemd/ directory is missing"
fi

# 4. Check Docker Configuration
section_header "🐳 Docker Configuration"

if [ -f "docker-compose.oracle.yml" ]; then
    check_pass "docker-compose.oracle.yml exists"
    
    # Validate YAML syntax (if docker-compose is available)
    if command -v docker-compose &> /dev/null; then
        if docker-compose -f docker-compose.oracle.yml config &> /dev/null; then
            check_pass "docker-compose.oracle.yml syntax is valid"
        else
            check_fail "docker-compose.oracle.yml has syntax errors"
        fi
    else
        check_info "docker-compose not installed, skipping YAML validation"
    fi
else
    check_fail "docker-compose.oracle.yml is missing"
fi

dockerfiles=(
    "Dockerfile.brain"
    "Dockerfile.executor"
    "Dockerfile.dashboard"
)

for dockerfile in "${dockerfiles[@]}"; do
    if [ -f "$dockerfile" ]; then
        check_pass "$dockerfile exists"
    else
        check_fail "$dockerfile is missing"
    fi
done

# 5. Check Environment Configuration
section_header "🔧 Environment Configuration"

if [ -f ".env.example" ]; then
    check_pass ".env.example exists"
    
    # Check for required environment variables
    required_vars=(
        "PRIVATE_KEY"
        "RPC_POLYGON"
        "RPC_ETHEREUM"
        "LIFI_API_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if grep -q "^$var=" .env.example 2>/dev/null; then
            check_pass ".env.example contains $var"
        else
            check_fail ".env.example missing $var"
        fi
    done
else
    check_fail ".env.example is missing"
fi

# 6. Check README Integration
section_header "📖 README Integration"

if [ -f "README.md" ]; then
    check_pass "README.md exists"
    
    # Check for Oracle Cloud section
    if grep -q "Oracle Cloud" README.md; then
        check_pass "README.md mentions Oracle Cloud"
    else
        check_fail "README.md does not mention Oracle Cloud"
    fi
    
    # Check for free tier mention
    if grep -qi "free tier\|always free" README.md; then
        check_pass "README.md mentions Always Free tier"
    else
        check_fail "README.md does not mention Always Free tier"
    fi
    
    # Check for deployment script reference
    if grep -q "deploy_oracle_cloud.sh" README.md; then
        check_pass "README.md references deploy_oracle_cloud.sh"
    else
        check_fail "README.md does not reference deploy_oracle_cloud.sh"
    fi
else
    check_fail "README.md is missing"
fi

# 7. Check for Required Directories
section_header "📁 Directory Structure"

required_dirs=(
    "offchain/ml"
    "offchain/execution"
    "systemd"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        check_pass "$dir/ directory exists"
    else
        check_fail "$dir/ directory is missing"
    fi
done

# 8. Verify Free Tier Specifications in Documentation
section_header "💰 Free Tier Specifications"

check_info "Validating Oracle Cloud Always Free tier specifications..."

# Check ARM A1.Flex specifications
if grep -q "4 OCPU" ORACLE_CLOUD_DEPLOYMENT.md 2>/dev/null && grep -q "24 GB" ORACLE_CLOUD_DEPLOYMENT.md 2>/dev/null; then
    check_pass "ARM A1.Flex specs documented correctly (4 OCPUs, 24GB RAM)"
else
    check_fail "ARM A1.Flex specs not documented correctly"
fi

# Check AMD E2.1.Micro specifications
if grep -q "1 OCPU.*1 GB" ORACLE_CLOUD_DEPLOYMENT.md 2>/dev/null; then
    check_pass "AMD E2.1.Micro specs documented correctly (1 OCPU, 1GB RAM)"
else
    check_fail "AMD E2.1.Micro specs not documented correctly"
fi

# Check storage specs
if grep -q "200 GB.*Block Volume" ORACLE_CLOUD_DEPLOYMENT.md 2>/dev/null; then
    check_pass "Storage specs documented correctly (200GB Block Volume)"
else
    check_fail "Storage specs not documented correctly"
fi

# 9. Check Script Content for Key Features
section_header "✨ Key Features Validation"

if [ -f "deploy_oracle_cloud.sh" ]; then
    # Check for architecture detection
    if grep -q "detect_architecture" deploy_oracle_cloud.sh; then
        check_pass "Deployment script has architecture detection"
    else
        check_fail "Deployment script missing architecture detection"
    fi
    
    # Check for instance type detection
    if grep -q "INSTANCE_TYPE" deploy_oracle_cloud.sh; then
        check_pass "Deployment script has instance type detection"
    else
        check_fail "Deployment script missing instance type detection"
    fi
    
    # Check for Redis optional installation
    if grep -q "Redis.*optional\|OPTIONAL.*Redis" deploy_oracle_cloud.sh; then
        check_pass "Deployment script supports optional Redis"
    else
        check_fail "Deployment script does not mention Redis as optional"
    fi
    
    # Check for lightweight mode configuration
    if grep -q "LIGHTWEIGHT_MODE" deploy_oracle_cloud.sh; then
        check_pass "Deployment script configures lightweight mode"
    else
        check_fail "Deployment script missing lightweight mode configuration"
    fi
fi

if [ -f "oracle_health_check.sh" ]; then
    # Check for comprehensive health checks
    if grep -q "System Resources\|Dependencies\|Titan Services" oracle_health_check.sh; then
        check_pass "Health check script has comprehensive checks"
    else
        check_fail "Health check script missing comprehensive checks"
    fi
    
    # Check for signal system validation
    if grep -q "signal.*file\|file.*signal" oracle_health_check.sh -i; then
        check_pass "Health check validates file-based signal system"
    else
        check_fail "Health check missing signal system validation"
    fi
fi

# 10. Final Summary
section_header "📊 Validation Summary"

echo ""
echo -e "Total Checks: ${CYAN}$CHECKS_TOTAL${NC}"
echo -e "Passed: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "Failed: ${RED}$CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL CHECKS PASSED!                                     ║${NC}"
    echo -e "${GREEN}║  Oracle Cloud Free Tier deployment is FULLY CONFIGURED    ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}✨ The Oracle Cloud Always Free tier deployment is ready!${NC}"
    echo ""
    echo "You can deploy with:"
    echo -e "  ${YELLOW}./deploy_oracle_cloud.sh${NC}"
    echo ""
    echo "For more information, see:"
    echo "  - ORACLE_QUICKSTART.md (15-minute quick start)"
    echo "  - ORACLE_CLOUD_DEPLOYMENT.md (comprehensive guide)"
    echo "  - ORACLE_FREE_TIER_VALIDATION.md (detailed validation report)"
    echo ""
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ⚠️  VALIDATION FAILED                                     ║${NC}"
    echo -e "${RED}║  Some components are missing or misconfigured             ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Please review the failed checks above and fix the issues.${NC}"
    echo ""
    exit 1
fi
