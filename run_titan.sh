#!/bin/bash
# Wrapper script for backward compatibility
# Redirects to the actual script in scripts/linux/
exec ./scripts/linux/run_titan.sh "$@"
