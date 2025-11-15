# application/api/mistake_type.py
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select

from corrector.application.database import get_session
from corrector.application.database.tables import Mistake_Type

router = APIRouter(
    prefix="/mistake_types", 
    tags=["mistake_types"]
)

SessionDep = Annotated[Session, Depends(get_session)]


class Mistake_TypeDb(BaseModel):
    """Тип ошибки"""
    id: int | None = Field(description="Идентификатор", default=None)
    mistake_type_name: str = Field(description="Наименование типа ошибки")

@router.get(path='', response_model=list[Mistake_TypeDb])
async def get_mistake_types(session: SessionDep):
    """Запрос: получение списка типов ошибок"""
    return session.execute(
        select(Mistake_Type)
    ).scalars().all()


@router.post(path='', response_model=list[Mistake_TypeDb])
async def post_mistake_type(body: Mistake_TypeDb, session: SessionDep):
    """Запрос: создание нового типа ошибки"""
    exists = session.execute(
        select(Mistake_Type).where(Mistake_Type.mistake_type_name == body.mistake_type_name)
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Тип ошибки уже существует")
        
    new_mistake_type = Mistake_Type(
        mistake_type_name=body.mistake_type_name
    )
    session.add(new_mistake_type)
    session.commit()
    session.refresh(new_mistake_type)
    return new_mistake_type


@router.put("/{mistake_type_id}",response_model=list[Mistake_TypeDb])
async def update_mistake_type(mistake_type_id:int, body: Mistake_TypeDb, session: SessionDep):
    """Запрос: обновить тип ошибки"""
    mistake_type = session.get(Mistake_Type, mistake_type_id)
    if not mistake_type:
        raise HTTPException(status_code=404, detail="Тип ошибки не найден")
    update_data = body.model_dump(exclude_unset=True, exclude={"id"})
    for key, value in update_data.items():
        setattr(mistake_type, key, value)
    session.commit()
    session.refresh(mistake_type)
    return mistake_type


@router.delete("/{mistake_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mistake_type(mistake_type_id: int, session: SessionDep):
    """Запрос: удалить тип ошибки"""
    mistake_type = session.get(Mistake_Type, mistake_type_id)
    if not mistake_type:
        raise HTTPException(status_code=404, detail="Тип ошибки не найден")
    session.delete(mistake_type)
    session.commit()
    return None