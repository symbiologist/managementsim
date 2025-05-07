import streamlit as st
import litellm
import os
import copy # To avoid modifying the original system prompt message
import pandas as pd
from case_config import SYSTEM_PROMPT # Import the system prompt

# --- Configuration ---
st.set_page_config(page_title="EM Case Simulator", layout="wide")
st.title("Emergency Medicine Case Simulator") # User's title

# --- Introductory Text ---
# User's introductory text
st.text("Welcome to the case simulator. You may ask questions, order tests, order medications, and request consults.")
st.text("You can also request a hint if needed. The case will continue until you Discharge or Admit the patient.")

# --- Prompts ---
# User's SUMMARY_SYSTEM_PROMPT
SUMMARY_SYSTEM_PROMPT = """
You are an expert medical summarizer. Your task is to review a transcript of an emergency medicine case simulation between an AI attending physician and a user (student/resident).
Based on the entire conversation provided, create a concise summary that would be useful for quickly understanding the patient's current status.

The summary MUST include the following sections. Bullet list these with a newline between each item:
**ID:** Age, Sex (if mentioned), Chief Complaint.
**PMH:** Relevant past medical history.
**Meds:** list any long-term meds the patient is taking.
**Vitals:** Show an indented list of the most recent set of vitals (BP, HR, RR, Temp, SpO2).
**Exam:** List pertinent positives and negatives from a physical exam in bullet form.
**Labs:** List significant abnormal or critical lab values reported.
**Imaging:** Briefly mention significant findings from X-rays, CT scans, ultrasounds, etc.
**Other:** Briefly mention significant findings from other tests, such as EKGs
**Interventions Administered:**

Format clearly using Markdown.
If information for a section is not yet available in the transcript, please the section black. 
The summary should reflect the *latest* state of the case based on the full transcript.
Example for Vitals:
* **BP:** 120/80 mmHg
* **HR:** 75 bpm
* **RR:** 16 breaths/min
* **Temp:** 37.0°C (98.6°F)
* **SpO2:** 98% on Room Air
"""

# --- API Key Setup ---
openai_key = st.secrets.get("OPENAI_API_KEY")
anthropic_secrets = st.secrets.get("anthropic", {})
anthropic_key = anthropic_secrets.get("api_key")
google_genai_secrets = st.secrets.get("google_genai", {})
gemini_key = google_genai_secrets.get("api_key")

if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key
if anthropic_key:
    os.environ["ANTHROPIC_API_KEY"] = anthropic_key
if gemini_key:
    os.environ["GEMINI_API_KEY"] = gemini_key

# --- Model Selection (left sidebar) ---
available_models = []
if gemini_key:
    available_models.extend(["gemini/gemini-2.0-flash", "gemini/gemini-2.5-pro"])
