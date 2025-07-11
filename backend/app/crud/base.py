"""
Base CRUD operations
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session, Query
from sqlalchemy import desc

from app.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base CRUD class with default methods"""
    
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and optional ordering"""
        query = db.query(self.model)

        # Add ordering if specified, default to updated_at desc if available
        if order_by:
            if hasattr(self.model, order_by):
                query = query.order_by(getattr(self.model, order_by))
        elif hasattr(self.model, 'updated_at'):
            query = query.order_by(desc(self.model.updated_at))
        elif hasattr(self.model, 'created_at'):
            query = query.order_by(desc(self.model.created_at))

        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record"""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> ModelType:
        """Delete a record"""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def count(self, db: Session) -> int:
        """Count total records"""
        return db.query(self.model).count()

    def exists(self, db: Session, *, id: Any) -> bool:
        """Check if record exists"""
        return db.query(self.model).filter(self.model.id == id).first() is not None

    def get_by_field(
        self,
        db: Session,
        *,
        field_name: str,
        field_value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get records by a specific field value"""
        if not hasattr(self.model, field_name):
            raise ValueError(f"Model {self.model.__name__} does not have field {field_name}")

        query = db.query(self.model).filter(getattr(self.model, field_name) == field_value)

        # Add default ordering
        if hasattr(self.model, 'updated_at'):
            query = query.order_by(desc(self.model.updated_at))
        elif hasattr(self.model, 'created_at'):
            query = query.order_by(desc(self.model.created_at))

        return query.offset(skip).limit(limit).all()

    def bulk_create(self, db: Session, *, objs_in: List[CreateSchemaType]) -> List[ModelType]:
        """Create multiple records efficiently"""
        db_objs = []
        for obj_in in objs_in:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)  # type: ignore
            db_objs.append(db_obj)

        db.add_all(db_objs)
        db.commit()

        # Refresh all objects
        for db_obj in db_objs:
            db.refresh(db_obj)

        return db_objs
