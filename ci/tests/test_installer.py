"""Integration tests for the installer package."""
import sys
import os
import tempfile
import shutil
import zipfile
from pathlib import Path
import unittest


class InstallerTests(unittest.TestCase):
    """Test cases for the installer package."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.dist_dir = Path("dist")
        cls.temp_dir = None
    
    def setUp(self):
        """Set up each test."""
        self.temp_dir = tempfile.mkdtemp(prefix="installer_test_")
    
    def tearDown(self):
        """Clean up after each test."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_01_dist_directory_exists(self):
        """Test that dist directory exists."""
        self.assertTrue(
            self.dist_dir.exists(),
            "dist/ directory not found"
        )
        print("  ✓ dist/ directory exists")
    
    def test_02_executable_present(self):
        """Test that at least one executable is present."""
        if sys.platform == 'win32':
            executables = list(self.dist_dir.glob("*.exe"))
        else:
            executables = [
                f for f in self.dist_dir.iterdir()
                if f.is_file() and 'rest-api-library' in f.name
            ]
        
        self.assertGreater(
            len(executables), 0,
            "No executables found in dist/"
        )
        print(f"  ✓ Found {len(executables)} executable(s)")
    
    def test_03_env_example_exists(self):
        """Test that .env.example file exists."""
        env_example = Path(".env.example")
        self.assertTrue(
            env_example.exists(),
            ".env.example file not found"
        )
        
        # Verify it's not empty
        content = env_example.read_text()
        self.assertGreater(len(content), 0, ".env.example is empty")
        self.assertIn('DATABASE_URL', content, "Missing DATABASE_URL in .env.example")
        print("  ✓ .env.example exists and has content")
    
    def test_04_documentation_exists(self):
        """Test that required documentation exists."""
        required_docs = [
            "README.md",
            "QUICKSTART.md",
            "BUILD.md"
        ]
        
        for doc in required_docs:
            doc_path = Path(doc)
            self.assertTrue(
                doc_path.exists(),
                f"Missing documentation: {doc}"
            )
            
            # Verify not empty
            content = doc_path.read_text()
            self.assertGreater(
                len(content), 100,
                f"{doc} is too small or empty"
            )
        
        print(f"  ✓ All {len(required_docs)} documentation files present")
    
    def test_05_package_structure(self):
        """Test package archive structure if it exists."""
        # Look for zip packages
        packages = list(self.dist_dir.glob("*.zip"))
        
        if not packages:
            print("  ⚠️  No .zip packages found, skipping")
            return
        
        package = packages[0]
        print(f"  Testing package: {package.name}")
        
        # Extract and verify structure
        extract_dir = Path(self.temp_dir) / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(package, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Check for required files in extracted package
        extracted_files = list(extract_dir.rglob("*"))
        file_names = [f.name for f in extracted_files]
        
        # Should have at least executable and docs
        has_exe = any('rest-api-library' in name for name in file_names)
        has_readme = 'README.md' in file_names
        has_env = '.env' in file_names or '.env.example' in file_names
        
        self.assertTrue(has_exe, "Package missing executable")
        self.assertTrue(has_readme, "Package missing README.md")
        self.assertTrue(has_env, "Package missing .env file")
        
        print(f"  ✓ Package structure verified ({len(extracted_files)} files)")
    
    def test_06_checksums_file(self):
        """Test that checksums file exists and is valid."""
        checksums_file = self.dist_dir / "checksums.txt"
        
        if not checksums_file.exists():
            print("  ⚠️  checksums.txt not found, skipping")
            return
        
        content = checksums_file.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        self.assertGreater(
            len(lines), 0,
            "checksums.txt is empty"
        )
        
        # Verify format (SHA256 hash  filename)
        for line in lines:
            parts = line.split()
            self.assertEqual(
                len(parts), 2,
                f"Invalid checksum line: {line}"
            )
            self.assertEqual(
                len(parts[0]), 64,
                f"Invalid SHA256 hash: {parts[0]}"
            )
        
        print(f"  ✓ Checksums file valid ({len(lines)} entries)")
    
    def test_07_executable_filenames(self):
        """Test that executables have correct naming."""
        if sys.platform == 'win32':
            executables = list(self.dist_dir.glob("*.exe"))
        else:
            executables = [
                f for f in self.dist_dir.iterdir()
                if f.is_file() and 'rest-api-library' in f.name
            ]
        
        for exe in executables:
            # Should contain 'rest-api-library' in name
            self.assertIn(
                'rest-api-library',
                exe.name.lower(),
                f"Unexpected executable name: {exe.name}"
            )
        
        print(f"  ✓ All {len(executables)} executable names valid")
    
    def test_08_startup_scripts(self):
        """Test for startup scripts if package exists."""
        packages = list(self.dist_dir.glob("*.zip"))
        
        if not packages:
            print("  ⚠️  No packages found, skipping startup script test")
            return
        
        package = packages[0]
        extract_dir = Path(self.temp_dir) / "startup_test"
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(package, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Check for startup scripts
        all_files = list(extract_dir.rglob("*"))
        file_names = [f.name for f in all_files]
        
        has_sh = 'start.sh' in file_names
        
        # Should have Unix startup script
        self.assertTrue(
            has_sh,
            \"Package missing startup script (start.sh)\"
        )
        
        if has_sh:
            print("  ✓ Unix startup script (start.sh) present")
    
    def test_09_readme_content(self):
        """Test that README has essential information."""
        readme = Path("README.md")
        content = readme.read_text().lower()
        
        essential_keywords = [
            'installation',
            'api',
            'database',
            'usage',
            'endpoint'
        ]
        
        for keyword in essential_keywords:
            self.assertIn(
                keyword,
                content,
                f"README missing essential keyword: {keyword}"
            )
        
        print(f"  ✓ README contains all essential information")
    
    def test_10_config_file_validity(self):
        """Test that config file is valid Python."""
        config_file = Path("config.py")
        self.assertTrue(config_file.exists(), "config.py not found")
        
        # Try to compile it
        content = config_file.read_text()
        try:
            compile(content, 'config.py', 'exec')
            print("  ✓ config.py is valid Python")
        except SyntaxError as e:
            self.fail(f"config.py has syntax errors: {e}")


def run_tests():
    """Run all installer tests."""
    print("="*60)
    print("INSTALLER INTEGRATION TESTS")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(InstallerTests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
