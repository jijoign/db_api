"""Clean up CI/CD artifacts and temporary files."""
import sys
import os
import shutil
from pathlib import Path


def clean_directory(directory, description):
    """Clean a directory."""
    path = Path(directory)
    if path.exists():
        try:
            shutil.rmtree(path)
            print(f"  ✓ Cleaned {description}: {directory}")
            return True
        except Exception as e:
            print(f"  ❌ Failed to clean {description}: {e}")
            return False
    else:
        print(f"  ⚠️  {description} not found: {directory}")
        return True


def clean_files(pattern, description):
    """Clean files matching pattern."""
    files = list(Path(".").rglob(pattern))
    count = len(files)
    
    if count == 0:
        print(f"  ⚠️  No {description} found")
        return True
    
    for file in files:
        try:
            file.unlink()
        except Exception as e:
            print(f"  ❌ Failed to delete {file}: {e}")
            return False
    
    print(f"  ✓ Cleaned {count} {description}")
    return True


def clean_ci_artifacts():
    """Clean CI/CD artifacts."""
    print("="*60)
    print("CI/CD CLEANUP")
    print("="*60)
    
    all_success = []
    
    # Clean build artifacts
    print("\n🧹 Cleaning build artifacts...")
    all_success.append(clean_directory("build", "build directory"))
    all_success.append(clean_directory("dist", "dist directory"))
    
    # Clean Python cache
    print("\n🧹 Cleaning Python cache...")
    all_success.append(clean_directory("__pycache__", "root __pycache__"))
    all_success.append(clean_files("**/__pycache__", "__pycache__ directories"))
    all_success.append(clean_files("**/*.pyc", "*.pyc files"))
    all_success.append(clean_files("**/*.pyo", "*.pyo files"))
    
    # Clean test artifacts
    print("\n🧹 Cleaning test artifacts...")
    all_success.append(clean_directory("htmlcov", "coverage HTML"))
    all_success.append(clean_directory(".pytest_cache", "pytest cache"))
    all_success.append(clean_directory("test-results", "test results"))
    all_success.append(clean_files("coverage.xml", "coverage XML"))
    all_success.append(clean_files(".coverage", "coverage data"))
    
    # Clean temporary files
    print("\n🧹 Cleaning temporary files...")
    all_success.append(clean_files("**/*.tmp", "temporary files"))
    all_success.append(clean_files("**/test.db", "test databases"))
    all_success.append(clean_files("**/*.log", "log files"))
    
    # Clean spec files (backup)
    print("\n🧹 Cleaning spec backups...")
    all_success.append(clean_files("*.spec.bak", "spec backups"))
    
    # Summary
    print("\n" + "="*60)
    if all(all_success):
        print("✅ Cleanup completed successfully!")
    else:
        print("⚠️  Cleanup completed with warnings")
    print("="*60)
    
    return 0 if all(all_success) else 1


if __name__ == '__main__':
    sys.exit(clean_ci_artifacts())
