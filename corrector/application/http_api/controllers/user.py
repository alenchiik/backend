from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select, update, insert, delete
from sqlalchemy.orm import Session

from corrector.application.database import get_session
from corrector.application.database.tables import User

router = APIRouter(
    prefix='/users',
    tags=['users']
)

SessionDep = Annotated[Session, Depends(get_session)]

class UserDb(BaseModel):
    """Пользователь"""
    id: int | None = Field(description="Идентификатор", default=None)
    first_name: str = Field(description="Имя")
    surname_name: str = Field(description="Фамилия")
    patronomic_name: str = Field(description="Отчество")
    user_name: str = Field(description="Логин")
    password: str = Field(description="Пароль")
    
@router.get(path='', response_model=list[UserDb])
async def get_users(session: SessionDep):
    """Запрос: получение списка пользователей"""
    return session.execute(
        select(User)
    ).scalars().all()
