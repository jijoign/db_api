#!/usr/bin/env python3
"""
Test runner that generates JUnit XML reports for Jenkins.
"""
import sys
import os
import unittest
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_test_module(test_module_name, output_dir='test-results'):
    """
    Run a test module and generate JUnit XML output.
    
    Args:
        test_module_name: Name of the test module (e.g., 'test_executable')
        output_dir: Directory to save XML results
    
    Returns:
        bool: True if all tests passed, False otherwise
    """
    # Import the test module
    try:
        test_module = __import__(test_module_name)
    except ImportError as e:
        print(f"❌ Failed to import {test_module_name}: {e}")
        return False
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_module)
    
    # Try to use xmlrunner if available, otherwise use standard runner
    try:
        import xmlrunner
        xml_file = output_path / f"{test_module_name}.xml"
        runner = xmlrunner.XMLTestRunner(
            output=str(output_path),
            verbosity=2,
            stream=sys.stdout
        )
        result = runner.run(suite)
    except ImportError:
        # Fallback to standard text runner
        print("⚠️  xmlrunner not available, using standard text runner")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run tests with JUnit XML output')
    parser.add_argument('test_module', help='Test module to run (without .py extension)')
    parser.add_argument('--output-dir', '-o', default='test-results',
                       help='Directory for XML output (default: test-results)')
    
    args = parser.parse_args()
    
    # Run the test
    success = run_test_module(args.test_module, args.output_dir)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
