"""
Повторно используемые классы и миксины
"""
from typing import TypeVar, Generic
from sqlalchemy.orm import Session
from app.shared.base_model import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class CRUDMixin(Generic[ModelType]):
    """Базовый CRUD миксин для репозиториев"""
    
    def __init__(self, model: type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: int) -> ModelType | None:
        """Получить по ID"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Получить список с пагинацией"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: dict) -> ModelType:
        """Создать новый объект"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: ModelType, obj_in: dict) -> ModelType:
        """Обновить объект"""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> ModelType | None:
        """Удалить объект"""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

