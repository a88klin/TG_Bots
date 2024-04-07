from sqlalchemy import Date, BigInteger, text
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from datetime import date, datetime
from typing import Annotated


intpk = Annotated[int, mapped_column(autoincrement=True, primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                               onupdate=datetime.utcnow)]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[intpk]
    tg_user_id: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    name: Mapped[str]
    dob: Mapped[date] = mapped_column(Date)
    education: Mapped[str]
    work: Mapped[str]
    full_message: Mapped[str | None]
