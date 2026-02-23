# CI/CD Documentation

This directory contains all CI/CD scripts, tests, and Jenkins pipeline configuration for the REST API Library project.

## Setup

### Virtual Environment (Recommended)

All scripts will automatically detect and use a virtual environment if present in the `venv/` directory:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements-dev.txt
```

**Note:** If no virtual environment is detected, scripts will fall back to system Python.

## Directory Structure

```
ci/
├── Jenkinsfile                       # Main Jenkins pipeline
├── README.md                         # This file
├── run_tests.py                      # Master test runner
├── run_tests.sh                      # Unix test runner script
├── scripts/                          # Build and verification scripts
│   ├── build_executable.py          # Build executables for CI/CD
│   ├── verify_build.py              # Verify build artifacts
│   ├── lint_check.py                # Code linting checks
│   └── type_check.py                # Type checking with mypy
└── tests/                            # Test suites
    ├── test_installer.py            # Installer package tests
    ├── test_executable.py           # Executable functionality tests
    ├── test_database_integration.py # Database integration tests
    └── test_performance.py          # Performance and load tests
```

## Jenkins Pipeline

### Pipeline Features

- ✅ Automated build on commit
- ✅ Code quality checks (linting, type checking)
- ✅ Unit and integration tests
- ✅ Multi-database build support
- ✅ Build verification
- ✅ Artifact archiving
- ✅ Email notifications

### Pipeline Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| BRANCH_NAME | String | main | Branch to build from |
| BUILD_TYPE | Choice | all | Database type (all/sqlite/postgresql/mysql) |
| RUN_TESTS | Boolean | true | Run test suite |
| CREATE_PACKAGE | Boolean | false | Create distribution package |

### Setting Up Jenkins

1. **Create New Pipeline Job:**
   ```
   New Item → Pipeline → OK
   ```

2. **Configure SCM:**
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: [your-repo-url]
   - Script Path: ci/Jenkinsfile

3. **Configure Build Triggers:**
   - Poll SCM: `H/5 * * * *` (every 5 minutes)
   - Or use webhooks for instant builds

4. **Save and Build**

### Manual Jenkins Build

```bash
# Trigger build with parameters
curl -X POST "http://jenkins-server/job/rest-api-library/buildWithParameters" \
  --user username:token \
  --data "BRANCH_NAME=main&BUILD_TYPE=sqlite&RUN_TESTS=true&CREATE_PACKAGE=false"
```

## Test Suites

### 1. Build Verification (`verify_build.py`)

Verifies build artifacts are created correctly.

**Checks:**
- ✓ dist/ directory exists
- ✓ Executables are present
- ✓ File sizes are reasonable
- ✓ Generate checksums
- ✓ Documentation files present

**Run:**
```bash
python ci/scripts/verify_build.py
```

### 2. Installer Tests (`test_installer.py`)

Tests the installer package structure and contents.

**Tests:**
- Package structure validation
- Documentation presence
- Configuration files
- Startup scripts
- Checksum validation
- README content verification

**Run:**
```bash
python ci/tests/test_installer.py
```

### 3. Executable Tests (`test_executable.py`)

Tests the executable functionality.

**Tests:**
- Executable exists and is runnable
- Server starts successfully
- Health endpoint responds
- API documentation accessible
- CRUD operations work
- Database operations
- Clean shutdown

**Run:**
```bash
python ci/tests/test_executable.py
```

### 4. Database Integration Tests (`test_database_integration.py`)

Tests different database backends.

**Tests:**
- SQLite backend
- In-memory database
- Data persistence
- CRUD operations per database
- Database file creation

**Run:**
```bash
python ci/tests/test_database_integration.py
```

### 5. Performance Tests (`test_performance.py`)

Tests performance and load handling.

**Tests:**
- Response time benchmarks
- Concurrent request handling
- Bulk operations
- Pagination performance
- Memory footprint
- Startup time

**Run:**
```bash
python ci/tests/test_performance.py
```

## Running Tests

### Run All Tests

```bash
# Unix/Mac
./ci/run_tests.sh

# Or directly with Python
python ci/run_tests.py
```

### Run Specific Test Suite

```bash
# Build verification only
python ci/run_tests.py --suite build

# Installer tests only
python ci/run_tests.py --suite installer

# Executable tests
python ci/run_tests.py --suite executable

# Database integration
python ci/run_tests.py --suite database

