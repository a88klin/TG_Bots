from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from set.config import config
import os


os.environ["TAVILY_API_KEY"] = config.TAVILY_API_KEY.get_secret_value()


@tool
async def tavily(query: str):
    """
    Поиск ответа на любой вопрос в интернете. Используй как дополнительную информацию к своим знаниям.
    Args: query (str) - текст запроса
    return: (str) - ответ на запрос
    """
    links = '\nСсылки на доп. материалы по вашему запросу:\n'
    all_content = '\nИнформация по вашему запросу:\n\n'
    results = TavilySearchResults(max_results=1,
                                  search_depth="advanced",
                                  include_answer=False,
                                  include_raw_content=True,
                                  include_images=False)
    for answer in await results.ainvoke({"query": query}):
        # links += f"{answer['url']}\n"
        all_content += f"{answer['url']}\n{answer['content']}\n\n"
    return all_content
