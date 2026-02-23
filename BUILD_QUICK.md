# Quick Build Reference

## Install Build Tools
```bash
pip install -r requirements-dev.txt
```

## Basic Builds

### Single Executable (All Databases)
```bash
python build.py
```
**Output**: `dist/rest-api-library.exe` (~60-80 MB)

### SQLite Only (Smallest)
```bash
python build_databases.py sqlite
```
**Output**: `dist/rest-api-library-sqlite.exe` (~40-50 MB)

### PostgreSQL
```bash
python build_databases.py postgresql
```

### MySQL
```bash
python build_databases.py mysql
```

### All Database Versions
```bash
python build_databases.py all
```

## Build Modes

### Single File (Default)
```bash
python build.py --mode onefile
```
- Slower startup
- Easy to distribute
- Single executable

### Directory Bundle
```bash
python build.py --mode onedir
```
- Faster startup
- Multiple files
- Smaller individual files

## Distribution Package

Create a complete distribution with docs and config:

```bash
python build.py --package
```

Creates: `dist/rest-api-library-1.0.0.zip`

## Custom Builds

Edit `api_library.spec` then:

```bash
python build.py --spec
```

## Testing

```bash
# Build
python build.py

# Run
cd dist
./rest-api-library

# Test API
curl http://localhost:8000/health
```

## Platform-Specific

### Windows
```bash
python build.py
# Creates: dist/rest-api-library.exe
```

### Linux
```bash
python build.py
# Creates: dist/rest-api-library
chmod +x dist/rest-api-library
```

### macOS
```bash
python build.py
# Creates: dist/rest-api-library
chmod +x dist/rest-api-library
```

## Common Issues

**Large size?**
→ Use database-specific builds

**Slow startup?**
→ Use `--mode onedir`

**Missing module?**
→ Add to `hiddenimports` in spec file

**Database error?**
→ Use `build_databases.py` for correct drivers

## File Locations

- **Executables**: `dist/`
- **Build logs**: `build/`
- **Spec file**: `api_library.spec`
- **Config**: `.env` (copy from `.env.example`)

## Next Steps

1. Build → `python build.py`
2. Test → `cd dist && ./rest-api-library`
3. Configure → Edit `.env`
4. Distribute → Share `dist/` folder or use `--package`

For detailed instructions, see [BUILD.md](BUILD.md)
