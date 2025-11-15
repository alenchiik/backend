# application/api/mistake.py
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select

from corrector.application.database import get_session
from corrector.application.database import Mistake, MistakeType, Document

router = APIRouter(
    prefix="/mistakes", 
    tags=["mistakes"]
)
SessionDep = Annotated[Session, Depends(get_session)]


class MistakeDb(BaseModel):
    """Ошибка"""
    id: int | None = Field(description="Идентификатор", default=None)
    mistake_type_id: int = Field(description="ID типа ошибки")
    description: str = Field(description="Описание ошибки")
    quantity: int = Field(description="Количество ошибок", ge=1)
    critical_status: str = Field(description="Статус критичности")
    document_id: str = Field(description="ID документа")



@router.get(path='', response_model=list[MistakeDb])
async def get_mistakes(session: SessionDep):
    """Запрос: получение списка ошибок"""
    return session.execute(
        select(Mistake)
    ).scalars().all()


@router.post(path='', response_model=list[MistakeDb])
async def post_mistake(body: MistakeDb, session: SessionDep):
    """Запрос: создание новой ошибки"""
    mistake_type = session.get(MistakeType, body.mistake_type_id)
    if not mistake_type:
        raise HTTPException(status_code=404, detail="Тип ошибки не найден")

    document = session.get(Document, body.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
        
    new_mistake = Mistake(
        mistake_type_id=body.mistake_type_id,
        description=body.description,
        quantity=body.quantity,
        critical_status=body.critical_status,
        document_id=body.document_id
    )
    session.add(new_mistake)
    session.commit()
    session.refresh(new_mistake)
    return new_mistake


@router.put("/{mistake_id}",response_model=list[MistakeDb])
async def update_mistake(mistake_id:int, body: MistakeDb, session: SessionDep):
    """Запрос: обновить ошибку"""
    mistake = session.get(Mistake, mistake_id)
    if not mistake:
        raise HTTPException(status_code=404, detail="Ошибка не найдена")
    update_data = body.model_dump(exclude_unset=True, exclude={"id"})
    for key, value in update_data.items():
        setattr(mistake, key, value)
    session.commit()
    session.refresh(mistake)
    return mistake


@router.delete("/{mistake_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mistake(mistake_id: int, session: SessionDep):
    """Запрос: удалить ошибку"""
    mistake = session.get(Mistake, mistake_id)
    if not mistake:
        raise HTTPException(status_code=404, detail="Ошибка не найдена")
    session.delete(mistake)
    session.commit()
    return None