#!/bin/bash
################################################################################
# TITAN 2.0 - PRE-START VALIDATION
# 
# This script runs before system startup to ensure all modules are validated.
# Enforces military-style gate validation before allowing operations.
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         TITAN 2.0 - PRE-START VALIDATION CHECK                    ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}\n"

# Check if validation has been run recently
VALIDATION_MARKER=".last_validation"
VALIDATION_TIMEOUT=3600  # 1 hour

should_validate=true

if [ -f "$VALIDATION_MARKER" ]; then
    last_validation=$(cat "$VALIDATION_MARKER")
    current_time=$(date +%s)
    time_diff=$((current_time - last_validation))
    
    if [ $time_diff -lt $VALIDATION_TIMEOUT ]; then
        echo -e "${GREEN}✓ System was validated $(($time_diff / 60)) minutes ago${NC}"
        echo -e "${GREEN}  Validation still valid (expires in $(( ($VALIDATION_TIMEOUT - $time_diff) / 60 )) minutes)${NC}\n"
        should_validate=false
    else
        echo -e "${YELLOW}⚠ Last validation expired ($(($time_diff / 3600)) hours ago)${NC}"
        echo -e "${YELLOW}  Running fresh validation...${NC}\n"
    fi
else
    echo -e "${YELLOW}⚠ No previous validation found${NC}"
    echo -e "${YELLOW}  Running military-style module validation...${NC}\n"
fi

# Run validation if needed
if [ "$should_validate" = true ]; then
    # Check if Python 3 is available
    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "\n${RED}✗ Python 3 not found${NC}"
        echo -e "${RED}  Please install Python 3.11 or higher${NC}\n"
        exit 1
    fi
    
    if python3 military_audit.py; then
        echo -e "\n${GREEN}✓ Military audit PASSED${NC}"
        # Mark validation timestamp
        date +%s > "$VALIDATION_MARKER"
        echo -e "${GREEN}✓ System validated and ready for operation${NC}\n"
    else
        echo -e "\n${RED}✗ Military audit FAILED${NC}"
        echo -e "${RED}✗ System cannot start - fix validation errors first${NC}\n"
        exit 1
    fi
fi

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ PRE-START VALIDATION COMPLETE - PROCEEDING WITH STARTUP        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════╝${NC}\n"

exit 0
