from datetime import datetime
from notion_client import Client
import getpass
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from modules.notion_retrieval import (
    get_env_variables, 
    get_date, search_internet, 
    get_notion_journaling_month, 
    get_notion_journaling_day, 
)
from memory.vector import (
    add_new_memory,
    find_in_memory_user_data,
    find_in_memory_notion_data,
    find_in_memory,
    get_user_memories,
    get_q2_2025_goals
)
from tools.basic_tools import *
from prompts.system_prompts import jarvis_main_prompt

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

checkpoint = MemorySaver()
config = {"configurable": {"thread_id": "abc123"},
          "recursion_limit": 100}

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    
)

personal_agent = create_react_agent(
    model=llm,
    name="Jarvis",
    tools=[
        get_env_variables, 
        get_date, 
        search_internet, 
        get_notion_journaling_month, 
        get_env_variables, 
        get_notion_journaling_day, 
        save_output,
        list_files,
        load_file_content,
        open_files,
        add_new_memory,
        find_in_memory_user_data,
        find_in_memory_notion_data,
        find_in_memory,
        get_q2_2025_goals
    ],
    prompt=jarvis_main_prompt,
    checkpointer=checkpoint
)

memory = get_user_memories()
files = load_output_files()
system_memory = SystemMessage(content=f'This is all you know about the user: \n{memory}')
file_history = HumanMessage(content=f"These are the files you have at your disposal, for your context, to know in case the user asks anything related to this: {files}")


if __name__ == '__main__':
    print("--------------Chat with AI-----------------")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "q":
            break
        for step in personal_agent.stream({
            "messages":[
                system_memory,
                file_history,
                HumanMessage(content=user_input)
            ]
        }, config, stream_mode="messages"):
            # step["messages"][-1].pretty_print()
            print(f"this is one step: {step}")
    
    # first check if its an agent or tool response
    # then if it is agent, check within messsages for the last message
    # and check whether there is .content and if there is data for .tool_calls 
    # if not, it is a normal agent message so display the content
    # if it has .tool_calls then display the tool it is calling
    # following up there should be a tool call message of which you can display the content
    # then finally display again the agent content