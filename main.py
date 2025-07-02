from datetime import datetime
from notion_client import Client
import getpass
import os
from dotenv import load_dotenv
# Removed: from functools import partial
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool

from modules.notion_retrieval import (
    get_env_variables, 
    get_date, 
    get_notion_journaling_month, 
    get_notion_journaling_day, 
    get_notion_ideas
)
from memory.vector import (
    add_new_memory,
    find_in_memory_user_data,
    find_in_memory_notion_data,
    find_in_memory,
    get_user_memories,
    get_q2_2025_goals
)
from tools.basic_tools import * # This should import delete_local_file
from tools.google_tools import (
    GoogleAuth,
    create_folder_tool_factory,
    upload_file_tool_factory,
    update_file_content_tool_factory,
    download_binary_file_tool_factory,
    export_google_workspace_doc_tool_factory,
    list_files_and_folders_tool_factory,
    create_google_doc_tool_factory
)
from googleapiclient.errors import HttpError
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

# --- Initialize Google Drive Tools ---
print("Attempting to initialize Google Drive tools...")
google_drive_tools_list = []
drive_service = None
try:
    auth_instance = GoogleAuth()
    drive_service = auth_instance.get_drive_service()
except HttpError as e:
    print(f"Failed to initialize Google Drive service due to HttpError: {e}")
    print("Google Drive tools will not be available for this session.")
except Exception as e:
    print(f"An unexpected error occurred during Google Drive service initialization: {e}")
    print("Google Drive tools will not be available for this session.")

if drive_service:
    print("Google Drive service initialized successfully.")

    agent_facing_create_folder = create_folder_tool_factory(drive_service)
    agent_facing_upload_file = upload_file_tool_factory(drive_service)
    agent_facing_update_file_content = update_file_content_tool_factory(drive_service)
    agent_facing_download_binary_file = download_binary_file_tool_factory(drive_service)
    agent_facing_export_google_workspace_doc = export_google_workspace_doc_tool_factory(drive_service)
    agent_facing_list_files_and_folders = list_files_and_folders_tool_factory(drive_service)
    agent_facing_create_google_doc = create_google_doc_tool_factory(drive_service)

    tool_create_folder = StructuredTool.from_function(
        func=agent_facing_create_folder,
        name="create_google_drive_folder",
        description=agent_facing_create_folder.__doc__
    )
    tool_upload_file = StructuredTool.from_function(
        func=agent_facing_upload_file,
        name="upload_file_to_google_drive",
        description=agent_facing_upload_file.__doc__
    )
    tool_update_file_content = StructuredTool.from_function(
        func=agent_facing_update_file_content,
        name="update_google_drive_file_content",
        description=agent_facing_update_file_content.__doc__
    )
    tool_download_binary_file = StructuredTool.from_function(
        func=agent_facing_download_binary_file,
        name="download_google_drive_binary_file",
        description=agent_facing_download_binary_file.__doc__
    )
    tool_export_google_workspace_doc = StructuredTool.from_function(
        func=agent_facing_export_google_workspace_doc,
        name="export_google_drive_workspace_document",
        description=agent_facing_export_google_workspace_doc.__doc__
    )
    tool_list_files_and_folders = StructuredTool.from_function(
        func=agent_facing_list_files_and_folders,
        name="list_google_drive_files_and_folders",
        description=agent_facing_list_files_and_folders.__doc__
    )
    tool_create_google_doc = StructuredTool.from_function(
        func=agent_facing_create_google_doc,
        name="create_empty_google_doc",
        description=agent_facing_create_google_doc.__doc__
    )

    google_drive_tools_list = [
        tool_create_folder,
        tool_upload_file,
        tool_update_file_content,
        tool_download_binary_file,
        tool_export_google_workspace_doc,
        tool_list_files_and_folders,
        tool_create_google_doc,
    ]
    print("Google Drive tools (from factories) wrapped with StructuredTool and added to agent's available tools.")
else:
    if not google_drive_tools_list:
        print("Google Drive service could not be initialized. Tools will not be available for this session.")


existing_tools = [
    get_env_variables,
    get_date,
    search_internet,
    get_notion_journaling_month,
    get_notion_journaling_day,
    get_notion_ideas,
    save_output,
    list_files,
    load_file_content,
    open_files,
    add_new_memory,
    find_in_memory_user_data,
    find_in_memory_notion_data,
    find_in_memory,
    get_q2_2025_goals,
    delete_local_file # Added new tool here
]

all_tools = existing_tools + google_drive_tools_list

personal_agent = create_react_agent(
    model=llm,
    name="Jarvis",
    tools=all_tools,
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