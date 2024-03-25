from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from settings import settings
import os


DB_INDEX_FILES = settings.db_index_files
os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()

db_index_vacancies = FAISS.load_local(folder_path=DB_INDEX_FILES,
                                      embeddings=OpenAIEmbeddings(),
                                      index_name='db_vacancies_index')
