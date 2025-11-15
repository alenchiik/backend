# application/api/document.py
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date, time
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid

from corrector.application.database import get_session
from corrector.application.database.tables import Document, User, Status

router = APIRouter(prefix="/documents", tags=["documents"])
SessionDep = Annotated[Session, Depends(get_session)]


class DocumentDb(BaseModel):
    """Документ"""
    id: str | None = Field(description="Идентификатор (UUID)", default=None)
    file_name: str = Field(description="Наименование файла")
    upload_date: date = Field(description="Дата загрузки")
    upload_time: time = Field(description="Время загрузки")
    size: Decimal = Field(description="Размер файла (MB)", decimal_places=2)
    user_id: int = Field(description="ID пользователя")
    status_id: int = Field(description="ID статуса")
    report_pdf_path: str = Field(description="Путь к PDF-отчету")
    score: Decimal = Field(description="Соответствие ГОСТу", decimal_places=1, default=Decimal("0.0"))
    analysis_time: Decimal = Field(description="Время анализа", decimal_places=2, default=Decimal("0.00"))

 

@router.get(path='', response_model=list[DocumentDb])
async def get_documents(session: SessionDep):
    """Запрос: получение списка документов"""
    return session.execute(
        select(Document)
    ).scalars().all()


@router.post(path='', response_model=list[DocumentDb])
async def post_document(body: DocumentDb, session: SessionDep):
    """Запрос: выгрузка нового документа"""
    exists = session.execute(
        select(Document).where(Document.file_name == body.file_name)
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Файл с таким именем уже загружен")

    user = session.get(User, body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    status_obj = session.get(Status, body.status_id)
    if not status_obj:
        raise HTTPException(status_code=404, detail="Статус не найден")
        
    new_document = Document(
        id=str(uuid.uuid4()),
        file_name=body.file_name,
        upload_date=body.upload_date,
        upload_time=body.upload_time,
        size=body.size,
        user_id=body.user_id,
        status_id=body.status_id,
        report_pdf_path=body.report_pdf_path,
        score=body.score,
        analysis_time=body.analysis_time
    )
    session.add(new_document)
    session.commit()
    session.refresh(new_document)
    return new_document


@router.put("/{document_id}",response_model=list[DocumentDb])
async def update_document(document_id:str, body: DocumentDb, session: SessionDep):
    """Запрос: обновить документ"""
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
    update_data = body.model_dump(exclude_unset=True, exclude={"id"})
    for key, value in update_data.items():
        setattr(document, key, value)
    session.commit()
    session.refresh(document)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str, session: SessionDep):
    """Запрос: удалить документ"""
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
    session.delete(document)
    session.commit()
    return None