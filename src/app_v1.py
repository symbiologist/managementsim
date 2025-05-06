import streamlit as st
import pandas as pd
import litellm  # Import litellm
import os       # Import os for environment variables
# Make sure case_config.py exists and defines SYSTEM_PROMPT
try:
    from case_config import SYSTEM_PROMPT
except ImportError:
    st.error("Error: Could not find or import 'case_config.py'. Please ensure it exists and defines SYSTEM_PROMPT.")
    # Define a default system prompt if the import fails, or stop execution
    SYSTEM_PROMPT = "You are a helpful assistant evaluating a management reasoning case."
    # st.stop() # Alternatively, stop if the config is critical

# --- Environment Variable Setup for API Keys ---
# *** IMPORTANT: REMOVE HARDCODED KEYS ***
# Use Streamlit secrets or environment variables

# Setup using Streamlit Secrets (Recommended)
# Ensure you have a .streamlit/secrets.toml file with:
# [google_genai]
# api_key = "YOUR_NEW_GOOGLE_API_KEY"

try:
    # Attempt to get key from Streamlit secrets
    google_api_key = st.secrets["google_genai"]["api_key"]
    os.environ["GEMINI_API_KEY"] = google_api_key
    st.success("Google API Key loaded successfully from Secrets.", icon="✅")
except (KeyError, FileNotFoundError):
    # Fallback to environment variable if secrets fail or aren't used
    google_api_key = os.environ.get("GEMINI_API_KEY")
    if google_api_key:
        st.warning("Loaded Google API Key from environment variable.", icon="⚠️")
    else:
        st.error("Google API Key not found. Please set it in Streamlit Secrets ([google_genai] section) or as an environment variable (GOOGLE_API_KEY).")
        st.stop()
except Exception as e:
    st.error(f"An error occurred while accessing secrets or environment variables: {e}")
    st.stop()



st.title("Management Reasoning Case Evaluation")
st.write(
    "Welcome! This tool evaluates your management script for a patient presentation using AI."
)

# --- Model selection using VALID litellm compatible names ---
# As of early 2025, these are more likely correct names. Check Google's documentation for the latest.
available_models = [
    "gemini/gemini-2.0-flash", # Use '-latest' tag or specific dated version
    "gemini/gemini-2.5-pro-latest",   # Use '-latest' tag or specific dated version
    # "gemini/gemini-1.0-pro",        # Older but potentially still available
    # Add other models if needed and if you have the keys configured
    # "gpt-4o-mini",
    # "gpt-4o",
    # "claude-3-opus-20240229",
]
# Filter list if some keys aren't available (optional enhancement)
# Example: if not os.environ.get("OPENAI_API_KEY"):
#    available_models = [m for m in available_models if not m.startswith("gpt")]

if not available_models:
    st.error("No models available. Check API key setup and model names.")
    st.stop()

model_selection = st.selectbox(
    "Select Model",
    available_models
)

# --- Gate the user behind a "Ready" button ---
if "ready" not in st.session_state:
    st.session_state.ready = False

if not st.session_state.ready:
    if st.button("I'm Ready to Begin"):
        st.session_state.ready = True
        # Reset conversation when user is ready
        st.session_state.messages = []
        st.session_state.system_prompt_executed = False
        st.rerun()
    else:
        # Display instructions while waiting for user to be ready
        st.info("Click 'I'm Ready to Begin' to start the evaluation.")
        st.stop()

# --- Initialize conversation state if not set ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt_executed" not in st.session_state:
    st.session_state.system_prompt_executed = False

# --- Execute system prompt once ---
# This section now runs *after* the ready button is clicked and state is initialized
if st.session_state.ready and not st.session_state.system_prompt_executed:
    st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})

    try:
        with st.spinner(f"Getting initial response from {model_selection}..."):
            response = litellm.completion(
                model=model_selection,
                messages=st.session_state.messages,
                # temperature=0.7, # Optional parameters
                # max_tokens=1500,
            )
        # Access content - litellm uses the same structure
        first_reply = response.choices[0].message.content

        st.session_state.messages.append({"role": "assistant", "content": first_reply})
        st.session_state.system_prompt_executed = True
        st.rerun() # Rerun to display the initial message immediately

    except litellm.exceptions.AuthenticationError:
         st.error(f"Authentication Error: Failed to authenticate with the API. Please check your API key for {model_selection.split('/')[0] if '/' in model_selection else 'the selected provider'}. Ensure it's valid, active, and has the correct permissions/billing enabled.")
         # Reset state to allow trying again after fixing the key
         st.session_state.ready = False
         st.session_state.messages = []
         st.session_state.system_prompt_executed = False
         st.stop()
    except litellm.exceptions.NotFoundError:
         st.error(f"Model Not Found Error: The model '{model_selection}' was not found. It might be misspelled or unavailable in your region or for your account.")
         # Reset state
         st.session_state.ready = False
         st.session_state.messages = []
         st.session_state.system_prompt_executed = False
         st.stop()
    except Exception as e:
        st.error(f"An error occurred calling LiteLLM: {e}")
        # Optional: Reset state on generic errors too
        if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
             st.session_state.messages.pop(0) # Remove system prompt if call failed
        st.session_state.system_prompt_executed = False # Allow retry
        st.stop()


# --- Display existing messages ---
# Only display if the system prompt has been executed successfully
if st.session_state.system_prompt_executed:
    for msg in st.session_state.messages:
        # hide system prompt from chat display
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# --- Chat input ---
# Only allow input if the system prompt has been executed successfully
if st.session_state.system_prompt_executed:
    if prompt := st.chat_input("Your response (as the student)..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            with st.spinner(f"Thinking with {model_selection}..."):
                response = litellm.completion(
                    model=model_selection,
                    messages=st.session_state.messages,
                )
            assistant_reply = response.choices[0].message.content

            with st.chat_message("assistant"):
                st.markdown(assistant_reply)
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
            st.rerun() # Rerun to ensure the save button logic runs correctly after display

        except litellm.exceptions.AuthenticationError:
             st.error(f"Authentication Error during chat. Please check your API key for {model_selection.split('/')[0] if '/' in model_selection else 'the selected provider'}.")
             # Remove the last user message if the API call failed
             if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
        except litellm.exceptions.NotFoundError:
             st.error(f"Model Not Found Error: The model '{model_selection}' was not found.")
             if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
        except Exception as e:
            st.error(f"An error occurred calling LiteLLM: {e}")
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()


# --- Save conversation ---
# Show save button only if conversation has started
if st.session_state.system_prompt_executed and len(st.session_state.messages) > 1: # More than just system prompt
    if st.button("Save Conversation"):
        messages_to_save = [msg for msg in st.session_state.messages if msg["role"] != "system"]

        if messages_to_save:
            df = pd.DataFrame(messages_to_save)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Conversation as CSV",
                data=csv,
                file_name="conversation_log.csv",
                mime="text/csv"
            )
        else:
            # This case should ideally not be reachable if the button is shown correctly
            st.warning("No user/assistant messages to save yet!")