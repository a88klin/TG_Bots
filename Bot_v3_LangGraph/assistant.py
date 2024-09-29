from datetime import datetime
from typing import Annotated
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Literal
import functools
import operator
import os
from typing import Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import create_react_agent
from set.config import config
from calendar_new import create_event, get_events, delete_event
from notepad import save_note, get_row
from weather import get_weather, get_weather_forecast
from expert import tavily
from pprint import pprint as pp


os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY.get_secret_value()
os.environ["LANGCHAIN_API_KEY"] = config.LANGCHAIN_API_KEY.get_secret_value()
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_TRACING_V2"] = "true"


llm = ChatOpenAI(model="gpt-4o-mini")
members = ["Calendar", "Notepad", "Weather", "Expert"]

system_prompt = ("""Ты - руководитель, которому поручено управлять следующими агентами: {members}.
# Calendar - записывает мероприятия в КАЛЕНДАРЬ пользователя, или получает информацию о записях из
календаря, или удаляет записи из календаря.
# Notepad - записывает заметки пользователя в БЛОКНОТ и выводит последнюю запись. По запросу может
выводить любую запись (строку) из блокнота по номеру.
# Weather - выводит информацию о ПОГОДЕ в конкретном городе в настоящий момент времени или
прогноз погоды в конкретном городе на конкретную дату и время.
# Expert - это консультант, который отвечает на любые запросы пользователя, кроме ответов Calendar, Notepad, Weather.
---------------------------------------------------------------
Учитывая следующий запрос пользователя, ответь, кто из агентов должен действовать следующим.
Каждый агент будет выполнять задание и отвечать, указывая результаты и статус.
По окончании ответь словом FINISH""")
# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed
options = ["FINISH"] + members


class routeResponse(BaseModel):
    next: Literal["FINISH", "Calendar", "Notepad", "Weather", "Expert"]


prompt = ChatPromptTemplate.from_messages(
    [("system", system_prompt),
     MessagesPlaceholder(variable_name="messages"),
     ("system",
      "Given the conversation above, who should act next? "
      "Or should we FINISH? Select one of: {options}")]
).partial(options=str(options), members=", ".join(members))


async def supervisor_agent(state):
    supervisor_chain = prompt | llm.with_structured_output(routeResponse)
    result = await supervisor_chain.ainvoke(state)
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nsupervisor_agent(): {result}\n")
    return result


async def agent_node(state, agent, name):
    result = await agent.ainvoke(state)
    return {"messages": [HumanMessage(content=result["messages"][-1].content, name=name)]}


# -----------------------------------------------------------------------------------------
# Calendar
calendar_prompt = f"""
Текущая дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M')}.
Если пользователь указал дату - число дня и не указал месяц - бери текущий месяц.
Если пользователь указал дату, но не указал год, бери текущий год.
Если для записи мероприятия пользователь указал единственное время - это будет время начала мероприятия
продолжительноятью один час, т.е. время окончания + 1 час от начала"""
calendar_agent = create_react_agent(llm, tools=[create_event, get_events, delete_event],
                                    state_modifier=calendar_prompt)
calendar_node = functools.partial(
    agent_node, agent=calendar_agent, name="Calendar")


# Notepad
notepad_prompt = """Возьми заметку пользователя для записи в блокнот. Исправь ошибки, если есть.
Потом запиши в блокнот. Выведи дату, время и последнюю запись"""
notepad_agent = create_react_agent(llm, tools=[save_note, get_row],
                                   state_modifier=notepad_prompt)
notepad_node = functools.partial(
    agent_node, agent=notepad_agent, name="Notepad")


# Weather
weather_agent = create_react_agent(
    llm, tools=[get_weather, get_weather_forecast])
weather_node = functools.partial(
    agent_node, agent=weather_agent, name="Weather")


# Expert
tavily_prompt = 'Подключи и дополнительно выведи в ответе ссылки результатов поиска от tavily по теме запроса'
expert_agent = create_react_agent(
    llm, tools=[tavily], state_modifier=tavily_prompt)
expert_node = functools.partial(agent_node, agent=expert_agent, name="Expert")


# ------------------------------------------------------------------------------------------
class AgentState(TypedDict):  # The agent state is the input to each node in the graph
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str


workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("Calendar", calendar_node)
workflow.add_node("Notepad", notepad_node)
workflow.add_node("Weather", weather_node)
workflow.add_node("Expert", expert_node)


for member in members:
    # We want our workers to ALWAYS "report back" to the supervisor when done
    workflow.add_edge(member, "supervisor")
# The supervisor populates the "next" field in the graph state
# which routes to a node or finishes
conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
workflow.add_conditional_edges(
    "supervisor", lambda x: x["next"], conditional_map)
# Finally, add entrypoint
workflow.add_edge(START, "supervisor")

memory = dict()
graph = workflow.compile()


async def clear_memory(tgid):
    global memory
    if tgid in memory:
        # pp(memory[tgid].get({"configurable": {"thread_id": "1"}}))
        del memory[tgid]
        memory[tgid] = MemorySaver()
        return 'The context memory has been cleared'
    else:
        return f'There are no entries in the context memory'


async def get_answer(text_msg, tgid, system_message: str = ''):
    query = HumanMessage(content=text_msg)
    if tgid not in memory:
        memory[tgid] = MemorySaver()
    graph = workflow.compile(checkpointer=memory[tgid])
    result = await graph.ainvoke({"messages": [system_message, query]},
                                 {"configurable": {"thread_id": "1"}})
    return result["messages"][-1].content
