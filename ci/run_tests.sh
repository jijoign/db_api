#!/bin/bash
# CI/CD test runner script for Unix systems

set -e

echo "========================================"
echo "CI/CD Test Runner"
echo "========================================"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found!"
    exit 1
fi

# Parse arguments
SKIP_SLOW=false
VERBOSE=false
SUITE="all"

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-slow)
            SKIP_SLOW=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --suite)
            SUITE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build command
CMD="python3 ci/run_tests.py --suite $SUITE"

if [ "$SKIP_SLOW" = true ]; then
    CMD="$CMD --skip-slow"
fi

if [ "$VERBOSE" = true ]; then
    CMD="$CMD --verbose"
fi

# Run tests
echo "Running: $CMD"
echo
$CMD

exit $?
