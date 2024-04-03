# pip install "motor[srv]"
import asyncio
from motor import motor_asyncio
from settings import settings


MONGODB_HOST = settings.mongodb_host

async def start_mongodb():
    mongo = motor_asyncio.AsyncIOMotorClient(MONGODB_HOST)
    db_hr = mongo.hr
    vacancies_collection = db_hr.vacancies_bot
    resumes_collection = db_hr.resumes_bot
    return resumes_collection, vacancies_collection


resumes_collection, \
vacancies_collection = asyncio.run(start_mongodb())
