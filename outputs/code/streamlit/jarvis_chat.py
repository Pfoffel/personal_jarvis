
import streamlit as st

def add_human_message(message: str):
    st.session_state.messages.append({"role": "human", "content": message})
    # Display user message in chat
    with st.chat_message("human", avatar="👨🏼‍🦱"):
        st.markdown(message)

def invoke_jarvis(prompt):
    response = f"I'm processing your request: {prompt}"  # Placeholder response
    # Add Jarvis's response to chat history
    st.session_state.messages.append({"role": "ai", "content": response})
    # Display Jarvis's response in chat
    with st.chat_message("ai", avatar="🤖"):
        st.markdown(response)

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
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    add_human_message(prompt)

    # Generate Jarvis's response (replace with your actual Jarvis logic)

    invoke_jarvis(prompt)

    tool = f"This is a tool call for: {prompt}"

    st.session_state.messages.append({"role": "tool", "content": tool})

    with st.chat_message("tool", avatar="🔨"):
        st.markdown(tool)
