# Quick Start Guide

## Installation & Setup

### 1. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate        # Windows (if needed)
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env if you want to use a different database
# Default is SQLite (no configuration needed)
```

### 4. Initialize Database
```bash
# Create database tables
python db_manager.py create

# Or reset the database (drops and recreates all tables)
python db_manager.py reset
```

### 5. Start the Server
```bash
# Method 1: Using the run script
python run.py

# Method 2: Using uvicorn directly
uvicorn app.main:app --reload

# Method 3: Using the main module
python -m app.main
```

The server will start at **http://localhost:8000**

### 6. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 7. Test the API
```bash
# In a new terminal, run the example usage script
python example_usage.py
```

## Using Different Databases

### SQLite (Default - No setup required)
```env
DATABASE_URL=sqlite:///./app.db
```

### PostgreSQL
1. Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

2. Update `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost/dbname
```

### MySQL
1. Install MySQL driver:
```bash
pip install pymysql
```

2. Update `.env`:
```env
DATABASE_URL=mysql+pymysql://username:password@localhost/dbname
```

## Common Commands

### Database Management
```bash
python db_manager.py create   # Create tables
python db_manager.py drop     # Drop tables
python db_manager.py reset    # Reset database
python db_manager.py show     # Show tables
```

### API Testing with curl

**Create a user:**
```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "full_name": "John Doe"}'
```

**Get all users:**
```bash
curl "http://localhost:8000/api/users/"
```

**Create an item:**
```bash
curl -X POST "http://localhost:8000/api/items/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Laptop", "description": "Gaming laptop", "price": 99999}'
```

**Search items:**
```bash
curl "http://localhost:8000/api/items/?search=laptop"
```

## Next Steps

1. Explore the interactive API documentation at http://localhost:8000/docs
2. Review the code in the `app/` directory
3. Extend the library by adding your own models, schemas, and routes
4. Configure your preferred database backend
5. Deploy to production

## Troubleshooting

**Issue: Module not found error**
- Solution: Make sure you installed all dependencies: `pip install -r requirements.txt`

**Issue: Database locked (SQLite)**
- Solution: Close all connections to the database or delete `app.db` and recreate it

**Issue: Port 8000 already in use**
- Solution: Change the port in `.env` or use: `uvicorn app.main:app --port 8001`

**Issue: CORS errors in browser**
- Solution: The API has CORS enabled by default. For production, configure allowed origins in `app/main.py`
