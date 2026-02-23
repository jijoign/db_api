"""Database management script."""
import sys
from app.database import init_db, drop_db, engine
from app.models import Base


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    init_db()
    print("✓ Tables created successfully!")


def drop_tables():
    """Drop all database tables."""
    response = input("Are you sure you want to drop all tables? (yes/no): ")
    if response.lower() == "yes":
        print("Dropping database tables...")
        drop_db()
        print("✓ Tables dropped successfully!")
    else:
        print("Operation cancelled.")


def reset_database():
    """Reset database (drop and recreate all tables)."""
    response = input("Are you sure you want to reset the database? This will delete all data! (yes/no): ")
    if response.lower() == "yes":
        print("Resetting database...")
        drop_db()
        init_db()
        print("✓ Database reset successfully!")
    else:
        print("Operation cancelled.")


def show_tables():
    """Show all tables in the database."""
    print("\nDatabase Tables:")
    print("-" * 50)
    inspector = engine.dialect.get_table_names(bind=engine)
    for table in Base.metadata.tables.keys():
        print(f"  - {table}")
    print("-" * 50)


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Database Management Script")
        print("\nUsage: python db_manager.py [command]")
        print("\nCommands:")
        print("  create    - Create all database tables")
        print("  drop      - Drop all database tables")
        print("  reset     - Reset database (drop and recreate)")
        print("  show      - Show all tables")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "create":
        create_tables()
    elif command == "drop":
        drop_tables()
    elif command == "reset":
        reset_database()
    elif command == "show":
        show_tables()
    else:
        print(f"Unknown command: {command}")
        print("Use: create, drop, reset, or show")
        sys.exit(1)


if __name__ == "__main__":
    main()
