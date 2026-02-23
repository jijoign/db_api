# CI/CD Quick Reference

Quick commands for common CI/CD tasks. See [README.md](README.md) for detailed documentation.

## Running Tests

```bash
# All tests
python ci/run_tests.py

# Specific suite
python ci/run_tests.py --suite build
python ci/run_tests.py --suite installer
python ci/run_tests.py --suite executable

# Skip slow tests
python ci/run_tests.py --skip-slow
```

## Jenkins Build

```bash
# Trigger build with parameters
curl -X POST "http://jenkins/job/rest-api-library/buildWithParameters" \
  --user username:token \
  --data "BRANCH_NAME=main&BUILD_TYPE=all&RUN_TESTS=true"
```

**Parameters:**
- BRANCH_NAME: main (or any branch)
- BUILD_TYPE: all, sqlite, postgresql, mysql
- BUILD_MODE: onefile, onedir
- RUN_TESTS: true/false
- CREATE_PACKAGE: true/false

## Build Executable

```bash
# Build all databases
python ci/scripts/build_executable.py --type all --mode onefile

# Build specific database
python ci/scripts/build_executable.py --type sqlite --mode onefile
```

## Code Quality

```bash
# Linting
python ci/scripts/lint_check.py

# Type checking
python ci/scripts/type_check.py

# Verify build
python ci/scripts/verify_build.py
```

## Common Workflows

**Before commit:**
```bash
python ci/scripts/lint_check.py
python ci/run_tests.py --skip-slow
```

**Full validation:**
```bash
python ci/run_tests.py
python build.py
python ci/scripts/verify_build.py
```

## File Locations

- **Pipeline**: `ci/Jenkinsfile`
- **Tests**: `ci/tests/`
- **Scripts**: `ci/scripts/`
- **Artifacts**: `dist/`, `build/`
