"""Build database-specific executables with appropriate drivers.

This script creates optimized executables for each database type,
including only the necessary database drivers.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


DATABASE_CONFIGS = {
    'sqlite': {
        'description': 'SQLite (embedded database, no external dependencies)',
        'packages': [],
        'hidden_imports': [],
        'env_template': 'DATABASE_URL=sqlite:///./app.db',
    },
    'postgresql': {
        'description': 'PostgreSQL database support',
        'packages': ['psycopg2-binary'],
        'hidden_imports': ['psycopg2', 'psycopg2.extensions', 'psycopg2.extras'],
        'env_template': 'DATABASE_URL=postgresql://user:password@localhost/dbname',
    },
    'mysql': {
        'description': 'MySQL/MariaDB database support',
        'packages': ['pymysql'],
        'hidden_imports': ['pymysql', 'pymysql.cursors', 'pymysql.connections'],
        'env_template': 'DATABASE_URL=mysql+pymysql://user:password@localhost/dbname',
    },
}


def build_for_database(db_type, output_dir='dist'):
    """Build executable for specific database type."""
    
    if db_type not in DATABASE_CONFIGS:
        print(f"❌ Unknown database type: {db_type}")
        print(f"   Available: {', '.join(DATABASE_CONFIGS.keys())}")
        return False
    
    config = DATABASE_CONFIGS[db_type]
    exe_name = f"rest-api-library-{db_type}"
    
    print(f"\n{'='*60}")
    print(f"Building: {exe_name}")
    print(f"Database: {config['description']}")
    print(f"{'='*60}\n")
    
    # Install database-specific packages if needed
    if config['packages']:
        print(f"📦 Installing {db_type} packages...")
        for package in config['packages']:
            try:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package],
                    check=True,
                    capture_output=True
                )
                print(f"  ✓ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"  ⚠️  Warning: Could not install {package}")
                print(f"     {e.stderr.decode()}")
    
    # Build PyInstaller command
    cmd = [
        'pyinstaller',
        '--name', exe_name,
        '--onefile',
        '--clean',
        '--noconfirm',
        '--console',
    ]
    
    # Add hidden imports
    base_imports = [
        'uvicorn.logging',
        'uvicorn.loops.auto',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan.on',
    ]
    
    for imp in base_imports + config['hidden_imports']:
        cmd.extend(['--hidden-import', imp])
    
    # Add data files
    cmd.extend([
        '--add-data', f'.env.example{os.pathsep}.',
        '--add-data', f'README.md{os.pathsep}.',
    ])
    
    # Collect packages
    for pkg in ['fastapi', 'pydantic', 'sqlalchemy']:
        cmd.extend(['--collect-all', pkg])
    
    # Copy metadata
    for pkg in ['fastapi', 'pydantic', 'uvicorn']:
        cmd.extend(['--copy-metadata', pkg])
    
    # Main script
    cmd.append('run.py')
    
    # Build
    print(f"\n🔨 Building {exe_name}...")
    print(f"   Command: {' '.join(cmd[:5])}...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ Build successful!\n")
        
        # Create database-specific README
        create_db_readme(db_type, exe_name, output_dir)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed!")
        print(f"   Error: {e.stderr}")
        return False


def create_db_readme(db_type, exe_name, output_dir):
    """Create database-specific README file."""
    
    config = DATABASE_CONFIGS[db_type]
    readme_path = Path(output_dir) / f"{exe_name}-README.txt"
    
    content = f"""
REST API Library - {db_type.upper()} Edition
{'='*60}

This executable includes support for {config['description']}.

QUICK START
-----------

1. Create a .env file in the same directory as the executable:

   {config['env_template']}

2. Run the executable:

   ./{exe_name}

3. Access the API:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

CONFIGURATION
-------------

Edit the .env file to customize:
- DATABASE_URL: Database connection string
- HOST: API server host (default: 0.0.0.0)
- PORT: API server port (default: 8000)
- DEBUG: Enable debug mode (default: True)

"""
    
    if db_type == 'postgresql':
        content += """
POSTGRESQL SETUP
----------------

1. Install PostgreSQL server
2. Create a database:
   createdb myapidb

3. Update .env with your connection:
   DATABASE_URL=postgresql://username:password@localhost/myapidb

"""
    elif db_type == 'mysql':
        content += """
MYSQL SETUP
-----------

1. Install MySQL/MariaDB server
2. Create a database:
   CREATE DATABASE myapidb;

3. Update .env with your connection:
   DATABASE_URL=mysql+pymysql://username:password@localhost/myapidb

"""
    
    content += """
SUPPORT
-------

For more information, see README.md or visit the documentation.

