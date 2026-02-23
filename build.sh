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

# Function to show help
show_help() {
    echo "Usage: ./build.sh [option]"
    echo
    echo "Options:"
    echo "  (none)      - Build default executable with all databases"
    echo "  clean       - Clean build directories"
    echo "  sqlite      - Build SQLite-only version"
    echo "  postgresql  - Build PostgreSQL version"
    echo "  mysql       - Build MySQL version"
    echo "  all         - Build all database-specific versions"
    echo "  package     - Build and create distribution package"
    echo "  help        - Show this help message"
    echo
    echo "Examples:"
    echo "  ./build.sh              Build default"
    echo "  ./build.sh sqlite       Build SQLite version"
    echo "  ./build.sh package      Create distribution"
    echo
}

# Parse arguments
case "${1:-default}" in
    default)
        echo "Building default executable..."
        python3 build.py
        ;;
    clean)
        echo "Cleaning build directories..."
        rm -rf build dist *.spec
        echo "Clean completed!"
        ;;
    sqlite)
        echo "Building SQLite version..."
        python3 build_databases.py sqlite
        ;;
    postgresql)
        echo "Building PostgreSQL version..."
        python3 build_databases.py postgresql
        ;;
    mysql)
        echo "Building MySQL version..."
        python3 build_databases.py mysql
        ;;
    all)
        echo "Building all database versions..."
        python3 build_databases.py all
        ;;
    package)
        echo "Building distribution package..."
        python3 build.py --package
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
echo "Executables are in the 'dist' folder."