# Performance tests
python ci/run_tests.py --suite performance
```

### Skip Slow Tests

```bash
# Skip database and performance tests (faster)
python ci/run_tests.py --skip-slow

# Or with script
./ci/run_tests.sh --skip-slow
```

### Verbose Output

```bash
python ci/run_tests.py --verbose
```

## Code Quality Checks

### Linting

```bash
python ci/scripts/lint_check.py
```

**Tools used:**
- flake8 - Style guide enforcement
- isort - Import sorting
- black - Code formatting

**Fix issues automatically:**
```bash
# Format code
black app/ --line-length=100

# Sort imports
isort app/ --profile black

# Check linting
flake8 app/ --max-line-length=100
```

### Type Checking

```bash
python ci/scripts/type_check.py
```

Uses mypy for static type checking.

## Build Scripts

### Build for CI/CD

```bash
# Build all databases
python ci/scripts/build_executable.py --type all

# Build SQLite only
python ci/scripts/build_executable.py --type sqlite

# Build and create distribution package
python ci/scripts/build_executable.py --type all --package

# Build specific database with package
python ci/scripts/build_executable.py --type sqlite --package
```

## Integration with CI/CD Platforms

### GitHub Actions

Example workflow:

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          python ci/run_tests.py
      - name: Build executable
        run: |
          python ci/scripts/build_executable.py --type all --package
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: executables
          path: dist/
```

### GitLab CI

Example `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - pip install -r requirements-dev.txt
    - python ci/run_tests.py
  
build:
  stage: build
  script:
    - pip install -r requirements-dev.txt
    - python ci/scripts/build_executable.py --type all --package
  artifacts:
    paths:
      - dist/
```

### Azure Pipelines

Example `azure-pipelines.yml`:

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.11'
  
  - script: |
      pip install -r requirements-dev.txt
    displayName: 'Install dependencies'
  
  - script: |
      python ci/run_tests.py
    displayName: 'Run tests'
  
  - script: |
      python ci/scripts/build_executable.py --type all --package
    displayName: 'Build executable'
  
  - task: PublishBuildArtifacts@1
    inputs:
      pathToPublish: 'dist'
      artifactName: 'executables'
```

## Test Reports

### Coverage Reports

Tests generate coverage reports in:
- `htmlcov/` - HTML coverage report
- `coverage.xml` - XML coverage report (for CI tools)

View coverage:
```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Open in browser (Unix)
open htmlcov/index.html

# Open in browser (Windows)
start htmlcov/index.html
```

### Test Results

JUnit XML test results are generated in:
- `test-results/` directory

## Troubleshooting

### Tests Fail Locally

1. **Check executable exists:**
   ```bash
   ls -l dist/
   ```

2. **Rebuild executable:**
   ```bash
   python build.py all
   ```

3. **Run tests with verbose output:**
   ```bash
   python ci/run_tests.py --verbose
   ```

### Port Already in Use

Tests use ports 8000-8200. If ports are busy:

```bash
# Find process using port
lsof -i :8000

# Kill the process or wait for tests to finish
```

### Permission Errors (Unix)

```bash
# Make scripts executable
chmod +x ci/run_tests.sh
chmod +x dist/rest-api-library
```

### Missing Dependencies

```bash
# Install all test dependencies
pip install -r requirements-dev.txt

# Specific dependencies
pip install pytest pytest-cov requests psutil
```

## Best Practices

1. **Run tests before committing:**
   ```bash
   python ci/run_tests.py --skip-slow
   ```

2. **Fix linting issues:**
   ```bash
   black app/
   isort app/
   ```

3. **Check build before pushing:**
   ```bash
   python build.py all
   python ci/scripts/verify_build.py
   ```

4. **Keep tests fast:**
   - Use `--skip-slow` during development
   - Run full suite in CI/CD

5. **Monitor test coverage:**
   - Aim for >80% coverage
   - Add tests for new features

## Continuous Improvement

### Adding New Tests

1. Create test file in `ci/tests/`
2. Follow existing test patterns
3. Add to `run_tests.py` if needed
4. Update this README

### Adding New Checks

1. Create script in `ci/scripts/`
2. Add to Jenkins pipeline if applicable
3. Document usage

## Support

For issues with CI/CD:
1. Check test output for errors
2. Review Jenkins console logs
3. Run tests locally with `--verbose`
4. Check this README for troubleshooting

## References

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [pytest Documentation](https://docs.pytest.org/)
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- Project README: [../README.md](../README.md)
- Build Documentation: [../BUILD.md](../BUILD.md)
