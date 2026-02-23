# Building Executable Packages

This guide explains how to package the REST API Library as standalone executables for distribution to systems without Python installed.

## Prerequisites

### 1. Install Build Dependencies

```bash
pip install -r requirements-dev.txt
```

This installs PyInstaller and other build tools.

### 2. Supported Platforms

- **Linux**: Builds ELF executables
- **macOS**: Builds Mach-O executables

**Note**: You must build on the target platform (cross-compilation is not supported).

## Build Methods

### Method 1: Quick Build (All Databases)

Build a single executable with support for all databases:

```bash
python build.py
```

This creates `dist/rest-api-library` (or equivalent on your platform) with SQLite, PostgreSQL, and MySQL support.

### Method 2: Database-Specific Builds

Build optimized executables for specific databases:

```bash
# Build for SQLite only (smallest size)
python build_databases.py sqlite

# Build for PostgreSQL
python build_databases.py postgresql

# Build for MySQL
python build_databases.py mysql

# Build all database-specific versions
python build_databases.py all
```

**Benefits**:
- Smaller file size
- Includes only necessary database drivers
- Database-specific README files

### Method 3: Custom Build with Spec File

For advanced customization, use the spec file:

```bash
python build.py --spec
```

Edit `api_library.spec` to customize:
- Hidden imports
- Data files
- Excluded modules
- Build options
- Icons

## Build Options

### Basic Options

```bash
# Single executable file (default)
python build.py --mode onefile

# Directory bundle (faster startup)
python build.py --mode onedir

# Specific database
python build.py --db sqlite

# Create distribution package
python build.py --package
```

### Advanced Options

```bash
# Skip cleaning previous builds
python build.py --no-clean

# Use custom spec file
python build.py --spec

# Full example
python build.py --db all --mode onefile --package
```

## Build Output

### File Structure

After building, you'll find:

```
dist/
├── rest-api-library             # Main executable
├── rest-api-library-sqlite      # SQLite-specific
├── rest-api-library-postgresql  # PostgreSQL-specific
├── rest-api-library-mysql       # MySQL-specific
└── rest-api-library-1.0.0/      # Distribution package (with --package)
    ├── rest-api-library
    ├── .env
    ├── README.md
    ├── QUICKSTART.md
    └── start.sh                 # Unix launcher
```

### File Sizes (Approximate)

- **SQLite only**: ~40-50 MB
- **All databases**: ~60-80 MB
- **onedir mode**: Larger but faster startup

## Distribution

### Creating Distribution Packages

```bash
# Build and create distribution package
python build.py --package
```

This creates a ZIP file with:
- Executable
- Configuration file (.env)
- Documentation
- Startup scripts

### Manual Distribution

1. **Build the executable**:
   ```bash
   python build.py
   ```

2. **Test the executable**:
   ```bash
   cd dist
   ./rest-api-library
   ```

3. **Create distribution folder**:
   ```bash
   mkdir release
   cp dist/rest-api-library release/
   cp .env.example release/.env
   cp README.md QUICKSTART.md release/
   ```

4. **Compress**:
   ```bash
   tar -czf rest-api-library-v1.0.0-linux.tar.gz release/
   ```

## Platform-Specific Instructions

### Linux

#### Building on Linux

```bash
python build.py
```

Output: `dist/rest-api-library`

#### Creating .deb Package

```bash
# Install packaging tools
sudo apt install dpkg-dev

# Create package structure
mkdir -p rest-api-library_1.0.0/usr/local/bin
mkdir -p rest-api-library_1.0.0/DEBIAN

# Copy executable
cp dist/rest-api-library rest-api-library_1.0.0/usr/local/bin/

# Create control file
cat > rest-api-library_1.0.0/DEBIAN/control << EOF
Package: rest-api-library
Version: 1.0.0
Architecture: amd64
Maintainer: Your Name <your.email@example.com>
Description: REST API Library with database support
EOF

# Build package
dpkg-deb --build rest-api-library_1.0.0
```

### macOS

#### Building on macOS

```bash
python build.py
```

Output: `dist/rest-api-library`

#### Creating .app Bundle (Optional)

```bash
# Create app bundle structure
mkdir -p "REST API Library.app/Contents/MacOS"
mkdir -p "REST API Library.app/Contents/Resources"

# Copy executable
cp dist/rest-api-library "REST API Library.app/Contents/MacOS/"

# Create Info.plist
cat > "REST API Library.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>rest-api-library</string>
    <key>CFBundleName</key>
    <string>REST API Library</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
</dict>
</plist>
EOF
```

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError

**Problem**: Missing hidden imports

**Solution**: Add to `api_library.spec`:
```python
hiddenimports += ['missing_module']
```

#### 2. Large Executable Size

**Problem**: Executable is too large

**Solutions**:
- Use `--mode onedir` for better compression
- Build database-specific versions
- Exclude unused modules in spec file:
  ```python
  excludes=['matplotlib', 'numpy', 'pandas']
  ```

#### 3. Slow Startup

**Problem**: Executable takes long to start

**Solution**: Use `--mode onedir` instead of `--onefile`

#### 4. Database Driver Not Found

**Problem**: Database connection fails

**Solution**: 
- Use `build_databases.py` for database-specific builds
- Ensure database drivers are in hidden imports

#### 5. Runtime Errors

**Problem**: Works in Python but fails in executable

**Solution**:
- Test with `python run.py` first
- Check console output for missing modules
- Add missing imports to spec file

### Testing the Executable

```bash
# Build
python build.py

# Test
cd dist
./rest-api-library

# In another terminal, test API
curl http://localhost:8000/health
```

## Optimization Tips

### 1. Reduce Size

```python
# In api_library.spec, exclude unused packages
excludes=[
    'matplotlib',
    'numpy', 
    'pandas',
    'scipy',
    'PIL',
    'tkinter',
]
```

### 2. Improve Startup Time

- Use `--onedir` mode
- Minimize hidden imports
- Use lazy imports in code

### 3. Better Compression

```bash
# Use UPX (if available)
pyinstaller --upx-dir=/path/to/upx ...
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Build Executables

on: [push, release]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Build executable
      run: python build.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: executable-${{ matrix.os }}
        path: dist/
```

## Security Considerations

1. **Don't embed secrets** in executables
2. **Use .env files** for configuration
3. **Validate user input** in production
4. **Use HTTPS** in production
5. **Keep dependencies updated**

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [PyInstaller Spec Files](https://pyinstaller.readthedocs.io/en/stable/spec-files.html)
- [create-dmg](https://github.com/create-dmg/create-dmg) (macOS installers)

## Support

For build issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review PyInstaller logs in `build/` directory
3. Open an issue on the repository
