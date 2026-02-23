@echo off
REM Quick build script for Windows

echo ========================================
echo REST API Library - Build Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check for arguments
if "%1"=="" (
    echo Building default executable...
    python build.py
    goto :end
)

if "%1"=="clean" (
    echo Cleaning build directories...
    if exist build rmdir /s /q build
    if exist dist rmdir /s /q dist
    echo Clean completed!
    goto :end
)

if "%1"=="sqlite" (
    echo Building SQLite version...
    python build_databases.py sqlite
    goto :end
)

if "%1"=="postgresql" (
    echo Building PostgreSQL version...
    python build_databases.py postgresql
    goto :end
)

if "%1"=="mysql" (
    echo Building MySQL version...
    python build_databases.py mysql
    goto :end
)

if "%1"=="all" (
    echo Building all database versions...
    python build_databases.py all
    goto :end
)

if "%1"=="package" (
    echo Building distribution package...
    python build.py --package
    goto :end
)

if "%1"=="help" (
    goto :help
)

echo Unknown option: %1
echo.

:help
echo Usage: build.bat [option]
echo.
echo Options:
echo   (none)      - Build default executable with all databases
echo   clean       - Clean build directories
echo   sqlite      - Build SQLite-only version
echo   postgresql  - Build PostgreSQL version
echo   mysql       - Build MySQL version
echo   all         - Build all database-specific versions
echo   package     - Build and create distribution package
echo   help        - Show this help message
echo.
echo Examples:
echo   build.bat              Build default
echo   build.bat sqlite       Build SQLite version
echo   build.bat package      Create distribution
echo.
goto :end

:end
echo.
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
) else (
    echo Build completed successfully!
    echo Executables are in the 'dist' folder.
    pause
)
