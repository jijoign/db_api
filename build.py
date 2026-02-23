"""Build script for creating executable packages of the REST API library.

This script uses PyInstaller to create standalone executables that can be
distributed and run on systems without Python installed.
"""
import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


# Build configuration
PROJECT_NAME = "rest-api-library"
VERSION = "1.0.0"
MAIN_SCRIPT = "run.py"
ICON_FILE = None  # Set to path of .ico file if available

# Directories
BUILD_DIR = Path("build")
DIST_DIR = Path("dist")
SPEC_DIR = Path(".")


def clean_builds():
    """Remove previous build artifacts."""
    print("🧹 Cleaning previous builds...")
    
    dirs_to_clean = [BUILD_DIR, DIST_DIR, Path("__pycache__")]
    for directory in dirs_to_clean:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"  ✓ Removed {directory}")
    
    # Remove spec files
    for spec_file in Path(".").glob("*.spec"):
        if spec_file.name != "api_library.spec":  # Keep custom spec
            spec_file.unlink()
            print(f"  ✓ Removed {spec_file}")
    
    print("✓ Clean completed\n")


def check_dependencies():
    """Check if required build dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    try:
        import PyInstaller
        print(f"  ✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("  ❌ PyInstaller not found")
        print("  Install with: pip install -r requirements-dev.txt")
        return False
    
    return True


def build_executable(database_type="sqlite", onefile=True):
    """Build executable for specific database type.
    
    Args:
        database_type: Database type (sqlite, postgresql, mysql, all)
        onefile: If True, create single executable file
    """
    print(f"\n📦 Building executable for {database_type.upper()}...")
    
    # Determine executable name
    exe_name = f"{PROJECT_NAME}-{database_type}" if database_type != "all" else PROJECT_NAME
    
    # Base PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", exe_name,
        "--clean",
        "--noconfirm",
    ]
    
    # Single file or directory bundle
    if onefile:
        cmd.append("--onefile")
        print("  Mode: Single executable file")
    else:
        cmd.append("--onedir")
        print("  Mode: Directory bundle")
    
    # Add icon if available
    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd.extend(["--icon", ICON_FILE])
    
    # Hidden imports for database drivers
    hidden_imports = [
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
    ]
    
    # Add database-specific imports
    if database_type in ["postgresql", "all"]:
        hidden_imports.extend([
            "psycopg2",
            "psycopg2.extensions",
            "psycopg2.extras",
        ])
    
    if database_type in ["mysql", "all"]:
        hidden_imports.extend([
            "pymysql",
            "pymysql.cursors",
        ])
    
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    
    # Add data files
    cmd.extend([
        "--add-data", f".env.example{os.pathsep}.",
        "--add-data", f"README.md{os.pathsep}.",
        "--add-data", f"QUICKSTART.md{os.pathsep}.",
    ])
    
    # Collect all from app package
    cmd.extend([
        "--collect-all", "fastapi",
        "--collect-all", "pydantic",
        "--collect-all", "sqlalchemy",
        "--copy-metadata", "fastapi",
        "--copy-metadata", "pydantic",
        "--copy-metadata", "uvicorn",
    ])
    
    # Main script
    cmd.append(MAIN_SCRIPT)
    
    # Run PyInstaller
    print(f"  Command: {' '.join(cmd)}")
    print("\n  Building...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  ✓ Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Build failed!")
        print(f"  Error: {e.stderr}")
        return False


def build_with_spec_file():
    """Build using custom spec file."""
    print("\n📦 Building with custom spec file...")
    
    spec_file = "api_library.spec"
    if not os.path.exists(spec_file):
        print(f"  ❌ Spec file {spec_file} not found")
        return False
    
    cmd = ["pyinstaller", "--clean", "--noconfirm", spec_file]
    
    try:
        subprocess.run(cmd, check=True)
        print("  ✓ Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Build failed: {e}")
        return False


def create_distribution_package():
    """Create a distribution package with documentation."""
    print("\n📦 Creating distribution package...")
    
    # Create distribution directory
    package_name = f"{PROJECT_NAME}-{VERSION}"
    package_dir = DIST_DIR / package_name
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    exe_files = list(DIST_DIR.glob(f"{PROJECT_NAME}*"))
    for exe_file in exe_files:
        if exe_file.is_file() and exe_file != package_dir:
            shutil.copy2(exe_file, package_dir)
            print(f"  ✓ Copied {exe_file.name}")
    
    # Copy documentation
    docs = ["README.md", "QUICKSTART.md", "LICENSE" if os.path.exists("LICENSE") else None]
    for doc in docs:
        if doc and os.path.exists(doc):
            shutil.copy2(doc, package_dir)
            print(f"  ✓ Copied {doc}")
    
    # Copy example environment file
    shutil.copy2(".env.example", package_dir / ".env")
    print("  ✓ Copied .env.example as .env")
    
    # Create startup scripts
    create_startup_scripts(package_dir)
    
    # Create zip archive
    print(f"\n  Creating archive...")
    archive_name = shutil.make_archive(
        str(DIST_DIR / package_name),
        'zip',
        DIST_DIR,
        package_name
    )
    print(f"  ✓ Created {archive_name}")
    
    print(f"\n✓ Distribution package ready: {archive_name}")


def create_startup_scripts(package_dir):
    """Create startup script for Unix systems."""
    
    # Linux/Mac shell script
    sh_content = f"""#!/bin/bash
echo "Starting REST API Library..."
echo
./{PROJECT_NAME}
"""
    sh_file = package_dir / "start.sh"
    with open(sh_file, "w") as f:
        f.write(sh_content)
    
    # Make executable on Unix systems
    os.chmod(sh_file, 0o755)
    
    print("  ✓ Created start.sh")


def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description="Build REST API Library executable")
    parser.add_argument(
        "--db",
        choices=["sqlite", "postgresql", "mysql", "all"],
        default="all",
        help="Database type to include support for (default: all)"
    )
    parser.add_argument(
        "--mode",
        choices=["onefile", "onedir"],
        default="onefile",
        help="Build mode: single file or directory (default: onefile)"
    )
    parser.add_argument(
        "--spec",
        action="store_true",
        help="Use custom spec file instead of command-line build"
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Skip cleaning previous builds"
    )
    parser.add_argument(
        "--package",
        action="store_true",
        help="Create distribution package after build"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"REST API Library - Build Script v{VERSION}")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Clean previous builds
    if not args.no_clean:
        clean_builds()
    
    # Build
    success = False
    if args.spec:
        success = build_with_spec_file()
    else:
        onefile = (args.mode == "onefile")
        success = build_executable(args.db, onefile)
    
    if not success:
        print("\n❌ Build failed!")
        sys.exit(1)
    
    # Create distribution package
    if args.package:
        create_distribution_package()
    
    print("\n" + "=" * 60)
    print("✓ Build completed successfully!")
    print("=" * 60)
    print(f"\nExecutable(s) available in: {DIST_DIR.absolute()}")
    print("\nTo run:")
    print(f"  ./{DIST_DIR}/{PROJECT_NAME}")
    print("\nTo build installer packages:")
    print("  - macOS: Use create-dmg or pkgbuild")
    print("  - Linux: Create .deb or .rpm packages")


if __name__ == "__main__":
    main()
