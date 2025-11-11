import json
from datetime import date, time
from decimal import Decimal
from sqlalchemy import MetaData, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase



class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s", #индексы
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s", #проверки?
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
    user_name: Mapped[str] = mapped_column(unique=True, nullable=False, comment="Логин")
    password: Mapped[str] = mapped_column(nullable=False, comment="Пароль")
    #tg_username: Mapped[str] = mapped_column(nullable=True, comment="TG") # нужно ли и можно ли
    #is_tg_subscribed:Mapped[bool] = mapped_column(nullable=True, default = False, comment="Есть ли подписка на канал")

# class Status(Base):
#     __tablename__ = "status"
#     __table_args__ = {"comment": "Статусы"}

#     id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор")
#     status_name: Mapped[str] = mapped_column(unique=True, comment="Вид статуса")    

# class Document(Base):
#     __tablename__ = "documents"
#     __table_args__ = {"comment": "Документы"}

#     id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор")
#     user_id: Mapped[int] = mapped_column(
#         ForeignKey("user.id"),
#         nullable=False, 
#         comment="Связь с User"
#     )
#     status_id: Mapped[int] = mapped_column(
#         ForeignKey("status.id"),
#         nullable=False, 
#         comment="Связь с Status"
#     )
#     check_report_id: Mapped[int] = mapped_column(
#         ForeignKey("check_report.id"),
#         nullable=False, 
#         comment="Связь с CheckReports"
#     )
#     file_name: Mapped[str] = mapped_column(unique=True,nullable=False, comment="Имя файла")
#     upload_date: Mapped[date] = mapped_column(nullable=False, comment="Дата загрузки")
#     upload_time: Mapped[time] = mapped_column(nullable=False, comment="Время загрузки")
#     size: Mapped[float] = mapped_column(float,nullable=False,comment="Размер файла в МБ")
    
# class Ratings(Base):
#     __tablename__ = "rating"
#     __table_args__ = {"comment": "Оценки"}

#     id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор(1-5)")
#     rating_name: Mapped[str] = mapped_column(unique=True, comment="Вид статуса")
    
# class Reviews(Base):
#     __tablename__ = "review"
#     __table_args__ = {"comment": "Отзамвы"}

#     id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор")
#     user_id: Mapped[int] = mapped_column(
#         ForeignKey("user.id"),
#         nullable=False, 
#         comment="Связь с User"
#     )
#     rating_id:Mapped[int] = mapped_column(
#         ForeignKey("rating.id"),
#         nullable=False, 
#         comment="Связь с Rating"
#     )
#     review_text:Mapped[str] = mapped_column(unique=True, comment="Вид статуса")
#     create_at: Mapped[date] = mapped_column(nullable=False, comment="Дата создания")

# class CheckReports(Base):
#     __tablename__ = "rating"
#     __table_args__ = {"comment": "Отчеты о проверке"}
    
#     id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор")
#     document_id: Mapped[int] = mapped_column(
#         ForeignKey("document.id"),
#         nullable=False, 
#         comment="Связь с Document"
#     )
#     check_type_id: Mapped[int] = mapped_column(
#         ForeignKey("check_report.id"),
#         nullable=False, 
#         comment="Связь с CheckTypes"
#     )
#     file_type_id: Mapped[int] = mapped_column(
#         ForeignKey("check_report.id"),
#         nullable=False, 
#         comment="Связь с FileTypes"
#     )
#     report_date: Mapped[date] = mapped_column(nullable=False, comment="Дата выполнения отчета")
#     report_pdf_url:Mapped[str] = mapped_column(unique=True, comment="Ссылка на сформированный pdf отчет")
#     score:Mapped[Decimal] = mapped_column(Decimal(precision=3,scale=1),nullable=False,comment="Общий балл")
#     analysis_time:Mapped[Decimal] = mapped_column(Decimal(precision=5,scale=2),nullable=False,comment="Время анализа")
#     overall_compliance:Mapped[Decimal] = mapped_column(Decimal(precision=5,scale=2),nullable=False,comment="% соответствия")
#     recommendations:Mapped[str] = mapped_column( nulable=True, comment="Рекоменадации")
