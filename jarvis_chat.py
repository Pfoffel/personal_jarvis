
from main import system_memory, file_history, personal_agent, config
from langchain_core.messages import HumanMessage
import streamlit as st
import json

def add_human_message(message: str):
    st.session_state.messages.append({"role": "human", "avatar": "👨🏼‍🦱", "content": message})
    # Display user message in chat
    with st.chat_message("human", avatar="👨🏼‍🦱"):
        st.markdown(message)

def invoke_jarvis(prompt):

    role_buffer = None
    content_buffer = ""
    container = None
    for chunk in personal_agent.stream({
            "messages":[
                system_memory,
                file_history,
                HumanMessage(content=prompt)
            ]
        }, config, stream_mode="messages"):
        content = chunk[0].content or "Making a tool call..."
        message_type = chunk[1].get('langgraph_node')
        if message_type == 'agent':
            role = 'ai'
            avatar = "🤖"
        elif message_type == 'tools':
            role = 'tool'
            avatar = "🔨"
        if role != role_buffer:
            if content_buffer:
                # Finalize previous role's message
                if role == "ai":
                    container.markdown(content_buffer)
                elif role == "tool":
                    container.code(content_buffer)
                st.session_state.messages.append({
                    "role": role,
                    "avatar": avatar,
                    "content": content_buffer
                })

            # Start new message container
            container = st.chat_message(role, avatar=avatar).empty()
            role_buffer = role
            content_buffer = ""

        # Stream content
        content_buffer += content
        if role_buffer == "ai":
            container.markdown(content_buffer + "▌")
        elif role_buffer == "tool":
            # Try to pretty-render structured tool outputs
            if isinstance(content_buffer, dict):
                # If the content_buffer is actually a dict (sometimes it is!), render it as formatted JSON
                formatted = json.dumps(content_buffer, indent=2)
                container.code(formatted, language="json")

            elif content_buffer.strip().startswith("{") or content_buffer.strip().startswith("["):
                # Likely JSON string
                container.code(content_buffer, language="json")

            elif any(content_buffer.strip().startswith(pfx) for pfx in ["def ", "function ", "class ", "#", "import "]):
                # Looks like Python or generic code
                container.code(content_buffer, language="python")

            elif content_buffer.strip().startswith("```"):
                # Already formatted code block from the LLM
                container.markdown(content_buffer)

            else:
                # Default fallback
                container.markdown(content_buffer)

    # Final flush
    if content_buffer:
        if role_buffer == "ai":
            container.markdown(content_buffer)
        elif role_buffer == "tool":
            if isinstance(content_buffer, dict):
                # If the content_buffer is actually a dict (sometimes it is!), render it as formatted JSON
                formatted = json.dumps(content_buffer, indent=2)
                container.code(formatted, language="json")

            elif content_buffer.strip().startswith("{") or content_buffer.strip().startswith("["):
                # Likely JSON string
                container.code(content_buffer, language="json")

            elif any(content_buffer.strip().startswith(pfx) for pfx in ["def ", "function ", "class ", "#", "import "]):
                # Looks like Python or generic code
                container.code(content_buffer, language="python")

            elif content_buffer.strip().startswith("```"):
                # Already formatted code block from the LLM
                container.markdown(content_buffer)

            else:
                # Default fallback
                container.markdown(content_buffer)
        st.session_state.messages.append({
            "role": role_buffer,
            "avatar": avatar,
            "content": content_buffer
        })

# Set page title and icon
st.set_page_config(
    page_title="Jarvis Chat",
    page_icon=":material/smart_toy:"
)

# Jarvis's intro message
st.title("Jarvis: Your AI Assistant")
st.write("How can I assist you today, Henoch?")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message["avatar"]):
        if message["role"] == "tool":
            st.code(message["content"])
        else: st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    add_human_message(prompt)

    # Generate Jarvis's response (replace with your actual Jarvis logic)

    invoke_jarvis(prompt)

    tool = f"This is a tool call for: {prompt}"

    
