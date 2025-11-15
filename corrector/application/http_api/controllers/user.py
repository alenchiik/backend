from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from fastapi import HTTPException
from fastapi import status
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
    tg_username:str = Field(description="Telegram")
    is_tg_subscribed:bool = Field(description="Проверка подписки",default=False)
    is_admin:bool = Field(description="Проверка на админа")
    theme:str = Field(description="Тема интерфейса Dark/Light")
    notification_push = Field(description="Уведомления в браузере ON/OFF")


@router.get(path='', response_model=list[UserDb])
async def get_users(session: SessionDep):
    """Запрос: получение списка пользователей"""
    return session.execute(
        select(User)
    ).scalars().all()

@router.post(path='',response_model=list[UserDb])
async def post_user(body: UserDb, session: SessionDep):
    """Запрос: создание нового пользователя"""
    exists = session.execute( #типа проверка на дубл
        select(User).where(
            (User.user_name == body.user_name)
        )
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким логином уже существует"
        )
    new_user = User(
        first_name=body.first_name,
        surname_name=body.surname_name,
        patronomic_name=body.patronomic_name,
        user_name=body.user_name,
        password=body.password,
        tg_username=body.tg_username,
        is_tg_subscribed=body.is_tg_subscribe,
        is_admin=body.is_admin,
        theme=body.theme,
        notification_push=body.notification_push
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return UserDb.from_orm(new_user)

@router.put("/{user_id}",response_model=UserDb)
async def update_user(user_id:int, body: UserDb, session: SessionDep):
    """Запрос: обновить пользователя"""
    user = session.get(User,user_id)
    if not user:
        raise HTTPException(status_code = 404, detail = "Пользователь не найден")
    update_data = body.model_dump(exclude_unset = True, exclude = {"id","password"})
    for key, value in update_data.items():
        setattr(user, key, value)
    if body.password and body.password !=user.password:
        user.password = body.password
    session.commit()
    session.refresh(user)
    return UserDb.from_orm(user)

@router.delete("/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session: SessionDep):
    """Запрос: удалить пользователя"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользоваnь не найден")
    session.delete(user)
    session.commit()
    return None