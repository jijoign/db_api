@echo off
REM CI/CD test runner script for Windows

echo ========================================
echo CI/CD Test Runner
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    exit /b 1
)

REM Parse arguments
set SKIP_SLOW=
set VERBOSE=
set SUITE=all

:parse_args
if "%1"=="" goto :run_tests
if "%1"=="--skip-slow" (
    set SKIP_SLOW=--skip-slow
    shift
    goto :parse_args
)
if "%1"=="-v" (
    set VERBOSE=--verbose
    shift
    goto :parse_args
)
if "%1"=="--verbose" (
    set VERBOSE=--verbose
    shift
    goto :parse_args
)
if "%1"=="--suite" (
    set SUITE=%2
    shift
    shift
    goto :parse_args
)
echo Unknown option: %1
exit /b 1

:run_tests
REM Build command
set CMD=python ci\run_tests.py --suite %SUITE% %SKIP_SLOW% %VERBOSE%

echo Running: %CMD%
echo.
%CMD%

exit /b %ERRORLEVEL%
