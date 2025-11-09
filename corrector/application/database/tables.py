import json
from datetime import date, time

from sqlalchemy import MetaData, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase



class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "Пользователи"}

    id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор")
    first_name: Mapped[str] = mapped_column(nullable=False, comment="Имя")
    surname_name: Mapped[str] = mapped_column(nullable=False, comment="Фамилия")
    patronomic_name: Mapped[str] = mapped_column(nullable=False, comment="Отчество")
    user_name: Mapped[str] = mapped_column(nullable=False, comment="Логин")
    password: Mapped[str] = mapped_column(nullable=False, comment="Пароль")