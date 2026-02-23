"""Test cases for the executable installer."""
import sys
import os
import time
import subprocess
import tempfile
import shutil
import requests
from pathlib import Path
import unittest


class ExecutableTests(unittest.TestCase):
    """Test cases for the built executable."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.dist_dir = Path("dist/rest-api-library-sqlite-1.0.0")
        cls.executable = cls._find_executable()
        cls.process = None
        cls.base_url = "http://localhost:8000"
        cls.test_port = 8000
    
    @classmethod
    def _find_executable(cls):
        """Find the executable in dist folder."""
        if sys.platform == 'win32':
            executables = list(cls.dist_dir.glob("rest-api-library*.exe"))
        else:
            # On Unix, executables have no extension
            executables = [
                f for f in cls.dist_dir.iterdir()
                if f.is_file() and 'rest-api-library' in f.name 
                and not f.suffix  # Exclude files with extensions (.txt, .md, etc.)
            ]
        
        if not executables:
            raise FileNotFoundError(f"No executable found in {cls.dist_dir}")
        
        # Return the first one (could be more sophisticated)
        return executables[0]
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        if cls.process:
            cls._stop_executable()
    
    @classmethod
    def _start_executable(cls, timeout=15):
        """Start the executable."""
        print(f"\nStarting executable: {cls.executable}")
        print(f"  Executable path: {cls.executable.absolute()}")
        print(f"  Working directory: {cls.dist_dir.absolute()}")
        
        # Verify executable exists
        if not cls.executable.exists():
            print(f"❌ Executable not found at {cls.executable}")
            return False
        
        # Ensure executable has execute permissions on Unix
        if sys.platform != 'win32':
            try:
                os.chmod(cls.executable, 0o755)
                print(f"  ✓ Set execute permissions on {cls.executable.name}")
            except Exception as e:
                print(f"  ⚠️  Could not set permissions: {e}")
                return False
        
        # Create test .env file
        env_content = f"""
