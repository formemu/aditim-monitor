"""API routes for blanks"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.blank import ModelBlank
from ..schemas.blank import SchemaBlankCreate, SchemaBlankUpdate, SchemaBlankResponse, SchemaBlankBulkCreate
from ..events import notify_clients

router = APIRouter(prefix="/api", tags=["blank"], redirect_slashes=False)


@router.get("/blank", response_model=List[SchemaBlankResponse])
def get_list_blank(db: Session = Depends(get_db)):
    """Получить все заготовки"""
    return db.query(ModelBlank).order_by(ModelBlank.order.desc(), ModelBlank.id.desc()).all()


@router.get("/blank/order/next")
def get_next_order_number(db: Session = Depends(get_db)):
    """Получить следующий номер заказа"""
    max_order = db.query(ModelBlank.order).order_by(ModelBlank.order.desc()).first()
    next_order = 1 if not max_order or not max_order[0] else max_order[0] + 1
    return {"next_order": next_order}


@router.get("/blank/{blank_id}", response_model=SchemaBlankResponse)
def get_blank(blank_id: int, db: Session = Depends(get_db)):
    """Получить заготовку по ID"""
    blank = db.query(ModelBlank).filter(ModelBlank.id == blank_id).first()
    if not blank:
        raise HTTPException(status_code=404, detail="Заготовка не найдена")
    return blank


@router.post("/blank", response_model=SchemaBlankResponse)
def create_blank(blank_data: SchemaBlankCreate, db: Session = Depends(get_db)):
    """Создать новую заготовку"""
    new_blank = ModelBlank(**blank_data.model_dump())
    db.add(new_blank)
    db.commit()
    db.refresh(new_blank)
    notify_clients("table", "blank", "created")
    return new_blank


@router.post("/blank/bulk", response_model=List[SchemaBlankResponse])
def create_list_blank(blank_data: SchemaBlankBulkCreate, db: Session = Depends(get_db)):
    """Создать несколько заготовок одного типа
    
    Принимает данные заготовки и количество (quantity).
    Создаёт указанное количество заготовок с одинаковыми параметрами,
    но каждая с уникальным ID.
    """
    quantity = blank_data.quantity
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Количество должно быть больше 0")
    
    if quantity > 100:
        raise HTTPException(status_code=400, detail="Максимальное количество за раз: 100")
    
    # Убираем quantity из данных перед созданием записей
    blank_dict = blank_data.model_dump(exclude={'quantity'})
    
    # Создаём указанныйное количество заготовок
    list_new_blank = []
    for _ in range(quantity):
        new_blank = ModelBlank(**blank_dict)
        db.add(new_blank)
        list_new_blank.append(new_blank)
    
    db.commit()
    
    # Обновляем все созданные записи для получения ID
    for blank in list_new_blank:
        db.refresh(blank)
    
    notify_clients("table", "blank", "created")
    return list_new_blank


@router.patch("/blank/{blank_id}", response_model=SchemaBlankResponse)
def update_blank(blank_id: int, blank_data: SchemaBlankUpdate, db: Session = Depends(get_db)):
    """Обновить заготовку"""
    blank = db.query(ModelBlank).filter(ModelBlank.id == blank_id).first()
    if not blank:
        raise HTTPException(status_code=404, detail="Заготовка не найдена")
    
    for key, value in blank_data.model_dump(exclude_unset=True).items():
        setattr(blank, key, value)
    
    db.commit()
    db.refresh(blank)
    notify_clients("table", "blank", "updated")
    return blank


@router.delete("/blank/{blank_id}")
def delete_blank(blank_id: int, db: Session = Depends(get_db)):
    """Удалить заготовку"""
    blank = db.query(ModelBlank).filter(ModelBlank.id == blank_id).first()
    if not blank:
        raise HTTPException(status_code=404, detail="Заготовка не найдена")
    
    db.delete(blank)
    db.commit()
    notify_clients("table", "blank", "deleted")
    return {"message": "Заготовка успешно удалена"}
