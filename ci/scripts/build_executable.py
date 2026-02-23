"""Build executable script for CI/CD pipeline."""
import sys
import subprocess
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Build executable for CI/CD')
    parser.add_argument('--type', choices=['all', 'sqlite', 'postgresql', 'mysql'], 
                       default='all', help='Build type')
    parser.add_argument('--mode', choices=['onefile', 'onedir'], 
                       default='onefile', help='Build mode')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"CI/CD Build - {args.type.upper()} ({args.mode})")
    print(f"{'='*60}\n")
    
    # Build command
    if args.type == 'all':
        cmd = ['python', 'build.py', '--mode', args.mode]
    else:
        cmd = ['python', 'build_databases.py', args.type]
    
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
