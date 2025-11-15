from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date

from corrector.application.database  import get_session
from corrector.application.database.tables  import Review, User

router = APIRouter(
    prefix="/reviews", 
    tags=["reviews"]
)

SessionDep = Annotated[Session, Depends(get_session)]


class ReviewDb(BaseModel):
    """Отзыв"""
    id: int | None = Field(description="Идентификатор", default=None)
    user_id: int = Field(description="ID пользователя")
    mark: int = Field(description="Оценка от 1 до 5", ge=1, le=5)
    review_text: str | None = Field(description="Текст отзыва", default=None)
    created_at: date = Field(description="Дата создания")

@router.post(path="", response_model=list[ReviewDb])
async def create_review(body: ReviewDb, session: SessionDep):
    """Запрос: создание отзыва"""
    # Проверка существования пользователя
    user = await session.get(User, body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    new_review = Review(
        user_id=body.user_id,
        mark=body.mark,
        review_text=body.review_text,
        created_at=date.today()
    )
    session.add(new_review)
    session.commit()
    session.refresh(new_review)
    return new_review


@router.get("/user/{user_id}", response_model=list[ReviewDb])
async def get_user_reviews(user_id: int, session: SessionDep):
    """Запрос: получить отзыв"""
    return (await session.execute(
        select(Review).where(Review.user_id == user_id)
    )).scalars().all()

@router.put("/{review_id}",response_model=list[ReviewDb])
async def update_review(review_id:int, body: ReviewDb, session: SessionDep):
    """Запрос: обновить отзыв"""
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    update_data = body.model_dump(exclude_unset=True, exclude={"id"})
    for key, value in update_data.items():
        setattr(review, key, value)
    session.commit()
    session.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: int, session: SessionDep):
    """Запрос: удалить отзыв"""
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    session.delete(review)
    session.commit()
    return None