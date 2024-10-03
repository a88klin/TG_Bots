# SQLAlchemy 2.0
from sqlalchemy import DateTime, BigInteger, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from datetime import datetime
from typing import Optional, List


# Создаем базовый класс для декларативного стиля SQLAlchemy, который будет служить основой для других моделей.
class Base(DeclarativeBase):
    pass  # Класс не содержит дополнительных атрибутов или методов


# Определяем модель таблицы пользователей
class User(Base):
    __tablename__ = 'users'  # Указываем имя таблицы в базе данных
    # Поле tg_id типа BigInteger, является первичным ключом и не будет автоматически увеличиваться
    tg_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False)
    # Поле dt типа DateTime, будет хранить дату и время
    dt: Mapped[datetime] = mapped_column(DateTime)
    # Поле user_name типа Text, может быть пустым (nullable=True)
    user_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Поле first_name типа Text, может быть пустым (nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Поле last_name типа Text, может быть пустым (nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Определяем связь с моделью Dialog, указываем, что это список диалогов для данного пользователя
    dialogs: Mapped[List["Dialog"]] = relationship(
        "Dialog", back_populates="user")  # Связываем с атрибутом user в модели Dialog


# Определяем модель таблицы диалогов
class Dialog(Base):
    __tablename__ = 'dialogues'  # Указываем имя таблицы в базе данных
    # Поле id типа BigInteger, является первичным ключом и будет автоматически увеличиваться
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    # Поле tg_id типа BigInteger, внешний ключ, ссылающийся на tg_id в таблице users
    tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.tg_id'))
    # Поле dt типа DateTime, будет хранить дату и время диалога
    dt: Mapped[datetime] = mapped_column(DateTime)
    # Поле input_text типа Text, может быть пустым (nullable=True), будет хранить входящий текст
    input_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Поле output_text типа Text, может быть пустым (nullable=True), будет хранить исходящий текст
    output_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Определяем связь с моделью User, указываем, что это пользователь, связанный с данным диалогом
    # Связываем с атрибутом dialogs в модели User
    user: Mapped["User"] = relationship("User", back_populates="dialogs")
