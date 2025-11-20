import os
import shutil
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from corrector.application.database import get_session
from corrector.application.database.tables import Document, User
from corrector.application.http_api.controllers.auth import get_current_active_user

router = APIRouter(prefix="/documents", tags=["file-upload"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}

class FileUploadResponse(BaseModel):
    id: int = Field(description="ID документа в системе")
    file_name: str = Field(description="Системное имя файла")
    original_name: str = Field(description="Оригинальное имя файла")
    file_path: str = Field(description="Путь к файлу на сервере")
    size: float = Field(description="Размер файла в МБ")
    upload_date: datetime = Field(description="Дата и время загрузки")
    message: str = Field(description="Статус операции")
    user_id: int = Field(description="ID пользователя-владельца")

class DocumentListResponse(BaseModel):
    id: int
    file_name: str
    original_name: str
    upload_date: datetime
    size: float
    status: str
    score: Optional[float] = None

@router.post("/upload", response_model=FileUploadResponse)
async def upload_document(
    file: Annotated[UploadFile, File(description="Выберите файл для загрузки")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_session)
):
    """Загрузка документа через проводник"""
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый формат файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{current_user.id}_{timestamp}{file_extension}"
    file_path = UPLOAD_DIR / safe_filename

    try:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE//1024//1024}MB"
            )
        
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        file_size_mb = len(contents) / (1024 * 1024)
        
        db_document = Document(
            file_name=safe_filename,
            original_name=file.filename,
            upload_date=datetime.now().date(),
            upload_time=datetime.now().time(),
            size=Decimal(str(round(file_size_mb, 2))),
            user_id=current_user.id,
            status_id=1,  # Статус "загружен"
            report_pdf_path="",
            score=Decimal('0.0'),
            analysis_time=Decimal('0.0')
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return FileUploadResponse(
            id=db_document.id,
            file_name=safe_filename,
            original_name=file.filename,
            file_path=str(file_path),
            size=file_size_mb,
            upload_date=datetime.now(),
            message="Файл успешно загружен",
            user_id=current_user.id
        )
        
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )

@router.get("/download/{document_id}")
async def download_document(
    document_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_session)
):
    """Скачать документ по ID"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ не найден"
        )
    
    file_path = UPLOAD_DIR / document.file_name
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден на сервере"
        )
    
    return FileResponse(
        path=file_path,
        filename=document.original_name or document.file_name,
        media_type='application/octet-stream'
    )

@router.get("/my-documents", response_model=List[DocumentListResponse])
async def get_my_documents(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_session)
):
    """Получить список моих документов"""
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.upload_date.desc()).all()
    
    result = []
    for doc in documents:
        result.append(DocumentListResponse(
            id=doc.id,
            file_name=doc.file_name,
            original_name=getattr(doc, 'original_name', doc.file_name),
            upload_date=datetime.combine(doc.upload_date, doc.upload_time),
            size=float(doc.size),
            status="Загружен",  # Здесь нужно получить реальный статус
            score=float(doc.score) if doc.score else None
        ))
    
    return result

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_session)
):
    """Удалить документ"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ не найден"
        )

    file_path = UPLOAD_DIR / document.file_name
    if file_path.exists():
        file_path.unlink()
    
    db.delete(document)
    db.commit()
    
    return {"message": "Документ успешно удален"}