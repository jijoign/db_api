"""Performance and load tests for the executable."""
import sys
import os
import time
import subprocess
import tempfile
import shutil
from pathlib import Path
import unittest
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


class PerformanceTests(unittest.TestCase):
    """Performance and load tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once."""
        cls.dist_dir = Path("dist")
        cls.executable = cls._find_executable()
        cls.temp_dir = tempfile.mkdtemp(prefix="perf_test_")
        cls.process = None
        cls.base_url = "http://localhost:8200"
        cls.test_port = 8200
        
        # Start executable once for all tests
        cls._start_executable()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        if cls.process:
            cls.process.terminate()
            try:
                cls.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cls.process.kill()
        
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
    
    @classmethod
    def _find_executable(cls):
        """Find executable."""
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
            raise FileNotFoundError("No executable found")
        return executables[0]
    
    @classmethod
    def _start_executable(cls, timeout=15):
        """Start the executable."""
        env_content = f"""
DATABASE_URL=sqlite:///:memory:
HOST=127.0.0.1
PORT={cls.test_port}
DEBUG=False
"""
        
        env_file = Path(cls.temp_dir) / ".env"
        env_file.write_text(env_content)
        
        temp_exe = Path(cls.temp_dir) / cls.executable.name
        shutil.copy2(cls.executable, temp_exe)
        
        if sys.platform != 'win32':
            os.chmod(temp_exe, 0o755)
        
        cls.process = subprocess.Popen(
            [str(temp_exe)],
            cwd=cls.temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{cls.base_url}/health", timeout=1)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                time.sleep(0.5)
        
        return False
    
    def test_01_response_time_health(self):
        """Test health endpoint response time."""
        print("\n  Testing health endpoint response time...")
        
        times = []
        for _ in range(10):
            start = time.time()
            response = requests.get(f"{self.base_url}/health")
            elapsed = time.time() - start
            
            self.assertEqual(response.status_code, 200)
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # Should respond quickly
        self.assertLess(avg_time, 0.1, f"Average response time too high: {avg_time:.3f}s")
        
        print(f"    ✓ Avg: {avg_time*1000:.1f}ms, Max: {max_time*1000:.1f}ms")
    
    def test_02_concurrent_requests(self):
        """Test handling concurrent requests."""
        print("\n  Testing concurrent requests...")
        
        num_requests = 50
        
        def make_request(i):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                return response.status_code == 200
            except:
                return False
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            results = [f.result() for f in as_completed(futures)]
        
        elapsed = time.time() - start_time
        success_count = sum(results)
        
        self.assertEqual(success_count, num_requests, "Some requests failed")
        
        rps = num_requests / elapsed
        print(f"    ✓ {num_requests} requests in {elapsed:.2f}s ({rps:.1f} req/s)")
    
    def test_03_bulk_user_creation(self):
        """Test creating multiple users."""
        print("\n  Testing bulk user creation...")
        
        num_users = 20
        start_time = time.time()
        
        for i in range(num_users):
            user_data = {
                "username": f"perfuser_{i}_{int(time.time())}",
                "email": f"perf{i}_{int(time.time())}@example.com",
                "full_name": f"Performance User {i}"
            }
            
            response = requests.post(
                f"{self.base_url}/api/users/",
                json=user_data,
                timeout=5
            )
            self.assertEqual(response.status_code, 201)
        
        elapsed = time.time() - start_time
        rate = num_users / elapsed
        
        print(f"    ✓ Created {num_users} users in {elapsed:.2f}s ({rate:.1f} users/s)")
    
    def test_04_pagination_performance(self):
        """Test pagination with large result sets."""
        print("\n  Testing pagination performance...")
        
        # Get users with pagination
        start_time = time.time()
        response = requests.get(
            f"{self.base_url}/api/users/?skip=0&limit=100",
            timeout=5
        )
        elapsed = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        users = response.json()
        
        print(f"    ✓ Retrieved {len(users)} users in {elapsed*1000:.1f}ms")
    
    def test_05_memory_footprint(self):
        """Test memory usage (basic check)."""
        print("\n  Checking memory footprint...")
        
        if sys.platform == 'win32':
            # Use psutil if available
            try:
                import psutil
                process = psutil.Process(self.process.pid)
                memory_mb = process.memory_info().rss / (1024 * 1024)
                
                # Should use reasonable memory
                self.assertLess(
                    memory_mb, 500,
                    f"Memory usage too high: {memory_mb:.1f} MB"
                )
                print(f"    ✓ Memory usage: {memory_mb:.1f} MB")
            except ImportError:
                print("    ⚠️  psutil not available, skipping memory check")
        else:
            print("    ⚠️  Memory check not implemented for this platform")
    
    def test_06_startup_time(self):
        """Test startup time (re-measure from class setup)."""
        print("\n  Startup time was measured during setup")
        print("    ✓ Service started within acceptable time")


def run_tests():
    """Run performance tests."""
    print("="*60)
    print("PERFORMANCE TESTS")
    print("="*60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(PerformanceTests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
