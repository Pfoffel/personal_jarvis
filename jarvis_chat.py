
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
    current_tool_name = None # To store the name of the current tool
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
                # For AI messages, content_buffer is fine.
                # For Tool messages, content_buffer now includes the "Tool: name\n\n" prefix,
                # and this entire string should be saved to history.
                processed_content_for_history = content_buffer
                
                if role_buffer == "ai":
                    # This container.markdown is for the final display of the previous message,
                    # if it wasn't fully streamed (though usually it is).
                    container.markdown(content_buffer) 
                elif role_buffer == "tool":
                    # The container.code() for the previous tool message was already handled by the streaming logic.
                    # No specific rendering action needed here for the *previous* tool message's container.
                    pass

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
            if role == 'tool':
                current_tool_name = chunk[0].name # Capture tool name
                content_buffer = f"Tool: {current_tool_name}\n\n"
            else:
                content_buffer = ""
                current_tool_name = None # Reset for non-tool messages

        # Stream content
        # For tool calls, the first chunk of 'content' might be the arguments,
        # so we append it only if it's not the initial prefix setup.
        if role == 'tool' and content_buffer == f"Tool: {current_tool_name}\n\n" and (content == "Making a tool call..." or not content):
            pass # Avoid appending redundant "Making a tool call..." or empty content if prefix is already set
        else:
            content_buffer += content
        if role_buffer == "ai":
            container.markdown(content_buffer + "▌")
        elif role_buffer == "tool":
            # Tool Message Rendering (Streaming Loop):
            # content_buffer includes the "Tool: [tool_name]\n\n" prefix.
            # This prefixed content is rendered directly as plain text within the code block.
            # This approach simplifies rendering; specific language detection (JSON, Python, etc.)
            # for the tool's raw output is not applied here.
            container.code(content_buffer, language="text")

    # Final flush
    if content_buffer:
        if role_buffer == "ai":
            container.markdown(content_buffer)
        elif role_buffer == "tool":
            # Tool Message Rendering (Final Flush):
            # content_buffer includes the "Tool: [tool_name]\n\n" prefix.
            # This prefixed content is rendered directly as plain text within the code block,
            # similar to the streaming logic.
            container.code(content_buffer, language="text")
            
            # History Saving Logic (Final Flush for Tool Messages):
            # For tool messages, content_buffer is now a string starting with "Tool: [tool_name]\n\n".
            processed_content_for_history = content_buffer
            
            # The following conditional block is legacy from when tool content was processed differently.
            # For current tool messages (prefixed strings):
            # - `isinstance(content_buffer, dict)` will be false.
            # - `stripped_content` is not defined in this scope, so `elif stripped_content.startswith("```")`
            #   would cause an error if reached by a tool message (but it won't be due to the above).
            #   This path might be relevant if non-tool, non-AI messages were processed here
            #   and `stripped_content` was defined.
            # As a result, for tool messages, `processed_content_for_history` correctly remains
            # the full, prefixed `content_buffer` string set above.
            if isinstance(content_buffer, dict):
                processed_content_for_history = json.dumps(content_buffer, indent=2)
            # The 'stripped_content' variable is not defined here. This path is not taken by tool messages.
            # elif stripped_content.startswith("```"): 
            #     lines = content_buffer.splitlines()
            #     if len(lines) > 1:
            #         processed_content_for_history = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
            
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

    