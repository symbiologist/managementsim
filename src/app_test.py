import streamlit as st
import litellm
import os
import copy # To avoid modifying the original system prompt message
import pandas as pd # Added for saving conversation
from case_config import SYSTEM_PROMPT # Import the system prompt

# --- Configuration ---
st.set_page_config(page_title="EM Case Simulator", layout="wide")
st.title("🚨 Emergency Medicine Case Simulator")
st.caption("Powered by LiteLLM")

# --- API Key Setup ---
# Try to get keys from st.secrets, using .get() for safer access
openai_key = st.secrets.get("OPENAI_API_KEY")
anthropic_secrets = st.secrets.get("anthropic", {})
anthropic_key = anthropic_secrets.get("api_key")
google_genai_secrets = st.secrets.get("google_genai", {})
gemini_key = google_genai_secrets.get("api_key")

# Set keys as environment variables for litellm (only if they exist)
if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key
if anthropic_key:
    os.environ["ANTHROPIC_API_KEY"] = anthropic_key
if gemini_key:
    os.environ["GEMINI_API_KEY"] = gemini_key # litellm expects GEMINI_API_KEY for Google models

# --- Model Selection ---
# Define available models (ensure these are valid litellm model strings)
available_models = []
if gemini_key:
    # Using user-specified Gemini model names
    available_models.extend(["gemini/gemini-2.0-flash", "gemini/gemini-2.5-pro"])
if openai_key:
    available_models.extend(["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
if anthropic_key:
    available_models.extend(["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"])

if not available_models:
    st.error("No API keys found or correctly configured in st.secrets. Please add at least one API key (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY) to your .streamlit/secrets.toml file.")
    st.stop()

selected_model = st.sidebar.selectbox(
    "Select LLM Model",
    available_models,
    index=0,
    key="selected_model"
)

# --- System Prompt ---
system_message = {"role": "system", "content": SYSTEM_PROMPT}

# --- Session State Initialization & Initial Case Presentation ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages: # If messages list is empty (new session or after reset)
    if st.session_state.selected_model: # Ensure a model is selected
        try:
            with st.spinner(f"Presenting new case with {st.session_state.selected_model}..."):
                # Initial call for case presentation.
                # For Gemini, it's often better to have a user message initiating the conversation
                # after the system prompt. The system prompt already asks the AI to present a case.
                initial_messages_for_case_presentation = [
                    system_message,
                    {"role": "user", "content": "Please present the first case as per your instructions."} # Explicit user turn
                ]
                initial_response = litellm.completion(
                    model=st.session_state.selected_model,
                    messages=initial_messages_for_case_presentation,
                    # temperature=0.7 # Optional: adjust for creativity of case presentation
                )
                assistant_initial_message = initial_response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": assistant_initial_message})
        except Exception as e:
            st.error(f"Error fetching initial case: {e}")
            # Add a placeholder message or instruction if the API call fails
            st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't load a case. Please try resetting or check the API configuration."})
    else:
        # This case should ideally not be hit if available_models check is robust
        st.warning("No model selected. Please select a model to start.")


# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input and Processing ---
if prompt := st.chat_input("Your response (e.g., 'Order CBC, Chem-7, LFTs', 'Perform focused cardiac exam')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare messages for LiteLLM: System prompt followed by the entire chat history.
    # The initial assistant message (case presentation) is already in st.session_state.messages.
    messages_for_api = [system_message] + copy.deepcopy(st.session_state.messages)

    try:
        with st.spinner(f"Thinking using {st.session_state.selected_model}..."):
            response = litellm.completion(
                model=st.session_state.selected_model,
                messages=messages_for_api,
                # temperature=0.7,
                # max_tokens=1500, # Adjust as needed
            )
            assistant_response = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.markdown(assistant_response)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        # Consider removing the last user message if the API call failed,
        # or adding an error message to the assistant's turn.
        # For now, we'll just show the error.

# --- Sidebar Options ---
st.sidebar.divider()
if st.sidebar.button("Reset Chat / New Case"):
    st.session_state.messages = [] # Clear messages
    # st.rerun() will re-execute the script from top, and the empty messages list
    # will trigger the initial case presentation logic.
    st.rerun()


st.sidebar.info("Select a model and start interacting with the case presented by the AI.")

# --- Save Conversation ---
# Ensure this button is not inside the sidebar if you want it in the main area
if st.button("Save Conversation"):
    if st.session_state.messages:
        # Filter out any potential initial error messages if needed
        valid_messages = [msg for msg in st.session_state.messages if msg.get("content")]
        if valid_messages:
            df = pd.DataFrame(valid_messages)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Conversation as CSV",
                data=csv,
                file_name=f"em_case_conversation_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No valid conversation content to save.")
    else:
        st.warning("No conversation to save yet!")

