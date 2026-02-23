"""Example usage of the REST API library."""
import requests
import json


# API base URL
BASE_URL = "http://localhost:8000/api"


def print_response(title, response):
    """Print formatted response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def main():
    """Demonstrate API usage."""
    print("REST API Library - Example Usage")
    print("Make sure the server is running: python run.py")
    print()
    
    # Create a user
    print("\n1. Creating a new user...")
    user_data = {
        "username": "alice",
        "email": "alice@example.com",
        "full_name": "Alice Johnson",
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print_response("Create User", response)
    user_id = response.json().get("id")
    
    # Get all users
    print("\n2. Getting all users...")
    response = requests.get(f"{BASE_URL}/users/")
    print_response("Get All Users", response)
    
    # Get specific user
    print(f"\n3. Getting user {user_id}...")
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    print_response(f"Get User {user_id}", response)
    
    # Update user
    print(f"\n4. Updating user {user_id}...")
    update_data = {
        "full_name": "Alice Smith",
        "is_active": True
    }
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data)
    print_response(f"Update User {user_id}", response)
    
    # Create an item
    print("\n5. Creating a new item...")
    item_data = {
        "title": "Gaming Laptop",
        "description": "High-performance gaming laptop with RTX graphics",
        "price": 149999,  # Price in cents ($1499.99)
        "is_available": True
    }
    response = requests.post(f"{BASE_URL}/items/", json=item_data)
    print_response("Create Item", response)
    item_id = response.json().get("id")
    
    # Get all items
    print("\n6. Getting all items...")
    response = requests.get(f"{BASE_URL}/items/")
    print_response("Get All Items", response)
    
    # Search items
    print("\n7. Searching items by title...")
    response = requests.get(f"{BASE_URL}/items/?search=laptop")
    print_response("Search Items", response)
    
    # Get available items only
    print("\n8. Getting available items only...")
    response = requests.get(f"{BASE_URL}/items/?available_only=true")
    print_response("Get Available Items", response)
    
    # Update item
    print(f"\n9. Updating item {item_id}...")
    update_data = {
        "price": 139999,  # New price: $1399.99
        "is_available": True
    }
    response = requests.put(f"{BASE_URL}/items/{item_id}", json=update_data)
    print_response(f"Update Item {item_id}", response)
    
    # Pagination example
    print("\n10. Testing pagination...")
    response = requests.get(f"{BASE_URL}/users/?skip=0&limit=5")
    print_response("Paginated Users", response)
    
    print("\n" + "="*60)
    print("Example completed successfully!")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to the API server.")
        print("Please make sure the server is running:")
        print("  python run.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
