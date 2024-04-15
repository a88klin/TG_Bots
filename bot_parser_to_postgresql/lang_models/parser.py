from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from config import settings
import os


os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()
not_found = "Else If you didn't find it, insert line: 'Not found'."

class Resume(BaseModel):
    full_name: str = Field(
        description=f"Find the full name in the text and write it down. There should be two or three words: "
                    f"Last name, first name, maybe patronymic. {not_found}")

    dob: str = Field(
        description=f"Find the date of birth of the candidate in the text and write it down in the "
                    f"format 'dd.mm.yyyy'. {not_found}")

    position: str = Field(
        description=f"Find the position from the text that the candidate is applying for and write it down."
                    f" {not_found}")

    skills: str = Field(
        description=f"Find in the text and write down all the skills, technologies and tools that the "
                    f"candidate possesses. {not_found}")


async def to_dict_parser(text, parser_class=Resume):
    parser = JsonOutputParser(pydantic_object=parser_class)
    prompt = PromptTemplate(
        input_variables=["query"],
        template="Answer the questions from the text.\n"
                 "{format_instructions}\n"
                 "{add_content}.\n"
                 "{query}\n",
        partial_variables={"format_instructions": parser.get_format_instructions(),
                           "add_content": 'You are a professional HR.'}, )

    model = ChatOpenAI(model_name='gpt-3.5-turbo-0125', temperature=0)
    chain = prompt | model | parser
    return chain.invoke({"query": text})
