"""Database integration tests for different backends."""
import sys
import os
import subprocess
import tempfile
import time
from pathlib import Path
import unittest
import requests


class DatabaseIntegrationTests(unittest.TestCase):
    """Integration tests for different database backends."""
    
    def setUp(self):
        """Set up test environment."""
        self.dist_dir = Path("dist")
        self.executable = self._find_executable()
        self.process = None
        self.base_url = "http://localhost:8100"
        self.test_port = 8100
        self.temp_dir = tempfile.mkdtemp(prefix="db_test_")
    
    def tearDown(self):
        """Clean up after test."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        # Clean up temp directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _find_executable(self):
        """Find executable in dist folder."""
        if sys.platform == 'win32':
            executables = list(self.dist_dir.glob("rest-api-library*.exe"))
        else:
            # On Unix, executables have no extension
            executables = [
                f for f in self.dist_dir.iterdir()
                if f.is_file() and 'rest-api-library' in f.name 
                and not f.suffix  # Exclude files with extensions (.txt, .md, etc.)
            ]
        
        if not executables:
            raise FileNotFoundError("No executable found")
        
        return executables[0]
    
    def _start_with_config(self, db_url, timeout=15):
        """Start executable with specific database configuration."""
        env_content = f"""
DATABASE_URL={db_url}
HOST=127.0.0.1
PORT={self.test_port}
DEBUG=True
"""
        
        # Create .env in temp directory
        env_file = Path(self.temp_dir) / ".env"
        env_file.write_text(env_content)
        
        # Copy executable to temp dir for testing
        import shutil
        temp_exe = Path(self.temp_dir) / self.executable.name
        shutil.copy2(self.executable, temp_exe)
        
        # Make executable on Unix
        if sys.platform != 'win32':
            os.chmod(temp_exe, 0o755)
        
        # Start process (use relative path since cwd is temp_dir)
        self.process = subprocess.Popen(
            [f"./{temp_exe.name}"],
            cwd=self.temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for startup
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/health", timeout=1)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                time.sleep(0.5)
        
        return False
    
    def _test_crud_operations(self):
        """Test basic CRUD operations."""
        # Create user
        user_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "full_name": "Integration Test User"
        }
        
        response = requests.post(
            f"{self.base_url}/api/users/",
            json=user_data
        )
        self.assertEqual(response.status_code, 201)
        user_id = response.json()['id']
        
        # Read user
        response = requests.get(f"{self.base_url}/api/users/{user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], user_data['username'])
        
        # Update user
        update_data = {"full_name": "Updated Name"}
        response = requests.put(
            f"{self.base_url}/api/users/{user_id}",
            json=update_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['full_name'], "Updated Name")
        
        # Delete user
        response = requests.delete(f"{self.base_url}/api/users/{user_id}")
        self.assertEqual(response.status_code, 200)
        
        # Verify deletion
        response = requests.get(f"{self.base_url}/api/users/{user_id}")
        self.assertEqual(response.status_code, 404)
        
        return True
    
    def test_01_sqlite_backend(self):
        """Test with SQLite backend."""
        print("\n  Testing SQLite backend...")
        
        db_path = Path(self.temp_dir) / "test.db"
        db_url = f"sqlite:///{db_path}"
        
        started = self._start_with_config(db_url)
        self.assertTrue(started, "Failed to start with SQLite")
        
        # Test CRUD operations
        self._test_crud_operations()
        
        # Verify database file was created
        self.assertTrue(db_path.exists(), "SQLite database file not created")
        
        print("    ✓ SQLite backend working")
    
    def test_02_sqlite_in_memory(self):
        """Test with in-memory SQLite."""
        print("\n  Testing in-memory SQLite...")
        
        db_url = "sqlite:///:memory:"
        started = self._start_with_config(db_url)
        self.assertTrue(started, "Failed to start with in-memory SQLite")
        
        # Test basic operations
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        print("    ✓ In-memory SQLite working")
    
    def test_03_database_persistence(self):
        """Test data persistence across restarts."""
        print("\n  Testing database persistence...")
        
        db_path = Path(self.temp_dir) / "persist.db"
        db_url = f"sqlite:///{db_path}"
        
        # First run - create data
        started = self._start_with_config(db_url)
        self.assertTrue(started)
        
        user_data = {
            "username": "persistent_user",
            "email": "persist@example.com",
            "full_name": "Persistent User"
        }
        
        response = requests.post(
            f"{self.base_url}/api/users/",
            json=user_data
        )
        self.assertEqual(response.status_code, 201)
        user_id = response.json()['id']
        
        # Stop executable
        self.process.terminate()
        self.process.wait(timeout=5)
        self.process = None
        
        time.sleep(2)
        
        # Second run - verify data persists
        started = self._start_with_config(db_url)
        self.assertTrue(started)
        
        response = requests.get(f"{self.base_url}/api/users/{user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], user_data['username'])
        
        print("    ✓ Data persistence verified")


def run_tests():
    """Run database integration tests."""
    print("="*60)
    print("DATABASE INTEGRATION TESTS")
    print("="*60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(DatabaseIntegrationTests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
