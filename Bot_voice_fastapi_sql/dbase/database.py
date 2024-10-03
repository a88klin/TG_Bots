from set.config import config  # Импортируем настройки из конфигурационного файла
# Импортируем базовую модель и модель пользователя из базы данных
from dbase.models import Base, User, Dialog
from datetime import datetime  # Импортируем класс datetime для работы с датами
# функции для работы с асинхронным SQLAlchemy
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


# Асинхронная функция для получения асинхронного движка базы данных
async def get_async_engine():
    # Создаем и возвращаем асинхронный движок с URL из настроек
    return create_async_engine(url=config.DATABASE_URL_asyncpg, echo=False)


# Асинхронная функция для создания базы данных
async def create_db():
    engine = await get_async_engine()  # Получаем асинхронный движок базы данных
    async with engine.begin() as conn:  # Открываем асинхронный контекст для начала транзакции
        # Удаляем все таблицы из базы данных
        await conn.run_sync(Base.metadata.drop_all)
        # Создаем все таблицы на основе метаданных
        await conn.run_sync(Base.metadata.create_all)


# Асинхронная функция для добавления данных пользователя
async def add_user(data_dict):
    engine = await get_async_engine()  # Получаем асинхронный движок базы данных
    # Создаем асинхронный сессионный объект
    async_session = async_sessionmaker(engine)

    async with async_session() as session:  # Открываем асинхронный контекст для сессии
        async with session.begin():  # Начинаем транзакцию в сессии
            user = User(tg_id=data_dict.get('tg_id'),
                        dt=datetime.now(),
                        user_name=data_dict.get('user_name', ''),
                        first_name=data_dict.get('first_name', ''),
                        last_name=data_dict.get('last_name', ''))
            session.add(user)  # Добавляем пользователя в сессию
        await session.commit()  # Подтверждаем изменения в базе данных


# Асинхронная функция для добавления диалогов
async def add_dialog(data_dict):
    engine = await get_async_engine()  # Получаем асинхронный движок базы данных
    # Создаем асинхронный сессионный объект
    async_session = async_sessionmaker(engine)

    async with async_session() as session:  # Открываем асинхронный контекст для сессии
        async with session.begin():  # Начинаем транзакцию в сессии
            user = Dialog(tg_id=data_dict.get('tg_id'),
                          dt=datetime.now(),
                          input_text=data_dict.get(
                              'input_text', '').replace('\n', '\\n'),
                          output_text=data_dict.get('output_text', '').replace('\n', '\\n'))
            session.add(user)  # Добавляем пользователя в сессию
        await session.commit()  # Подтверждаем изменения в базе данных
