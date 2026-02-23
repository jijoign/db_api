"""Quick CI/CD setup verification script."""
import sys
from pathlib import Path


def check_file_exists(file_path, description):
    """Check if a file exists."""
    path = Path(file_path)
    if path.exists():
        print(f"  ✓ {description}: {file_path}")
        return True
    else:
        print(f"  ❌ {description} missing: {file_path}")
        return False


def check_directory_exists(dir_path, description):
    """Check if a directory exists."""
    path = Path(dir_path)
    if path.exists() and path.is_dir():
        file_count = len(list(path.iterdir()))
        print(f"  ✓ {description}: {dir_path} ({file_count} files)")
        return True
    else:
        print(f"  ❌ {description} missing: {dir_path}")
        return False


def verify_ci_setup():
    """Verify CI/CD setup is complete."""
    print("="*60)
    print("CI/CD SETUP VERIFICATION")
    print("="*60)
    
    all_checks = []
    
    # Check directories
    print("\n📁 Checking directories...")
    all_checks.append(check_directory_exists("ci", "CI directory"))
    all_checks.append(check_directory_exists("ci/scripts", "Scripts directory"))
    all_checks.append(check_directory_exists("ci/tests", "Tests directory"))
    
    # Check Jenkins files
    print("\n🔧 Checking Jenkins files...")
    all_checks.append(check_file_exists("ci/Jenkinsfile", "Jenkins pipeline"))
    
    # Check scripts
    print("\n📜 Checking CI scripts...")
    scripts = [
        ("ci/scripts/build_executable.py", "Build script"),
        ("ci/scripts/verify_build.py", "Verification script"),
        ("ci/scripts/lint_check.py", "Linting script"),
        ("ci/scripts/type_check.py", "Type check script"),
    ]
    
    for script_path, description in scripts:
        all_checks.append(check_file_exists(script_path, description))
    
    # Check test files
    print("\n🧪 Checking test files...")
    tests = [
        ("ci/tests/test_installer.py", "Installer tests"),
        ("ci/tests/test_executable.py", "Executable tests"),
        ("ci/tests/test_database_integration.py", "Database tests"),
        ("ci/tests/test_performance.py", "Performance tests"),
    ]
    
    for test_path, description in tests:
        all_checks.append(check_file_exists(test_path, description))
    
    # Check runners
    print("\n🏃 Checking test runners...")
    all_checks.append(check_file_exists("ci/run_tests.py", "Master test runner"))
    all_checks.append(check_file_exists("ci/run_tests.sh", "Unix test runner"))

    
    # Check documentation
    print("\n📚 Checking documentation...")
    all_checks.append(check_file_exists("ci/README.md", "CI/CD README"))
    
    # Check build scripts
    print("\n🔨 Checking build scripts...")
    all_checks.append(check_file_exists("build.py", "Database build script"))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    total = len(all_checks)
    passed = sum(all_checks)
    failed = total - passed
    
    print(f"\nTotal checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if all(all_checks):
        print("\n✅ CI/CD setup is complete!")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements-dev.txt")
        print("  2. Build executable: python build.py all")
        print("  3. Run tests: python ci/run_tests.py")
        return 0
    else:
        print("\n❌ CI/CD setup is incomplete!")
        print("\nPlease ensure all required files are present.")
        return 1


if __name__ == '__main__':
    sys.exit(verify_ci_setup())
