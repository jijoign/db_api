#!/bin/bash
# Quick build script for Linux/macOS

set -e

echo "========================================"
echo "REST API Library - Build Script"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found!"
    echo "Please install Python 3.8 or higher."
    exit 1
fi

# Detect and activate virtual environment
PYTHON_CMD="python3"
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    PYTHON_CMD="python"
fi

# Function to show help
show_help() {
    echo "Usage: ./build.sh [database] [--package]"
    echo
    echo "Database Options:"
    echo "  (none)      - Build all database versions"
    echo "  clean       - Clean build directories"
    echo "  sqlite      - Build SQLite-only version"
    echo "  postgresql  - Build PostgreSQL version"
    echo "  mysql       - Build MySQL version"
    echo "  all         - Build all database-specific versions"
    echo "  help        - Show this help message"
    echo
    echo "Flags:"
    echo "  --package   - Create distribution package after build"
    echo
    echo "Examples:"
    echo "  ./build.sh                    Build all databases"
    echo "  ./build.sh sqlite             Build SQLite version"
    echo "  ./build.sh sqlite --package   Build and package SQLite"
    echo "  ./build.sh all --package      Build and package all"
    echo
}

# Parse arguments
DB_TYPE="${1:-all}"
PACKAGE_FLAG=""

# Check for --package flag in second argument
if [ "$2" = "--package" ]; then
    PACKAGE_FLAG="--package"
fi

case "$DB_TYPE" in
    default|all)
        echo "Building all database versions..."
        $PYTHON_CMD build.py all $PACKAGE_FLAG
        ;;
    clean)
        echo "Cleaning build directories..."
        rm -rf build dist *.spec
        echo "Clean completed!"
        ;;
    sqlite)
        echo "Building SQLite version..."
        $PYTHON_CMD build.py sqlite $PACKAGE_FLAG
        ;;
    postgresql)
        echo "Building PostgreSQL version..."
        $PYTHON_CMD build.py postgresql $PACKAGE_FLAG
        ;;
    mysql)
        echo "Building MySQL version..."
        $PYTHON_CMD build.py mysql $PACKAGE_FLAG
        ;;
    help)
        show_help
        exit 0
        ;;
    *)
        echo "Unknown option: $1"
        echo
        show_help
        exit 1
        ;;
esac

echo
echo "Build completed successfully!"
if [ -n "$PACKAGE_FLAG" ]; then
    echo "Distribution packages are in the 'dist' folder."
else
    echo "Executables are in the 'dist' folder."
fi
