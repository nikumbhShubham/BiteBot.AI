import os
from dotenv import load_dotenv
load_dotenv()

from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_tool_calling_agent
from tools import tools

llm = ChatCohere(
    model="command-r",
    temperature=0.6,
    cohere_api_key=os.getenv("CO_API_KEY")
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a food trend advisor AI for Zomato."),
    MessagesPlaceholder(variable_name="messages"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])



memory = ConversationBufferMemory(return_messages=True)

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)