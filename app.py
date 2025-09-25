import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up the Gemini API key from the environment variable
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found. Please set the 'GEMINI_API_KEY' environment variable in your .env file.")
    st.stop()

genai.configure(api_key=api_key)

# Set up the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Set the Streamlit page title
st.title("🤖 Chat with Me")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages
for message in st.session_state.messages:
    # Map 'model' role from API to 'assistant' for Streamlit display
    role_to_display = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role_to_display):
        st.markdown(message["content"])

# Process user input
if prompt := st.chat_input("What can I do for you?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get a response from the Gemini model
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Convert Streamlit history to the Gemini API format
                chat_history = []
                for message in st.session_state.messages:
                    # The API expects 'model' for the assistant role
                    api_role = "model" if message["role"] == "assistant" else "user"
                    chat_history.append({"role": api_role, "parts": [{"text": message["content"]}]})

                # Create a chat session with the formatted history
                chat_session = model.start_chat(history=chat_history)
                response = chat_session.send_message(prompt, stream=True)
                
                # Display the response in a streaming fashion
                response_text = ""
                placeholder = st.empty()
                for chunk in response:
                    response_text += chunk.text
                    placeholder.markdown(response_text + "▌") # Add a blinking cursor for effect
                placeholder.markdown(response_text)
                
                # Add the assistant's response to the chat history (in Streamlit's format)
                st.session_state.messages.append({"role": "model", "content": response_text})
            except Exception as e:
                st.error(f"An error occurred: {e}")
