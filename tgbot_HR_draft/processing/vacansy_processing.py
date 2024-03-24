from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from settings import settings
import os


os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()
DB_INDEX_FILES = settings.db_index_files

embed = OpenAIEmbeddings()
# # v1. Position, Skills, M.Requirements, Add.Requirements
# db_v1 = FAISS.load_local(folder_path=DB_INDEX_FILES, embeddings=embed,
#                          index_name='db_vacancies_1_index')
# # v2. Levels, WorkFormat, Location, Salary
# db_v2 = FAISS.load_local(folder_path=DB_INDEX_FILES, embeddings=embed,
#                          index_name='db_vacancies_2_index')
# # v3. 1 + 3.Project Tasks
# db_v3 = FAISS.load_local(folder_path=DB_INDEX_FILES, embeddings=embed,
#                          index_name='db_vacancies_3_index')

# v4. 1 + 2 + 3
db_index_vacancies = FAISS.load_local(folder_path=DB_INDEX_FILES, embeddings=embed,
                                      index_name='db_vacancies_4_index')
