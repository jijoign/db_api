"""Master test runner for all CI/CD tests."""
import sys
import os
import subprocess
import argparse
from pathlib import Path


class TestRunner:
    """Run all CI/CD tests."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {}
        self.ci_dir = Path("ci")
    
    def run_test_suite(self, name, script_path):
        """Run a single test suite."""
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print(f"{'='*60}")
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=not self.verbose,
                text=True,
                check=False
            )
            
            success = result.returncode == 0
            self.results[name] = {
                'success': success,
                'returncode': result.returncode
            }
            
            if not self.verbose and result.stdout:
                print(result.stdout)
            
            if success:
                print(f"\n✓ {name} PASSED")
            else:
                print(f"\n❌ {name} FAILED")
                if result.stderr:
                    print(f"Error output:\n{result.stderr}")
            
            return success
            
        except Exception as e:
            print(f"\n❌ {name} ERROR: {e}")
            self.results[name] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def run_all(self, skip_slow=False):
        """Run all test suites."""
        print("="*60)
        print("CI/CD TEST SUITE RUNNER")
        print("="*60)
        
        # Define test suites
        suites = [
            ("Build Verification", self.ci_dir / "scripts" / "verify_build.py"),
            ("Installer Tests", self.ci_dir / "tests" / "test_installer.py"),
            ("Executable Tests", self.ci_dir / "tests" / "test_executable.py"),
        ]
        
        if not skip_slow:
            suites.extend([
                ("Database Integration", self.ci_dir / "tests" / "test_database_integration.py"),
                ("Performance Tests", self.ci_dir / "tests" / "test_performance.py"),
            ])
        
        # Run each suite
        all_passed = True
        for name, script in suites:
            if not script.exists():
                print(f"\n⚠️  {name} script not found: {script}")
                continue
            
            passed = self.run_test_suite(name, script)
            all_passed = all_passed and passed
        
        # Print summary
        self.print_summary()
        
        return 0 if all_passed else 1
    
    def print_summary(self):
        """Print test results summary."""
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results.values() if r['success'])
        failed = total - passed
        
        for name, result in self.results.items():
            status = "✓ PASS" if result['success'] else "❌ FAIL"
            print(f"{status:10} {name}")
        
        print(f"\n{'='*60}")
        print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
        print(f"{'='*60}")
        
        if passed == total:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {failed} test suite(s) failed")


def main():
    parser = argparse.ArgumentParser(description='Run CI/CD test suites')
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--skip-slow',
        action='store_true',
        help='Skip slow tests (database, performance)'
    )
    parser.add_argument(
        '--suite',
        choices=['build', 'installer', 'executable', 'database', 'performance', 'all'],
        default='all',
        help='Run specific test suite'
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose)
    
    if args.suite == 'all':
        return runner.run_all(skip_slow=args.skip_slow)
    else:
        # Run specific suite
        suite_map = {
            'build': ('Build Verification', 'ci/scripts/verify_build.py'),
            'installer': ('Installer Tests', 'ci/tests/test_installer.py'),
            'executable': ('Executable Tests', 'ci/tests/test_executable.py'),
            'database': ('Database Integration', 'ci/tests/test_database_integration.py'),
            'performance': ('Performance Tests', 'ci/tests/test_performance.py'),
        }
        
        name, script_path = suite_map[args.suite]
        success = runner.run_test_suite(name, Path(script_path))
        runner.print_summary()
        return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
