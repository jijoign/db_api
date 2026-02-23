"""Type checking for CI/CD pipeline."""
import sys
import subprocess


def run_mypy():
    """Run mypy type checking."""
    print("="*60)
    print("TYPE CHECKING")
    print("="*60 + "\n")
    
    print("Running mypy...")
    try:
        result = subprocess.run(
            ['mypy', 'app/', '--ignore-missing-imports', '--no-strict-optional'],
            capture_output=True,
            text=True,
            check=False
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n✓ mypy: No type errors found")
            return 0
        else:
            print("\n❌ mypy: Type errors found")
            return 1
            
    except FileNotFoundError:
        print("  ⚠️  mypy not installed, skipping type checking...")
        return 0


def main():
    return run_mypy()


if __name__ == '__main__':
    sys.exit(main())
