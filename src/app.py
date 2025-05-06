import streamlit as st
import litellm
import os
import copy # To avoid modifying the original system prompt message
from case_config import SYSTEM_PROMPT # Import the system prompt

# --- Configuration ---
st.set_page_config(page_title="EM Case Simulator", layout="wide")
st.title("🚨 Emergency Medicine Case Simulator")

# --- API Key Setup ---
# Try to get keys from st.secrets
openai_key = st.secrets.get("OPENAI_API_KEY")
anthropic_key = st.secrets["anthropic"]["api_key"]
gemini_key = st.secrets["google_genai"]["api_key"]

# Set keys as environment variables for litellm (only if they exist)
if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key
if anthropic_key:
    os.environ["ANTHROPIC_API_KEY"] = anthropic_key
if gemini_key:
    os.environ["GEMINI_API_KEY"] = gemini_key

# --- Model Selection ---
# Define available models (ensure these are valid litellm model strings)
# Add/remove models based on which APIs you have keys for and want to offer
available_models = []
if gemini_key:
    available_models.extend(["gemini/gemini-2.0-flash", "gemini/gemini-2.5-pro"])
if openai_key:
    available_models.extend(["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
if anthropic_key:
    available_models.extend(["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"])


if not available_models:
    st.error("No API keys found in st.secrets. Please add at least one API key (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY) to your .streamlit/secrets.toml file.")
    st.stop() # Stop execution if no models are available

selected_model = st.sidebar.selectbox(
    "Select LLM Model",
    available_models,
    index=0, # Default to the first model in the list
    key="selected_model" # Use a key to access this widget's state
)

# --- System Prompt & Initial Message ---
# Define the system message structure
system_message = {"role": "system", "content": SYSTEM_PROMPT}

# --- Session State Initialization ---
# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Optionally add a starting message from the assistant based on the system prompt
    # You might want the simulation to start automatically or wait for user input.
    # Let's assume the system prompt asks the AI to present the first case,
    # so we don't need an initial assistant message here. The first API call will generate it.

# --- Display Chat History ---
# Display existing messages in the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input and Processing ---
if prompt := st.chat_input("Your response (e.g., 'Order CBC, Chem-7, LFTs', 'Perform focused cardiac exam')"):
    # 1. Add user message to chat history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Prepare messages for LiteLLM
    # Create a deep copy to avoid modifying the session state directly here
    messages_for_api = [system_message] + copy.deepcopy(st.session_state.messages)

    # 3. Call LiteLLM API
    try:
        with st.spinner(f"Thinking using {selected_model}..."):
            # Use litellm.completion for synchronous calls
            response = litellm.completion(
                model=st.session_state.selected_model,
                messages=messages_for_api,
                # Optional parameters (adjust as needed):
                # temperature=0.7,
                # max_tokens=1000,
            )

            # Extract the assistant's response
            # LiteLLM's response structure mirrors OpenAI's
            assistant_response = response.choices[0].message.content

            # 4. Add assistant response to chat history and display it
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.markdown(assistant_response)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        # Optionally remove the last user message if the API call failed
        # st.session_state.messages.pop()


# --- Sidebar Options ---
st.sidebar.divider()
if st.sidebar.button("Reset Chat / New Case"):
    st.session_state.messages = []
    st.rerun() # Rerun the app to clear the chat display

st.sidebar.info("Select a model and start interacting with the case presented by the AI.")

# Save conversation
if st.button("Save Conversation"):
    if st.session_state.messages:
        df = pd.DataFrame(st.session_state.messages)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Conversation as CSV",
            data=csv,
            file_name="conversation.csv",
            mime="text/csv"
        )
    else:
        st.warning("No conversation to save yet!")