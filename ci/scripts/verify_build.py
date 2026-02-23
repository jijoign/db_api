"""Verify build artifacts and integrity."""
import sys
import os
from pathlib import Path
import hashlib


class BuildVerifier:
    """Verify build artifacts."""
    
    def __init__(self):
        self.dist_dir = Path("dist")
        self.errors = []
        self.warnings = []
        # Extensions to exclude from executable checks
        self.exclude_exts = {'.txt', '.md', '.spec', '.toc', '.log', '.xml', '.json'}
    
    def verify_directory_exists(self):
        """Check if dist directory exists."""
        print("Checking dist directory...")
        if not self.dist_dir.exists():
            self.errors.append("dist/ directory not found")
            return False
        print("  ✓ dist/ directory exists")
        return True
    
    def verify_executables_exist(self):
        """Check if executables are built."""
        print("\nChecking for executables...")
        
        # Look for actual executable files (not docs or artifacts)
        if sys.platform == 'win32':
            executables = list(self.dist_dir.glob("*.exe"))
        else:
            # On Unix, look for files without extension containing 'rest-api-library'
            executables = [
                f for f in self.dist_dir.iterdir()
                if f.is_file() and 'rest-api-library' in f.name
                and not f.suffix  # No extension = executable on Unix
            ]
        
        if not executables:
            self.errors.append("No executables found in dist/")
            return False
        
        for exe in executables:
            print(f"  ✓ Found: {exe.name}")
        
        return True
    
    def verify_file_sizes(self):
        """Check if executables have reasonable sizes."""
        print("\nChecking file sizes...")
        
        min_size = 10 * 1024 * 1024  # 10 MB minimum
        max_size = 200 * 1024 * 1024  # 200 MB maximum
        
        if sys.platform == 'win32':
            executables = list(self.dist_dir.glob("*.exe"))
        else:
            # Only check actual executables (no extension on Unix)
            executables = [
                f for f in self.dist_dir.iterdir()
                if f.is_file() and 'rest-api-library' in f.name
                and not f.suffix  # Exclude .txt, .md, etc.
            ]
        
        for exe in executables:
            size = exe.stat().st_size
            size_mb = size / (1024 * 1024)
            
            if size < min_size:
                self.warnings.append(
                    f"{exe.name} is only {size_mb:.1f} MB (expected > 10 MB)"
                )
            elif size > max_size:
                self.warnings.append(
                    f"{exe.name} is {size_mb:.1f} MB (expected < 200 MB)"
                )
            else:
                print(f"  ✓ {exe.name}: {size_mb:.1f} MB")
        
        return True
    
    def verify_checksums(self):
        """Generate checksums for verification."""
        print("\nGenerating checksums...")
        
        checksum_file = self.dist_dir / "checksums.txt"
        
        if sys.platform == 'win32':
            files = list(self.dist_dir.glob("*.exe"))
        else:
            # Only checksum actual executables
            files = [
                f for f in self.dist_dir.iterdir()
                if f.is_file() and 'rest-api-library' in f.name
                and not f.suffix  # Exclude .txt, .md, etc.
            ]
        
        checksums = []
        for file in files:
            sha256 = hashlib.sha256()
            with open(file, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            
            checksum = sha256.hexdigest()
            checksums.append(f"{checksum}  {file.name}")
            print(f"  ✓ {file.name}: {checksum[:16]}...")
        
        # Write checksums file
        with open(checksum_file, 'w') as f:
            f.write('\n'.join(checksums))
        
        print(f"\n  Checksums saved to: {checksum_file}")
        return True
    
    def verify_documentation_files(self):
        """Check if required documentation exists."""
        print("\nChecking documentation files...")
        
        required_docs = [
            "README.md",
            "QUICKSTART.md",
            "BUILD.md",
            ".env.example"
        ]
        
        for doc in required_docs:
            if not Path(doc).exists():
                self.warnings.append(f"Missing documentation: {doc}")
            else:
                print(f"  ✓ {doc}")
        
        return True
    
    def run(self):
        """Run all verification checks."""
        print("="*60)
        print("BUILD VERIFICATION")
        print("="*60)
        
        # Run checks
        self.verify_directory_exists()
        self.verify_executables_exist()
        self.verify_file_sizes()
        self.verify_checksums()
        self.verify_documentation_files()
        
        # Report results
        print("\n" + "="*60)
        print("VERIFICATION RESULTS")
        print("="*60)
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
            print("\n❌ Verification FAILED!")
            return 1
        else:
            print("\n✓ All checks passed!")
            if self.warnings:
                print("  (with warnings)")
            return 0


def main():
    verifier = BuildVerifier()
    return verifier.run()


if __name__ == '__main__':
    sys.exit(main())
