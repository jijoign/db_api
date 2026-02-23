"""Linting checks for CI/CD pipeline."""
import sys
import subprocess


def run_flake8():
    """Run flake8 linting."""
    print("Running flake8...")
    try:
        result = subprocess.run(
            ['flake8', 'app/', '--max-line-length=100', '--extend-ignore=E203,W503'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("  ✓ flake8: No issues found")
            return True
        else:
            print(f"  ❌ flake8 found issues:\n{result.stdout}")
            return False
    except FileNotFoundError:
        print("  ⚠️  flake8 not installed, skipping...")
        return True


def run_isort_check():
    """Check import sorting."""
    print("Checking import sorting...")
    try:
        result = subprocess.run(
            ['isort', 'app/', '--check-only', '--profile', 'black'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("  ✓ isort: Imports are sorted correctly")
            return True
        else:
            print(f"  ❌ isort: Imports need sorting:\n{result.stdout}")
            return False
    except FileNotFoundError:
        print("  ⚠️  isort not installed, skipping...")
        return True


def run_black_check():
    """Check code formatting."""
    print("Checking code formatting...")
    try:
        result = subprocess.run(
            ['black', 'app/', '--check', '--line-length=100'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("  ✓ black: Code is formatted correctly")
            return True
        else:
            print(f"  ❌ black: Code needs formatting:\n{result.stdout}")
            return False
    except FileNotFoundError:
        print("  ⚠️  black not installed, skipping...")
        return True


def main():
    """Run all linting checks."""
    print("="*60)
    print("LINTING CHECKS")
    print("="*60 + "\n")
    
    results = []
    results.append(run_flake8())
    results.append(run_isort_check())
    results.append(run_black_check())
    
    print("\n" + "="*60)
    if all(results):
        print("✓ All linting checks passed!")
        return 0
    else:
        print("❌ Some linting checks failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