DATABASE_URL=sqlite:///./test.db
HOST=127.0.0.1
PORT={cls.test_port}
DEBUG=True
"""
        test_env = cls.dist_dir / ".env"
        test_env.write_text(env_content)
        print(f"  ✓ Created .env file")
        
        # Start executable (use just the name since cwd is dist_dir)
        try:
            cls.process = subprocess.Popen(
                [f"./{cls.executable.name}"],
                cwd=cls.dist_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"  ✓ Process started (PID: {cls.process.pid})")
        except Exception as e:
            print(f"❌ Failed to start process: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Wait for server to start
        print(f"Waiting for server to start (timeout: {timeout}s)...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if process crashed
            if cls.process.poll() is not None:
                stdout, stderr = cls.process.communicate()
                print(f"❌ Process crashed!")
                print(f"  Exit code: {cls.process.returncode}")
                print(f"  STDOUT ({len(stdout)} chars):")
                print(f"    {stdout[:1000] if stdout else '(empty)'}")
                print(f"  STDERR ({len(stderr)} chars):")
                print(f"    {stderr[:1000] if stderr else '(empty)'}")
                cls.process = None
                return False
            
            try:
                response = requests.get(f"{cls.base_url}/health", timeout=1)
                if response.status_code == 200:
                    print("✓ Server started successfully!")
                    return True
            except requests.exceptions.RequestException:
                time.sleep(0.5)
        
        # Timeout
        print("❌ Server failed to start within timeout")
        if cls.process and cls.process.poll() is None:
            # Process still running, try to get output before killing
            print("  Process is still running, terminating to get output...")
            cls.process.terminate()
            try:
                stdout, stderr = cls.process.communicate(timeout=2)
                print(f"  STDOUT ({len(stdout)} chars): {stdout[:500] if stdout else '(empty)'}")
                print(f"  STDERR ({len(stderr)} chars): {stderr[:500] if stderr else '(empty)'}")
            except subprocess.TimeoutExpired:
                print("  Process didn't terminate, killing...")
                cls.process.kill()
                cls.process.wait()
        elif cls.process:
            print(f"  Process already exited with code: {cls.process.returncode}")
        cls._stop_executable()
        return False
    
    @classmethod
    def _stop_executable(cls):
        """Stop the executable."""
        if cls.process:
            print("\nStopping executable...")
            cls.process.terminate()
            try:
                cls.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cls.process.kill()
                cls.process.wait()
            print("✓ Executable stopped")
            
            # Clean up test database
            test_db = cls.dist_dir / "test.db"
            if test_db.exists():
                test_db.unlink()
    
    def test_01_executable_exists(self):
        """Test that executable file exists."""
        self.assertTrue(
            self.executable.exists(),
            f"Executable not found: {self.executable}"
        )
        print(f"  ✓ Executable exists: {self.executable.name}")
    
    def test_02_executable_is_executable(self):
        """Test that file has executable permissions (Unix)."""
        if sys.platform != 'win32':
            self.assertTrue(
                os.access(self.executable, os.X_OK),
                f"File is not executable: {self.executable}"
            )
        print(f"  ✓ File has correct permissions")
    
    def test_03_executable_size(self):
        """Test that executable has reasonable size."""
        size = self.executable.stat().st_size
        min_size = 10 * 1024 * 1024  # 10 MB
        max_size = 200 * 1024 * 1024  # 200 MB
        
        self.assertGreater(size, min_size, "Executable is too small")
        self.assertLess(size, max_size, "Executable is too large")
        
        size_mb = size / (1024 * 1024)
        print(f"  ✓ Executable size: {size_mb:.1f} MB (within expected range)")
    
    def test_04_start_executable(self):
        """Test that executable can start."""
        started = self._start_executable()
        if not started:
            # Print additional debug info
            print(f"\n❌ Startup failed for: {self.__class__.executable}")
            print(f"   Working directory: {self.__class__.dist_dir.absolute()}")
            print(f"   File exists: {self.__class__.executable.exists()}")
            if self.__class__.executable.exists():
                print(f"   File size: {self.__class__.executable.stat().st_size} bytes")
                if sys.platform != 'win32':
                    import stat
                    mode = self.__class__.executable.stat().st_mode
                    print(f"   Permissions: {oct(stat.S_IMODE(mode))}")
        self.assertTrue(started, "Executable failed to start - check debug output above")
    
    def test_05_health_endpoint(self):
        """Test health endpoint."""
        # Check if process is actually running
        if not self.__class__.process or self.__class__.process.poll() is not None:
            started = self._start_executable()
            self.assertTrue(started, "Failed to start executable for health check")
        
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        print(f"  ✓ Health endpoint working: {data}")
    
    def test_06_root_endpoint(self):
        """Test root endpoint."""
        # Check if process is actually running
        if not self.__class__.process or self.__class__.process.poll() is not None:
            started = self._start_executable()
            self.assertTrue(started, "Failed to start executable for root endpoint test")
        
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('version', data)
        print(f"  ✓ Root endpoint working: {data.get('message')}")
    
    def test_07_docs_endpoint(self):
        """Test API documentation endpoint."""
        # Check if process is actually running
        if not self.__class__.process or self.__class__.process.poll() is not None:
            started = self._start_executable()
            self.assertTrue(started, "Failed to start executable for docs test")
        
        response = requests.get(f"{self.base_url}/docs")
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.headers.get('content-type', ''))
        print(f"  ✓ API docs endpoint accessible")
    
    def test_08_create_user(self):
        """Test creating a user via API."""
        # Check if process is actually running
        if not self.__class__.process or self.__class__.process.poll() is not None:
            started = self._start_executable()
            self.assertTrue(started, "Failed to start executable for user creation test")
        
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True
        }
        
        response = requests.post(
            f"{self.base_url}/api/users/",
            json=user_data
        )
        self.assertEqual(response.status_code, 201)
        
        data = response.json()
        self.assertEqual(data['username'], user_data['username'])
        self.assertEqual(data['email'], user_data['email'])
        self.assertIn('id', data)
        print(f"  ✓ User created successfully: ID {data['id']}")
    
    def test_09_get_users(self):
        """Test getting users list."""
        # Check if process is actually running
        if not self.__class__.process or self.__class__.process.poll() is not None:
            started = self._start_executable()
            self.assertTrue(started, "Failed to start executable for get users test")
        
        response = requests.get(f"{self.base_url}/api/users/")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "Should have at least one user")
        print(f"  ✓ Retrieved {len(data)} user(s)")
    
    def test_10_create_item(self):
        """Test creating an item via API."""
        # Check if process is actually running
        if not self.__class__.process or self.__class__.process.poll() is not None:
            started = self._start_executable()
            self.assertTrue(started, "Failed to start executable for item creation test")
        
        item_data = {
            "title": "Test Item",
            "description": "Test description",
            "price": 9999,
            "is_available": True
        }
        
        response = requests.post(
            f"{self.base_url}/api/items/",
            json=item_data
        )
        self.assertEqual(response.status_code, 201)
        
        data = response.json()
        self.assertEqual(data['title'], item_data['title'])
        self.assertIn('id', data)
        print(f"  ✓ Item created successfully: ID {data['id']}")
    
    def test_11_stop_executable(self):
        """Test stopping the executable."""
        if self.__class__.process:
            self._stop_executable()
            self.__class__.process = None
        print(f"  ✓ Executable stopped cleanly")


def run_tests():
    """Run all tests."""
    print("="*60)
    print("EXECUTABLE TESTS")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ExecutableTests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
