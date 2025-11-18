from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date, time
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Literal, List, Optional

from corrector.application.database import get_session
from corrector.application.database.tables import Document

router = APIRouter(
    prefix="/documents", 
    tags=["documents"]
    )

SessionDep = Annotated[Session, Depends(get_session)]

    
class DocumentDb(BaseModel):
    id: int | None = Field(description="Идентификатор", default=None)
    file_name: str = Field(description="Имя файла", max_length=255)
    upload_date: date = Field(description="Дата загрузки")
    upload_time: time = Field(description="Время загрузки")
    size: Decimal = Field(description="Размер в МБ", decimal_places=2)
    report_pdf_path: str = Field(description="Путь к отчёту")
    score: Decimal = Field(description="Оценка", decimal_places=1)
    analysis_time: Decimal = Field(description="Время анализа", decimal_places=2)

@router.post(path="", status_code=status.HTTP_204_NO_CONTENT)
async def create_document(body: DocumentDb, session: SessionDep):
    """Запрос: создание нового документа"""
    new_document = Document(
        file_name=body.file_name,
        upload_date=body.upload_date,
        upload_time=body.upload_time,
        size=body.size,
        report_pdf_path=body.report_pdf_path,
        score=body.score,
        analysis_time=body.analysis_time
    )
    session.add(new_document)
    session.commit()
    return None

@router.get(path="", response_model=list[DocumentDb])
async def get_documents(session: SessionDep):
    """Запрос: получение списка документов"""
    return session.scalars(select(Document)).all()

@router.get("/{document_id}")
async def get_document_by_id(document_id: int, session: SessionDep):
    """Запрос: получение документа по ID"""
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Документ не найден")
    return {"file_name": document.file_name}