"""
    
    readme_path.write_text(content)
    print(f"  ✓ Created {readme_path.name}")


def create_startup_scripts(package_dir, exe_name):
    """Create startup script for Unix systems."""
    
    # Linux/Mac shell script
    sh_content = f"""#!/bin/bash
echo "Starting REST API Library ({exe_name})..."
echo
./{exe_name}
"""
    sh_file = package_dir / "start.sh"
    with open(sh_file, "w") as f:
        f.write(sh_content)
    
    # Make executable on Unix systems
    os.chmod(sh_file, 0o755)
    
    print(f"  ✓ Created start.sh")


def create_distribution_package(db_type):
    """Create a distribution package for a specific database build."""
    print(f"\n📦 Creating distribution package for {db_type}...")
    
    exe_name = f"rest-api-library-{db_type}"
    package_name = f"{exe_name}-1.0.0"
    package_dir = Path("dist") / package_name
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    exe_file = Path("dist") / exe_name
    if exe_file.exists():
        shutil.copy2(exe_file, package_dir)
        print(f"  ✓ Copied {exe_name}")
    else:
        print(f"  ⚠️  Executable not found: {exe_file}")
        return None
    
    # Copy database-specific README
    readme_file = Path("dist") / f"{exe_name}-README.txt"
    if readme_file.exists():
        shutil.copy2(readme_file, package_dir / "README.txt")
        print(f"  ✓ Copied database-specific README")
    
    # Copy main documentation
    docs = ["README.md", "QUICKSTART.md"]
    for doc in docs:
        if os.path.exists(doc):
            shutil.copy2(doc, package_dir)
            print(f"  ✓ Copied {doc}")
    
    # Copy and customize .env file
    config = DATABASE_CONFIGS[db_type]
    env_content = f"""# {db_type.upper()} Configuration
{config['env_template']}

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False
"""
    env_file = package_dir / ".env"
    env_file.write_text(env_content)
    print(f"  ✓ Created .env with {db_type} defaults")
    
    # Create startup scripts
    create_startup_scripts(package_dir, exe_name)
    
    # Create zip archive
    print(f"\n  Creating archive...")
    archive_name = shutil.make_archive(
        str(Path("dist") / package_name),
        'zip',
        Path("dist"),
        package_name
    )
    print(f"  ✓ Created {archive_name}")
    
    print(f"\n✓ Distribution package ready: {archive_name}")
    return archive_name


def create_all_packages():
    """Create distribution packages for all database types."""
    print(f"\n{'='*60}")
    print("Creating distribution packages for all builds")
    print(f"{'='*60}")
    
    packages = []
    for db_type in DATABASE_CONFIGS.keys():
        exe_file = Path("dist") / f"rest-api-library-{db_type}"
        if exe_file.exists():
            archive = create_distribution_package(db_type)
            if archive:
                packages.append(archive)
        else:
            print(f"\n⚠️  Skipping {db_type}: executable not found")
    
    if packages:
        print(f"\n{'='*60}")
        print("PACKAGE SUMMARY")
        print(f"{'='*60}")
        for pkg in packages:
            print(f"✓ {Path(pkg).name}")
        print()
    
    return len(packages) > 0


def build_all():
    """Build executables for all database types."""
    
    print("\n" + "="*60)
    print("Building executables for all database types")
    print("="*60)
    
    results = {}
    for db_type in DATABASE_CONFIGS.keys():
        success = build_for_database(db_type)
        results[db_type] = success
    
    # Summary
    print("\n" + "="*60)
    print("BUILD SUMMARY")
    print("="*60)
    
    for db_type, success in results.items():
        status = "✓" if success else "❌"
        print(f"{status} {db_type.upper()}: {'Success' if success else 'Failed'}")
    
    print()
    
    if all(results.values()):
        print("✓ All builds completed successfully!")
        print(f"\nExecutables available in: {Path('dist').absolute()}")
        return True
    else:
        print("⚠️  Some builds failed")
        return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Build database-specific executables"
    )
    parser.add_argument(
        'database',
        nargs='?',
        choices=list(DATABASE_CONFIGS.keys()) + ['all'],
        default='all',
        help='Database type to build for (default: all)'
    )
    parser.add_argument(
        '--package',
        action='store_true',
        help='Create distribution package after build'
    )
    
    args = parser.parse_args()
    
    # Check PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not installed")
        print("   Install with: pip install -r requirements.txt")
        sys.exit(1)
    
    # Build
    if args.database == 'all':
        success = build_all()
    else:
        success = build_for_database(args.database)
    
    # Create distribution package if requested
    if success and args.package:
        if args.database == 'all':
            create_all_packages()
        else:
            create_distribution_package(args.database)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
