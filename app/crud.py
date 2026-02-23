"""CRUD operations for database models."""
from typing import Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base

# Generic CRUD type
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a single record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records with pagination."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Update an existing record."""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[ModelType]:
        """Delete a record by ID."""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


class CRUDUser(CRUDBase[models.User, schemas.UserCreate, schemas.UserUpdate]):
    """CRUD operations for User model."""

    def get_by_email(self, db: Session, email: str) -> Optional[models.User]:
        """Get user by email."""
        return db.query(models.User).filter(models.User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[models.User]:
        """Get user by username."""
        return db.query(models.User).filter(models.User.username == username).first()

    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
        """Get all active users."""
        return (
            db.query(models.User)
            .filter(models.User.is_active.is_(True))
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDItem(CRUDBase[models.Item, schemas.ItemCreate, schemas.ItemUpdate]):
    """CRUD operations for Item model."""

    def get_available_items(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[models.Item]:
        """Get all available items."""
        return (
            db.query(models.Item)
            .filter(models.Item.is_available.is_(True))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_by_title(
        self, db: Session, title: str, skip: int = 0, limit: int = 100
    ) -> List[models.Item]:
        """Search items by title."""
        return (
            db.query(models.Item)
            .filter(models.Item.title.contains(title))
            .offset(skip)
            .limit(limit)
            .all()
        )


# Create instances
user = CRUDUser(models.User)
item = CRUDItem(models.Item)
