# application/api/status.py
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select

from corrector.application.database import get_session
from corrector.application.database.tables import Status

router = APIRouter(
    prefix="/statuses", 
    tags=["statuses"]
    )

SessionDep = Annotated[Session, Depends(get_session)]


class StatusDb(BaseModel):
    """Статус"""
    id: int | None = Field(description="Идентификатор", default=None)
    status_name: str = Field(description="Наименование статуса", max_length=50)


@router.get(path='', response_model=list[StatusDb])
async def get_statuses(session: SessionDep):
    """Запрос: получение списка статусов"""
    return session.execute(
        select(Status)
    ).scalars().all()


@router.post(path='', response_model=list[StatusDb])
async def post_status(body: StatusDb, session: SessionDep):
    """Запрос: создание нового статуса"""
    exists = session.execute(
        select(Status).where(Status.status_name == body.status_name)
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Статус уже существует")
        
    new_status = Status(
        status_name=body.status_name
    )
    session.add(new_status)
    session.commit()
    session.refresh(new_status)
    return new_status


@router.put("/{status_id}",response_model=list[StatusDb])
async def update_status(status_id:int, body: StatusDb, session: SessionDep):
    """Запрос: обновить статус"""
    doc_status = session.get(Status, status_id)
    if not doc_status:
        raise HTTPException(status_code=404, detail="Статус не найден")
    update_data = body.model_dump(exclude_unset=True, exclude={"id"})
    for key, value in update_data.items():
        setattr(doc_status, key, value)
    session.commit()
    session.refresh(doc_status)
    return doc_status


@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_status(status_id: int, session: SessionDep):
    """Запрос: удалить статус"""
    doc_status = session.get(Status, status_id)
    if not doc_status:
        raise HTTPException(status_code=404, detail="Статус не найден")
    session.delete(doc_status)
    session.commit()
    return None