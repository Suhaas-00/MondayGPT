import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv(override=True)

from agents.chatbot_agent import ChatbotAgent

st.set_page_config(
    page_title="Monday.com BI Assistant",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for Dark mode with Dark Red chat boxes
st.markdown("""
<style>
    /* Main background: Black */
    .stApp {
        background-color: #000000;
    }
    
    /* Make all general text white */
    div, p, span, h1, h2, h3, h4, h5, h6, li {
        color: #ffffff !important;
    }

    /* Hide sidebar, top decorations, toolbar */
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
    
    /* Main container width */
    .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    /* Title styling */
    .chatgpt-title {
        text-align: center;
        font-family: 'Söhne', 'Segoe UI', sans-serif;
        font-weight: 600;
        font-size: 24px;
        margin-bottom: 2rem;
        color: #ffffff;
    }
    
    /* Input box styling */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    
    /* Input textarea container styling */
    [data-testid="stChatInput"] {
        background-color: #1a1a1a !important;
        border: 1px solid #333 !important;
    }
    
    /* Text inside the input box */
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
    }
    
    /* Chat message container - Rectangular with Dark Red Fill */
    [data-testid="stChatMessage"] {
        background-color: #8B0000 !important; /* Dark Red background */
        border: 2px solid #8B0000 !important; /* Dark Red border */
        border-radius: 0px !important; /* Sharp rectangle (0px radius) */
        padding: 15px !important;
        margin-bottom: 20px !important;
    }

    /* Ensure text inside the message is white */
    [data-testid="stChatMessageContent"], [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }
    
    /* Avatar icons color adjustment to contrast against dark red */
    [data-testid="stChatMessageAvatar"] {
        background-color: #000000 !important; 
        border-radius: 4px;
    }
    
    /* Styling for code or inline styling returned by LLM */
    code {
        color: #000000 !important;
        background-color: #dddddd !important;
    }
</style>

<div class="chatgpt-title">Monday.com BI Assistant</div>
""", unsafe_allow_html=True)

# Initialize chat history and agent in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial greeting
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I'm your Monday.com Business Intelligence Assistant. How can I help you analyze your Deals or Work Orders today?"
    })

if "agent" not in st.session_state:
    try:
        st.session_state.agent = ChatbotAgent()
    except Exception as e:
        st.error(f"Failed to initialize ChatbotAgent: {e}")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    # Use standard Streamlit chat message UI
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Message Monday.com BI Assistant..."):
    # Add user message to chat history immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent.handle_question(prompt)
                
                if "Rate limit" in response or "rate_limit_exceeded" in response:
                    err_msg = "⚠️ Rate limit reached on the API. Please wait a bit before asking another question."
                    st.warning(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
                else:
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
