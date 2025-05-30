from datetime import datetime
from notion_client import Client
import getpass
import os
from dotenv import load_dotenv
from functools import partial # Added import
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
from tools.google_tools import ( # Updated imports
    GoogleAuth,
    create_folder,
    upload_file,
    update_file_content,
    download_binary_file,
    export_google_workspace_doc,
    list_files_and_folders,
    create_google_doc
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
    drive_service = auth_instance.get_drive_service() # This will print messages internally
except HttpError as e:
    print(f"Failed to initialize Google Drive service due to HttpError: {e}")
    print("Google Drive tools will not be available for this session.")
except Exception as e:
    print(f"An unexpected error occurred during Google Drive service initialization: {e}")
    print("Google Drive tools will not be available for this session.")

if drive_service:
    print("Google Drive service initialized successfully.")
    # Removed: google_tools_instance = GoogleDriveTools(drive_service)

    # Populate with partial objects
    google_drive_tools_list = [
        partial(create_folder, drive_service=drive_service),
        partial(upload_file, drive_service=drive_service),
        partial(update_file_content, drive_service=drive_service),
        partial(download_binary_file, drive_service=drive_service),
        partial(export_google_workspace_doc, drive_service=drive_service),
        partial(list_files_and_folders, drive_service=drive_service),
        partial(create_google_doc, drive_service=drive_service),
    ]
    print("Google Drive tools added to agent's available tools.")
    # In a Streamlit app, you would typically store the drive_service in st.session_state
    # after successful authentication to avoid re-authenticating on every interaction.
    # For example:
    # if 'drive_service' not in st.session_state:
    # st.session_state.drive_service = drive_service
    # And then retrieve it when needed:
    # drive_service = st.session_state.drive_service
else:
    if not google_drive_tools_list:
        print("Google Drive service could not be initialized. Tools will not be available for this session.")


existing_tools = [
    get_env_variables,
    get_date,
    search_internet,
    get_notion_journaling_month,
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