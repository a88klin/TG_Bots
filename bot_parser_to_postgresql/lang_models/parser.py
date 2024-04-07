from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from typing import List
from config import settings
import os


add_string = "If you haven't found the information you need, insert the line: 'not found'. "
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()


class About(BaseModel):
    name: str = Field(description=f"Write the author's full name. {add_string}")
    dob: str = Field(description=f"Write down the author's date of birth. {add_string}")
    education: str = Field(description=f"Describes the author's educational experience / educational background. {add_string}")
    work: List[str] = Field(description=f"Describes the author's job experience / job background. {add_string}")


async def to_dict_parser(query, class_parser=About):
    parser = JsonOutputParser(pydantic_object=class_parser)
    prompt = PromptTemplate(
        input_variables=["query"],
        template="Answer the user query.\n"
                 "{format_instructions}\n"
                 "{add_content}.\n"
                 "{query}\n",
        partial_variables={"format_instructions": parser.get_format_instructions(),
                           "add_content": add_string}, )
    model = ChatOpenAI(temperature=0)
    chain = prompt | model | parser
    return chain.invoke({"query": query})
