from config import settings
from dbase.models import Base, User
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


async def get_async_engine():
    return create_async_engine(url=settings.DATABASE_URL_asyncpg, echo=False)


async def create_db():
    engine = await get_async_engine()
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def add_user_and_massage(tg_user_id, data_dict, full_message):
    engine = await get_async_engine()
    async_session = async_sessionmaker(engine)

    try: # дата рождения, если распарсилась
        dob = datetime.strptime(data_dict['dob'], '%d.%m.%Y').date()
    except:
        dob = 'not found'

    try: # места работы, если распарсились
        work = ', '.join(data_dict['work'])
    except:
        work = 'not found'

    async with async_session() as session:
        async with session.begin():
            user = User(tg_user_id = tg_user_id,
                        name=data_dict.get('name', 'not found'),
                        dob = dob,
                        education = data_dict.get('education', 'not found'),
                        work = work,
                        full_message = full_message)
            session.add(user)
        await session.commit()


# **************************************************************************
# if __name__ == "__main__":
#     import asyncio
#     from _config import settings
#     from sqlalchemy import select
#
#
#     async def select_all():
#         engine = await get_async_engine()
#         async_session = async_sessionmaker(engine)
#
#         async with async_session() as session:
#             query = select(User)
#             result = await session.execute(query)
#             for row in result.scalars().all():
#                 print(row.updated_at, row.name)
#
#         async with engine.connect() as conn:
#             query = select(User)
#             result = await conn.execute(query)
#             for row in result.all():
#                 print(row[3:5])
#
#
#     data_dict = {
#         'name': 'Иван Иванович Пупкин',
#         'dob': '10.10.1995',
#         'education': 'Высшее экономическое образование',
#         'work': [
#             'Менеджер фирмы Альфа в 2020 году',
#             'Менеджер фирмы Бетта в 2021 году',
#             'Менеджер фирмы Тетта в 2023 году'
#         ]
#     }
#     asyncio.run(create_db())
#     asyncio.run(add_user_and_massage(123, data_dict, 'Полный текст сообщения пользователя'))
#     asyncio.run(select_all())