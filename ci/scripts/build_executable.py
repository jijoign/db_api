"""Build executable script for CI/CD pipeline."""
import sys
import subprocess
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Build executable for CI/CD')
    parser.add_argument('--type', choices=['all', 'sqlite', 'postgresql', 'mysql'], 
                       default='all', help='Build type')
    parser.add_argument('--package', action='store_true',
                       help='Create distribution package after build')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"CI/CD Build - {args.type.upper()}")
    if args.package:
        print("Package: Yes")
    print(f"{'='*60}\n")
    
    # Build command
    cmd = ['python', 'build.py', args.type]
    if args.package:
        cmd.append('--package')
    
    print(f"Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("\n✓ Build completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed!")
        print(f"Error: {e.stderr}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