if openai_key:
    available_models.extend(["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
if anthropic_key:
    available_models.extend(["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"])

if not available_models:
    st.error("No API keys found. Please add API keys to your .streamlit/secrets.toml file.")
    st.stop()

selected_model = st.sidebar.selectbox(
    "Select LLM Model for Case Simulation",
    available_models,
    index=0,
    key="selected_model"
)
summarizer_model = selected_model # Use the same model for summarization for simplicity

# --- System Prompt for Main Chat ---
main_chat_system_message = {"role": "system", "content": SYSTEM_PROMPT}

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "case_summary" not in st.session_state:
    st.session_state.case_summary = "Summary will appear here once the case starts."
if 'error_fetching_initial_case' not in st.session_state: # To track initial load errors for st.info message
    st.session_state.error_fetching_initial_case = False


# --- Helper Function to Format Chat History for Summarizer ---
def format_chat_history_for_summary(chat_messages):
    formatted_history = []
    for msg in chat_messages:
        role = "Attending (AI)" if msg["role"] == "assistant" else "Student/Resident (User)"
        formatted_history.append(f"{role}: {msg['content']}")
    return "\n".join(formatted_history)

# --- Helper Function to Generate Case Summary ---
def generate_case_summary(chat_history_for_summary, model_to_use):
    if not chat_history_for_summary:
        return "No case information available to summarize yet."

    summary_messages = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": f"Please summarize the following case interaction transcript:\n\n{chat_history_for_summary}"}
    ]
    try:
        response = litellm.completion(
            model=model_to_use,
            messages=summary_messages,
            temperature=0.3 # Lower temperature for more factual summary
        )
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        return f"Could not generate summary at this time. Error: {str(e)[:100]}..."

# --- Initial Case Presentation ---
if not st.session_state.messages and not st.session_state.error_fetching_initial_case : # Only on first run or after reset, and no previous error
    if st.session_state.selected_model:
        try:
            with st.spinner(f"Preparing a new case..."): # User's spinner text
                initial_messages_for_case_presentation = [
                    main_chat_system_message,
                    {"role": "user", "content": "Initialize the case. Please present the initial patient information including chief complaint, brief history, and initial vital signs."}
                ]
                initial_response = litellm.completion(
                    model=st.session_state.selected_model,
                    messages=initial_messages_for_case_presentation,
                )
                assistant_initial_message = initial_response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": assistant_initial_message})
                
                formatted_history = format_chat_history_for_summary(st.session_state.messages)
                st.session_state.case_summary = generate_case_summary(formatted_history, summarizer_model)
                st.session_state.error_fetching_initial_case = False # Reset error flag on success

        except Exception as e:
            st.error(f"Error fetching initial case: {e}")
            st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't load a case. Please try resetting or check the API configuration."})
            st.session_state.case_summary = "Could not load initial case summary due to an error."
            st.session_state.error_fetching_initial_case = True # Set error flag
    else:
        st.warning("No model selected. Please select a model to start.")

# --- Define Page Layout: Main chat area and Right Sidebar ---
main_col, right_sidebar_col = st.columns([3, 1]) # User's column sizing

with main_col:
    st.subheader("Simulation Interface") # User's subheader
    
    # Create a container for the chat messages with a fixed height to make it scrollable
    chat_display_area = st.container(height=500, border=True) # Adjust height as needed (e.g., 600, 700 pixels)

    with chat_display_area:
        # Display all chat messages from session state inside the scrollable container.
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Display "case will be presented shortly" only if messages are empty AND no initial error, inside the scrollable area
        if not st.session_state.messages and not st.session_state.error_fetching_initial_case:
            st.info("The case will be presented shortly...")

    # Chat input is rendered after all messages and outside the scrollable container.
    # User's chat input placeholder
    if prompt := st.chat_input("Your response (e.g., 'When did this start?', 'Vitals', 'Order CBC', 'Administer Tylenol')"):
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})

        messages_for_api = [main_chat_system_message] + copy.deepcopy(st.session_state.messages)

        try:
            with st.spinner(f"Loading..."): # User's spinner text
                response = litellm.completion(
                    model=st.session_state.selected_model,
                    messages=messages_for_api,
                )
                assistant_response = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

                formatted_history = format_chat_history_for_summary(st.session_state.messages)
                st.session_state.case_summary = generate_case_summary(formatted_history, summarizer_model)

            st.rerun()

        except Exception as e:
            st.error(f"An error occurred with the main chat: {e}")
            st.rerun()


with right_sidebar_col:
    st.subheader("Live Case Summary") # User's subheader
    summary_display_area = st.container(height=500, border=True) 
    
    with summary_display_area:
        if st.session_state.get("case_summary"):
            st.markdown(st.session_state.case_summary)
        else:
            st.info("Case summary will be generated as the simulation progresses.")


# --- Left Sidebar Options ---
st.sidebar.divider()
if st.sidebar.button("Reset"): # User's button text
    st.session_state.messages = []
    st.session_state.case_summary = "Summary will appear here once the new case starts." 
    st.session_state.error_fetching_initial_case = False # Reset error flag
    st.rerun() 

st.sidebar.info("Select a model and start interacting with the case presented by the AI.")

if st.sidebar.button("Save Conversation"):
    if st.session_state.messages:
        valid_messages = [msg for msg in st.session_state.messages if msg.get("content")]
        if valid_messages:
            df = pd.DataFrame(valid_messages)
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            csv_filename = f"em_case_conversation_{timestamp}.csv"
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.sidebar.download_button(
                label="Download Conversation as CSV",
                data=csv_data,
                file_name=csv_filename,
                mime="text/csv",
                key=f"download_{timestamp}" 
            )
        else:
            st.sidebar.warning("No valid conversation content to save.")
    else:
        st.sidebar.warning("No conversation to save yet!")

