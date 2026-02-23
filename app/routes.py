"""API routes for the REST API."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

# Create routers
user_router = APIRouter(prefix="/users", tags=["users"])
item_router = APIRouter(prefix="/items", tags=["items"])


# ========== User Routes ==========


@user_router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if user already exists
    db_user = crud.user.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    db_user = crud.user.get_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )
    return crud.user.create(db=db, obj_in=user)


@user_router.get("/", response_model=List[schemas.UserResponse])
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    """Get all users with pagination."""
    if active_only:
        users = crud.user.get_active_users(db, skip=skip, limit=limit)
    else:
        users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@user_router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID."""
    db_user = crud.user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@user_router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update a user."""
    db_user = crud.user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if email is being updated and already exists
    if user.email and user.email != db_user.email:
        existing_user = crud.user.get_by_email(db, email=user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
            )

    # Check if username is being updated and already exists
    if user.username and user.username != db_user.username:
        existing_user = crud.user.get_by_username(db, username=user.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

    return crud.user.update(db=db, db_obj=db_user, obj_in=user)


@user_router.delete("/{user_id}", response_model=schemas.MessageResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user."""
    db_user = crud.user.delete(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": f"User {user_id} deleted successfully"}


# ========== Item Routes ==========


@item_router.post("/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Create a new item."""
    return crud.item.create(db=db, obj_in=item)


@item_router.get("/", response_model=List[schemas.ItemResponse])
def read_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    available_only: bool = False,
    search: str = None,
    db: Session = Depends(get_db),
):
    """Get all items with pagination and optional search."""
    if search:
        items = crud.item.search_by_title(db, title=search, skip=skip, limit=limit)
    elif available_only:
        items = crud.item.get_available_items(db, skip=skip, limit=limit)
    else:
        items = crud.item.get_multi(db, skip=skip, limit=limit)
    return items


@item_router.get("/{item_id}", response_model=schemas.ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item by ID."""
    db_item = crud.item.get(db, id=item_id)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return db_item


@item_router.put("/{item_id}", response_model=schemas.ItemResponse)
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    """Update an item."""
    db_item = crud.item.get(db, id=item_id)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return crud.item.update(db=db, db_obj=db_item, obj_in=item)


@item_router.delete("/{item_id}", response_model=schemas.MessageResponse)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item."""
    db_item = crud.item.delete(db, id=item_id)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {"message": f"Item {item_id} deleted successfully"}
