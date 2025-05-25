
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
                processed_content_for_history = content_buffer
                if role_buffer == "ai":
                    container.markdown(content_buffer)
                elif role_buffer == "tool":
                    # This is the rendering logic for the *previous* message.
                    # We also need to prepare content_buffer for history.
                    stripped_content = content_buffer.strip()
                    if isinstance(content_buffer, dict):
                        processed_content_for_history = json.dumps(content_buffer, indent=2)
                        # container.code(processed_content_for_history, language="json") # Already rendered by stream
                    elif stripped_content.startswith("{") or stripped_content.startswith("["):
                        # container.code(content_buffer, language="json") # Already rendered
                        pass # processed_content_for_history is already content_buffer
                    elif any(stripped_content.startswith(pfx) for pfx in ["def ", "class ", "import ", "#"]):
                        # container.code(content_buffer, language="python") # Already rendered
                        pass
                    elif stripped_content.startswith("```"):
                        lines = content_buffer.splitlines()
                        if len(lines) > 1:
                            # lang_spec = lines[0][3:].strip()
                            processed_content_for_history = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
                            # container.code(extracted_code, language=lang_spec if lang_spec else "text") # Already rendered
                        # else: container.code(content_buffer, language="text") # Already rendered
                    # else: container.code(content_buffer, language="text") # Already rendered
                
                # Determine avatar for the role_buffer that just finished
                previous_avatar = "🤖" if role_buffer == "ai" else "🔨" if role_buffer == "tool" else ""

                st.session_state.messages.append({
                    "role": role_buffer, # Should be role_buffer for the message that just ended
                    "avatar": previous_avatar, # Avatar for the role_buffer
                    "content": processed_content_for_history
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
            stripped_content = content_buffer.strip()
            if isinstance(content_buffer, dict):
                formatted = json.dumps(content_buffer, indent=2)
                container.code(formatted, language="json")
            elif stripped_content.startswith("{") or stripped_content.startswith("["):
                container.code(content_buffer, language="json")
            elif any(stripped_content.startswith(pfx) for pfx in ["def ", "class ", "import ", "#"]):
                container.code(content_buffer, language="python")
            elif stripped_content.startswith("```"):
                # Extract content and language from markdown code block
                lines = content_buffer.splitlines()
                if len(lines) > 1:
                    lang_spec = lines[0][3:].strip()
                    extracted_code = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
                    container.code(extracted_code, language=lang_spec if lang_spec else "text")
                else:
                    # Fallback if format is unexpected
                    container.code(content_buffer, language="text")
            else:
                container.code(content_buffer, language="text")

    # Final flush
    if content_buffer:
        if role_buffer == "ai":
            container.markdown(content_buffer)
        elif role_buffer == "tool":
            stripped_content = content_buffer.strip()
            if isinstance(content_buffer, dict):
                formatted = json.dumps(content_buffer, indent=2)
                container.code(formatted, language="json")
            elif stripped_content.startswith("{") or stripped_content.startswith("["):
                container.code(content_buffer, language="json")
            elif any(stripped_content.startswith(pfx) for pfx in ["def ", "class ", "import ", "#"]):
                container.code(content_buffer, language="python")
            elif stripped_content.startswith("```"):
                # Extract content and language from markdown code block
                lines = content_buffer.splitlines()
                if len(lines) > 1:
                    lang_spec = lines[0][3:].strip()
                    extracted_code = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
                    container.code(extracted_code, language=lang_spec if lang_spec else "text")
                else:
                    # Fallback if format is unexpected
                    container.code(content_buffer, language="text")
            else:
                container.code(content_buffer, language="text")
            
            # Prepare content for history
            processed_content_for_history = content_buffer
            if isinstance(content_buffer, dict):
                processed_content_for_history = json.dumps(content_buffer, indent=2)
            elif stripped_content.startswith("```"): # stripped_content is already defined in this block
                lines = content_buffer.splitlines()
                if len(lines) > 1:
                    processed_content_for_history = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
            # For other tool types (plain JSON string, python code, text), 
            # content_buffer is already the string to be stored.
            
        st.session_state.messages.append({
            "role": role_buffer,
            "avatar": avatar, # Avatar is already correct for the current role_buffer
            "content": processed_content_for_history if role_buffer == "tool" else content_buffer
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

    
