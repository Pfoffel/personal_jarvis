from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.tools import tool
import threading
from structure_schema.basic_structures import NewMemory
from uuid import uuid4
from datetime import datetime
import os
import json

LOG = "memory/log.json"
log_lock = threading.Lock()

embedding_model = OllamaEmbeddings(model="mxbai-embed-large")

persist_directory = "memory/chroma_store_new"
os.makedirs(persist_directory, exist_ok=True)

vectorstore = Chroma(
    collection_name="agent_memory",
    embedding_function=embedding_model,
    persist_directory=persist_directory
)

# vectorstore_notion = Chroma(
#     collection_name="notion_db",
#     embedding_function=embedding_model,
#     persist_directory=persist_directory
# )

retriever = vectorstore.as_retriever(search_kwargs={"k":5})

# retriever_notion = vectorstore_notion.as_retriever(search_kwargs={"k": 10})

@tool
def find_in_memory(query: str) -> list:
    """ finds related topics to 'query' in the vector store memory, returning all relevant documents in a list """
    global retriever

    return retriever.invoke(query)

@tool
def find_in_memory_notion_data(query: str) -> list:
    """ finds related topics to 'query' only searching the vector store memory for documents from 'notion' source.
    - documents saved from notion pages or journaling entries
    Returns a list of all relevant documents
    """
    global retriever

    return retriever.invoke(query, filter={"source": "notion"})

@tool
def find_in_memory_user_data(query: str) -> list:
    """ finds related topics to 'query' only searching the vector store memory for documents from 'user' source.
    - documents saved from user conversations or specific atributes to the user or his environment
    Returns a list of all relevant documents
    """
    global retriever

    return retriever.invoke(query, filter={"source": "user"})

@tool(args_schema=NewMemory)
def add_new_memory(new_memory: str, source: str) -> str:
    """ add a new memory to the vector store memory db.
    Arguments:
    - new_memory: str, representing a concise summary of the new memory to be added
    - source: str, either 'user' or 'notion' representing the source from which the new memory is saved from
    """

    try:
        with log_lock:
            with open(LOG, "r") as f:
                logs = json.load(f)
                if not logs:
                    logs = []
    except Exception as e:
        return f"Issue saving the memory: {e}"
    
    last_id = -1
    if logs:
        last_id = logs[-1].get("id", -1)

    new_doc = [Document(
        page_content=new_memory,
        metadata={"source": source},
        id=last_id+1
    )]

    uuid = str(uuid4())

    log_entry = {
    "id": last_id+1,
    "uid": uuid,
    "content": new_memory,
    "source": source,
    "timestamp": datetime.now().isoformat()
    }

    vectorstore.add_documents(documents=new_doc, ids = [uuid])

    logs.append(log_entry)

    try:
        with log_lock:
            with open(LOG, "w") as f:
                json.dump(logs, f, indent=4)
    except Exception as e:
        return f"Error occured while saving log: {e}"
    
    return f"New memory: {new_memory} saved successfully to memory."

def get_user_memories():
    data = vectorstore.get()
    documents = data['documents']
    meta_data = data['metadatas']

    user_memories = '\n'.join([f'- {memory}' for i, memory in enumerate(documents) if meta_data[i]['source'] == 'user'])

    return user_memories

@tool
def get_q2_2025_goals():
    """ Retrieves all memories saved for Q2 goals """
    data = vectorstore.get(where={"source": "spring_reset_q2_2025"})
    documents = data['documents']
    meta_data = data['metadatas']

    user_memories = '\n'.join([f'- {memory}' for i, memory in enumerate(documents) if meta_data[i]['source'] == 'spring_reset_q2_2025'])

    return 'Q2 Goals saved memories:\n' + user_memories
    

if __name__ == "__main__":

    # test_doc = [Document(
    #     page_content="The users name is henoch",
    #     metadata={"source": "test"},
    #     # for sources i will for now give it "user" or "notion" maybe also expicitely the notion page but we will see
    #     id=0
    # )]

    # uuids = [str(uuid4()) for _ in range(len(test_doc))]

    # vectorstore.add_documents(documents=[test_doc], ids=uuids)

    # result = retriever.invoke("What is the users Name?")

    # for r in result:
    #     print(r.page_content)

    # vectorstore.delete(ids="6dc11050-ac4e-426b-9f67-5882c2189830")

    # data = vectorstore.get()
    # documents = data['documents']
    # meta_data = data['metadatas']
    # print(data)

    # documents_update = documents[-26:]
    # updated_documents = []
    # for document in documents_update:
    #     updated_documents.append(Document(
    #         page_content=document,
    #         metadata={"source": "spring_reset_q2_2025"}
    #     ))

    # vectorstore.update_documents(
    #     ids=data["ids"][-26:],
    #     documents=updated_documents
    # )

    get_q2_2025_goals()