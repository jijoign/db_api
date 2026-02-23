# CI/CD Quick Reference

## Setup Verification

```bash
# Verify CI/CD setup is complete
python ci/verify_setup.py
```

## Running Tests

### All Tests
```bash
# Full test suite
python ci/run_tests.py

# Or using platform scripts
./ci/run_tests.sh          # Unix/Mac
ci\run_tests.bat           # Windows
```

### Specific Test Suites
```bash
# Build verification
python ci/run_tests.py --suite build

# Installer tests
python ci/run_tests.py --suite installer

# Executable tests
python ci/run_tests.py --suite executable

# Database integration
python ci/run_tests.py --suite database

# Performance tests
python ci/run_tests.py --suite performance
```

### Test Options
```bash
# Skip slow tests (database, performance)
python ci/run_tests.py --skip-slow

# Verbose output
python ci/run_tests.py --verbose

# Combined
python ci/run_tests.py --skip-slow --verbose
```

## Jenkins Pipeline

### Trigger Build
```bash
# Via Jenkins UI
Build with Parameters → Select options → Build

# Via API
curl -X POST "http://jenkins/job/rest-api-library/buildWithParameters" \
  --user username:token \
  --data "BRANCH_NAME=main&BUILD_TYPE=all&RUN_TESTS=true"
```

### Pipeline Parameters
- **BRANCH_NAME**: main (or any branch name)
- **BUILD_TYPE**: all, sqlite, postgresql, mysql
- **BUILD_MODE**: onefile, onedir
- **RUN_TESTS**: true/false
- **CREATE_PACKAGE**: true/false

## Build & Verification

### Build Executable
```bash
# Standard build
python ci/scripts/build_executable.py --type all --mode onefile

# Database-specific
python ci/scripts/build_executable.py --type sqlite --mode onefile
```

### Verify Build
```bash
# Verify artifacts
python ci/scripts/verify_build.py
```

## Code Quality

### Linting
```bash
# Check code quality
python ci/scripts/lint_check.py

# Auto-fix issues
black app/ --line-length=100
isort app/ --profile black
```

### Type Checking
```bash
python ci/scripts/type_check.py
```

## Cleanup

```bash
# Clean all CI/CD artifacts
python ci/clean_artifacts.py
```

## Test Coverage

### Generate Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html

# View report
open htmlcov/index.html          # Mac
xdg-open htmlcov/index.html      # Linux
start htmlcov/index.html         # Windows
```

## Common Workflows

### Before Commit
```bash
# 1. Run linting
python ci/scripts/lint_check.py

# 2. Run quick tests
python ci/run_tests.py --skip-slow

# 3. Commit if all pass
git commit -m "Your message"
```

### Full Validation
```bash
# 1. Clean previous builds
python ci/clean_artifacts.py

# 2. Build executable
python build.py

# 3. Run all tests
python ci/run_tests.py

# 4. Verify build
python ci/scripts/verify_build.py
```

### CI/CD Setup (New Environment)
```bash
# 1. Verify setup
python ci/verify_setup.py

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Run initial tests
python ci/run_tests.py --skip-slow

# 4. Build
python build.py
```

## Troubleshooting

### Tests Fail
```bash
# Run with verbose output
python ci/run_tests.py --verbose --suite [failing-suite]

# Check logs
cat ci/tests/*.log  # If log files exist
```

### Port Conflicts
```bash
# Find processes using test ports (8000-8200)
lsof -i :8000           # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or wait for tests to finish
```

### Build Issues
```bash
# Clean and rebuild
python ci/clean_artifacts.py
python build.py
python ci/scripts/verify_build.py
```

## File Locations

- **Tests**: `ci/tests/`
- **Scripts**: `ci/scripts/`
- **Pipeline**: `ci/Jenkinsfile`
- **Test Results**: `test-results/`
- **Coverage**: `htmlcov/`
- **Build Artifacts**: `dist/`

## Exit Codes

- **0**: Success
- **1**: Failure
- Check return codes in scripts for automation

## Quick Links

- [Full CI/CD Documentation](README.md)
- [Project README](../README.md)
- [Build Documentation](../BUILD.md)
- [Deployment Guide](../DEPLOYMENT.md)
