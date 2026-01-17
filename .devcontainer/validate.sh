#!/bin/bash

# ==============================================================================
# Codespace Configuration Validation Script
# ==============================================================================
# This script validates the GitHub Codespace configuration to ensure
# all necessary components are properly set up.
# ==============================================================================

echo "===================================================="
echo "  CODESPACE CONFIGURATION VALIDATION"
echo "===================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

passed=0
failed=0

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    passed=$((passed + 1))
}

print_failure() {
    echo -e "${RED}❌ $1${NC}"
    failed=$((failed + 1))
}

print_info() {
    echo -e "ℹ️  $1"
}

# Test 1: Check devcontainer.json exists and is valid JSON
echo "Test 1: Validating devcontainer.json..."
if [ -f ".devcontainer/devcontainer.json" ]; then
    if python3 -m json.tool .devcontainer/devcontainer.json > /dev/null 2>&1; then
        print_success "devcontainer.json is valid JSON"
    else
        print_failure "devcontainer.json has invalid JSON syntax"
    fi
else
    print_failure "devcontainer.json not found"
fi
echo ""

# Test 2: Check setup.sh exists and is executable
echo "Test 2: Validating setup.sh..."
if [ -f ".devcontainer/setup.sh" ]; then
    if [ -x ".devcontainer/setup.sh" ]; then
        print_success "setup.sh is executable"
    else
        print_failure "setup.sh is not executable"
    fi
    
    if bash -n .devcontainer/setup.sh 2>/dev/null; then
        print_success "setup.sh has no syntax errors"
    else
        print_failure "setup.sh has syntax errors"
    fi
else
    print_failure "setup.sh not found"
fi
echo ""

# Test 3: Check documentation files
echo "Test 3: Validating documentation..."
if [ -f ".devcontainer/README.md" ]; then
    print_success "README.md exists"
else
    print_failure "README.md not found"
fi

if [ -f ".devcontainer/CI_CD_OPERATIONS.md" ]; then
    print_success "CI_CD_OPERATIONS.md exists"
else
    print_failure "CI_CD_OPERATIONS.md not found"
fi
echo ""

# Test 4: Check required features in devcontainer.json
echo "Test 4: Checking required features..."
if grep -q "node" .devcontainer/devcontainer.json; then
    print_success "Node.js feature configured"
else
    print_failure "Node.js feature missing"
fi

if grep -q "python" .devcontainer/devcontainer.json; then
    print_success "Python feature configured"
else
    print_failure "Python feature missing"
fi

if grep -q "rust" .devcontainer/devcontainer.json; then
    print_success "Rust feature configured"
else
    print_failure "Rust feature missing"
fi

if grep -q "go" .devcontainer/devcontainer.json; then
    print_success "Go feature configured"
else
    print_failure "Go feature missing"
fi
echo ""

# Test 5: Check port forwarding configuration
echo "Test 5: Checking port forwarding..."
if grep -q "forwardPorts" .devcontainer/devcontainer.json; then
    print_success "Port forwarding configured"
    
    for port in 3000 3001 8000 8080; do
        if grep -q "$port" .devcontainer/devcontainer.json; then
            print_success "Port $port configured"
        else
            print_failure "Port $port not configured"
        fi
    done
else
    print_failure "Port forwarding not configured"
fi
echo ""

# Test 6: Check VSCode extensions
echo "Test 6: Checking VSCode extensions..."
if grep -q "extensions" .devcontainer/devcontainer.json; then
    print_success "VSCode extensions configured"
    
    for ext in "eslint" "python" "rust-analyzer" "golang.go"; do
        if grep -qi "$ext" .devcontainer/devcontainer.json; then
            print_success "Extension for $ext configured"
        fi
    done
else
    print_failure "VSCode extensions not configured"
fi
echo ""

# Test 7: Check CI/CD files
echo "Test 7: Checking CI/CD workflow files..."
if [ -f ".github/workflows/ci.yml" ]; then
    print_success "CI workflow exists"
else
    print_failure "CI workflow not found"
fi

if [ -f "Makefile" ]; then
    print_success "Makefile exists"
else
    print_failure "Makefile not found"
fi
echo ""

# Test 8: Check prerequisite files
echo "Test 8: Checking prerequisite files..."
for file in "package.json" "requirements.txt" ".env.example"; do
    if [ -f "$file" ]; then
        print_success "$file exists"
    else
        print_failure "$file not found"
    fi
done
echo ""

# Summary
echo "===================================================="
echo "  VALIDATION SUMMARY"
echo "===================================================="
echo -e "${GREEN}Passed: $passed${NC}"
if [ $failed -gt 0 ]; then
    echo -e "${RED}Failed: $failed${NC}"
else
    echo -e "${GREEN}Failed: $failed${NC}"
fi
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✅ All validation checks passed!${NC}"
    echo "The Codespace configuration is ready to use."
    exit 0
else
    echo -e "${RED}❌ Some validation checks failed.${NC}"
    echo "Please review and fix the issues above."
    exit 1
fi
