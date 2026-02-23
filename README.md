# REST API Library

A comprehensive REST API library built with **FastAPI** and **SQLAlchemy**, providing database functionality with support for multiple open-source database backends.

## Features

✨ **Modern FastAPI Framework** - Fast, async-ready REST API with automatic OpenAPI documentation  
📦 **SQLAlchemy ORM** - Powerful and flexible database abstraction  
🗄️ **Multiple Database Support** - SQLite, PostgreSQL, MySQL, and more  
🔒 **Data Validation** - Pydantic schemas for request/response validation  
🚀 **CRUD Operations** - Complete Create, Read, Update, Delete functionality  
📊 **Pagination & Filtering** - Built-in pagination and search capabilities  
🎯 **Type Safety** - Full type hints throughout the codebase  

## Quick Start

**New to this project?** See [QUICKSTART.md](QUICKSTART.md) for step-by-step setup instructions.

**Quick commands:**
```bash
python3 -m venv venv              # Create virtual environment
source venv/bin/activate          # Activate it (Linux/macOS)
pip install -r requirements.txt   # Install dependencies
python db_manager.py create       # Create database tables
python run.py                      # Start server
```

Visit http://localhost:8000/docs for interactive API documentation.

## Database Configuration

The library uses **SQLite** by default (no setup required). To use other databases, update the `DATABASE_URL` in your `.env` file:

### PostgreSQL
```env
DATABASE_URL=postgresql://username:password@localhost/dbname
```

### MySQL
```env
DATABASE_URL=mysql://username:password@localhost/dbname
```

### SQLite (default)
```env
DATABASE_URL=sqlite:///./app.db
```

## Building Executables

Package the API as standalone executables for distribution to systems without Python:

### Quick Build

```bash
# Install build tools
pip install -r requirements.txt

# Build executable (all databases)
python build.py all

# Build database-specific versions
python build.py sqlite      # SQLite only (~40 MB)
python build.py postgresql  # PostgreSQL
python build.py mysql       # MySQL
python build.py all         # All versions

# Create distribution packages
python build.py sqlite --package  # SQLite package
python build.py all --package     # All packages
```

**Note:** For production deployments, build on the target platform (Linux/macOS) for best compatibility.

### Using Build Scripts

**Linux/Mac:**
```bash
chmod +x build.sh
./build.sh                   # Build all databases
./build.sh sqlite            # SQLite version
./build.sh sqlite --package  # SQLite with package
./build.sh all --package     # All databases with packages
```

**Output:** Executables in `dist/` folder

📖 **Detailed instructions:** See [BUILD.md](BUILD.md)

## API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/` | Create a new user |
| GET | `/api/users/` | List all users (with pagination) |
| GET | `/api/users/{user_id}` | Get a specific user |
| PUT | `/api/users/{user_id}` | Update a user |
| DELETE | `/api/users/{user_id}` | Delete a user |

### Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/items/` | Create a new item |
| GET | `/api/items/` | List all items (with pagination) |
| GET | `/api/items/{item_id}` | Get a specific item |
| PUT | `/api/items/{item_id}` | Update an item |
| DELETE | `/api/items/{item_id}` | Delete an item |

## Usage Examples

### Create a User
```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true
  }'
```

### Get All Users
```bash
curl "http://localhost:8000/api/users/?skip=0&limit=10"
```

### Create an Item
```bash
curl -X POST "http://localhost:8000/api/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Laptop",
    "description": "High-performance laptop",
    "price": 99999,
    "is_available": true
  }'
```

### Search Items
```bash
curl "http://localhost:8000/api/items/?search=laptop"
```

## Project Structure

```
repo/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # CRUD operations
│   └── routes.py            # API endpoints
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Extending the Library

### Adding a New Model

1. **Define the model** in `app/models.py`:
```python
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    # ... more fields
```

2. **Create schemas** in `app/schemas.py`:
```python
class ProductBase(BaseModel):
    name: str
    # ... more fields

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

3. **Add CRUD operations** in `app/crud.py`:
```python
class CRUDProduct(CRUDBase[models.Product, schemas.ProductCreate, schemas.ProductUpdate]):
    pass

product = CRUDProduct(models.Product)
```

4. **Create routes** in `app/routes.py`:
```python
product_router = APIRouter(prefix="/products", tags=["products"])

@product_router.post("/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.product.create(db=db, obj_in=product)
```

5. **Register the router** in `app/main.py`:
```python
from app.routes import product_router
app.include_router(product_router, prefix="/api")
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

### Type Checking
```bash
mypy app/
```

## Requirements

- Python 3.8+
- FastAPI
- SQLAlchemy
- Uvicorn
- Pydantic

See `requirements.txt` for complete list.

## CI/CD & Testing

The project includes comprehensive CI/CD pipeline and testing infrastructure:

### Jenkins Integration
- Automated builds with Jenkins pipeline
- Multi-database build support
- Automated testing and verification
- Build artifact archiving

### Test Suites
- ✅ **Build Verification** - Validate build artifacts
- ✅ **Installer Tests** - Package structure validation  
- ✅ **Executable Tests** - Functionality testing
- ✅ **Database Integration** - Multi-database testing
- ✅ **Performance Tests** - Load and performance benchmarks

### Quick Test Commands

```bash
# Verify CI/CD setup
python ci/verify_setup.py

# Run all tests
python ci/run_tests.py

# Run specific test suite
python ci/run_tests.py --suite executable

# Skip slow tests
python ci/run_tests.py --skip-slow

# Clean artifacts
python ci/clean_artifacts.py
```

📖 **Detailed CI/CD documentation:** See [ci/README.md](ci/README.md)

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the repository.
