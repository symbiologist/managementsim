import streamlit as st
import litellm
import os
import copy # To avoid modifying the original system prompt message
import pandas as pd
# Updated import from case_config
from case_config import SYSTEM_PROMPT, CASE_1, CASE_2, CASE_3 # Assuming CASE_1, CASE_2, CASE_3 are defined

# Imports for Google Drive integration
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload # More robust for in-memory uploads

# --- Configuration ---
st.set_page_config(page_title="EM Case Simulator", layout="wide")
st.title("Emergency Medicine Case Simulator") # User's title

# --- Define Available Cases (mapping user-friendly names to case detail variables) ---
AVAILABLE_CASES = {
    "Case 1": CASE_1,
    "Case 2": CASE_2,
    "Case 3": CASE_3,
    # If you add CASE_4, CASE_5 in case_config.py, add them here too:
    # "Case 4": CASE_4, # Example
}
DEFAULT_CASE_NAME = list(AVAILABLE_CASES.keys())[0] if AVAILABLE_CASES else None


# --- Session State Initialization ---
if "username" not in st.session_state:
    st.session_state.username = ""
if "username_submitted" not in st.session_state:
    st.session_state.username_submitted = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "case_summary" not in st.session_state:
    st.session_state.case_summary = "Summary will appear here once the case starts."
if 'error_fetching_initial_case' not in st.session_state: 
    st.session_state.error_fetching_initial_case = False
if 'selected_case_name' not in st.session_state: 
    st.session_state.selected_case_name = DEFAULT_CASE_NAME
if 'current_system_prompt_content' not in st.session_state: 
    if st.session_state.selected_case_name and st.session_state.selected_case_name in AVAILABLE_CASES:
        st.session_state.current_system_prompt_content = SYSTEM_PROMPT + "\n\n" + AVAILABLE_CASES[st.session_state.selected_case_name]
    else:
        st.session_state.current_system_prompt_content = SYSTEM_PROMPT
if 'chat_input_disabled' not in st.session_state: # This will now control if the chat input is *rendered*
    st.session_state.chat_input_disabled = False


# --- Prompts (SUMMARY_SYSTEM_PROMPT is static) ---
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

# --- API Key Setup (done once) ---
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

# --- Model Selection (left sidebar - always visible) ---
available_llm_models = [] 
if gemini_key:
    available_llm_models.extend(["gemini/gemini-2.0-flash"]) 
if openai_key:
    available_llm_models.extend(["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
if anthropic_key:
    available_llm_models.extend(["claude-3-sonnet-20240229", "claude-3-haiku-20240307"])

if not available_llm_models:
    st.sidebar.error("No API keys found for LLMs. Please add API keys to your .streamlit/secrets.toml file.")
else:
    selected_llm_model_for_sim = st.sidebar.selectbox( 
        "Select LLM Model",
        available_llm_models,
        index=0,
        key="selected_llm_model_widget" 
    )
    summarizer_llm_model_for_sim = selected_llm_model_for_sim 

# --- Helper Functions (defined globally) ---
def format_chat_history_for_summary(chat_messages):
    formatted_history = []
    for msg in chat_messages:
        role = "Attending (AI)" if msg["role"] == "assistant" else "Student/Resident (User)"
        formatted_history.append(f"{role}: {msg['content']}")
    return "\n".join(formatted_history)

def generate_case_summary(chat_history_for_summary, model_to_use):
    if not model_to_use: 
        return "Summarizer LLM not selected. Cannot generate summary."
    if not chat_history_for_summary:
        return "No case information available to summarize yet."
    summary_messages = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": f"Please summarize the following case interaction transcript:\n\n{chat_history_for_summary}"}
    ]
    try:
        response = litellm.completion(
            model=model_to_use, messages=summary_messages, temperature=0.3
        )
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        return f"Could not generate summary at this time. Error: {str(e)[:100]}..."

def upload_to_google_drive(messages_to_save, username_prefix, case_name_for_file):
    if not messages_to_save:
        st.sidebar.warning("No conversation content to save to Google Drive.")
        return False
    creds_dict = st.secrets.get("gcp_service_account_key_json")
    if not creds_dict:
        st.sidebar.error("Google Cloud service account key not found in secrets for Drive upload.")
        return False
    try:
        with st.spinner(f"Saving conversation for {case_name_for_file} to Google Drive..."): 
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=['https://www.googleapis.com/auth/drive.file']
            )
            drive_service = build('drive', 'v3', credentials=creds)
            df = pd.DataFrame(messages_to_save)
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_buffer.seek(0)
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            
            safe_case_name = case_name_for_file.replace(':', '').replace(' ', '_').replace('/', '_') if case_name_for_file else "UnknownCase"
            file_name = f"{username_prefix}_{safe_case_name}_em_case_conversation_{timestamp}.csv"
            
            folder_id = "1mLOznW0Jtcdb_2AJKKu3y94L913Y26ji" 
            if folder_id == "YOUR_GOOGLE_DRIVE_FOLDER_ID": 
                 st.sidebar.warning("Google Drive Folder ID is not configured. Please update the script.")
                 return False 
            file_metadata = {'name': file_name, 'parents': [folder_id]}
            media_body = MediaIoBaseUpload(csv_buffer, mimetype='text/csv', resumable=True)
            drive_service.files().create(
                body=file_metadata, media_body=media_body, fields='id'
            ).execute()
            st.sidebar.success(f"Conversation for {case_name_for_file} saved to Google Drive: {file_name}")
            return True
    except Exception as e:
        st.sidebar.error(f"Failed to save to Google Drive: {e}")
        return False

# --- Main Application Logic ---
if not st.session_state.username_submitted:
    # --- Username Input Display (left-aligned and narrower using columns) ---
    login_input_col, empty_spacer_col = st.columns([1.5, 2.5]) 

    with login_input_col: 
        st.header("User Login") 
        st.markdown("Please enter your username to begin the simulation.")
        
        with st.form("username_form_main_page"):
            username_input_main = st.text_input("Username", key="username_input_main_page_widget", help="This will be used to prefix saved filenames.")
            submitted_main = st.form_submit_button("Start Simulation")
            
            if submitted_main:
                if not available_llm_models: 
                    st.error("No LLM models available. Please check API key configuration in the sidebar and secrets file.")
                elif not AVAILABLE_CASES:
                     st.error("No cases are defined. Please check case_config.py and the AVAILABLE_CASES dictionary in the script.")
                elif username_input_main.strip():
                    st.session_state.username = username_input_main.strip()
                    st.session_state.username_submitted = True
                    
                    if st.session_state.selected_case_name not in AVAILABLE_CASES: 
                        st.session_state.selected_case_name = DEFAULT_CASE_NAME
                    
                    if st.session_state.selected_case_name: 
                        st.session_state.current_system_prompt_content = SYSTEM_PROMPT + "\n\n" + AVAILABLE_CASES[st.session_state.selected_case_name]
                    else: 
                        st.session_state.current_system_prompt_content = SYSTEM_PROMPT
                        st.warning("No default case could be selected. Using base system prompt.")

                    st.session_state.messages = [] 
                    st.session_state.case_summary = "Summary will appear here once the case starts." 
                    st.session_state.error_fetching_initial_case = False 
                    st.session_state.chat_input_disabled = False 
                    st.rerun() 
                else:
                    st.error("Username cannot be empty. Please enter a username.")
    
    st.sidebar.info("Please enter a username to start.")

else: # Username has been submitted
    case_options = list(AVAILABLE_CASES.keys()) 
    if not case_options:
        st.sidebar.error("No cases found. Please define cases in case_config.py and AVAILABLE_CASES dictionary.")
    else:
        if st.session_state.selected_case_name not in case_options:
            st.session_state.selected_case_name = case_options[0] 
            st.session_state.current_system_prompt_content = SYSTEM_PROMPT + "\n\n" + AVAILABLE_CASES[st.session_state.selected_case_name]
            st.session_state.messages = []
            st.session_state.case_summary = "Summary will appear here once the new case starts."
            st.session_state.error_fetching_initial_case = False
            st.session_state.chat_input_disabled = False 

        previous_case_name = st.session_state.selected_case_name
        # Store whether the input was disabled for the *previous* case before changing it.
        previous_case_chat_input_disabled = st.session_state.chat_input_disabled


        newly_selected_case_name = st.sidebar.selectbox(
            "Select Case",
            options=case_options, 
            key="case_selector_widget",
            index=case_options.index(st.session_state.selected_case_name) if st.session_state.selected_case_name in case_options else 0
        )

        if newly_selected_case_name != previous_case_name:
            # Auto-save the previous case's chat log ONLY IF chat input was NOT already disabled (i.e., "Done" wasn't typed)
            if st.session_state.messages and not previous_case_chat_input_disabled:
                valid_messages_to_save = [msg for msg in st.session_state.messages if msg.get("content")]
                if valid_messages_to_save:
                    upload_to_google_drive(valid_messages_to_save, st.session_state.username, previous_case_name)
            
            st.session_state.selected_case_name = newly_selected_case_name
            st.session_state.messages = [] 
            st.session_state.case_summary = "Summary will appear here once the new case starts."
            st.session_state.error_fetching_initial_case = False
            st.session_state.current_system_prompt_content = SYSTEM_PROMPT + "\n\n" + AVAILABLE_CASES[st.session_state.selected_case_name]
            st.session_state.chat_input_disabled = False # Re-enable chat for new case
            st.rerun() 

    current_main_chat_system_message = {"role": "system", "content": st.session_state.current_system_prompt_content}

    st.text(f"Welcome, {st.session_state.username}! You are working on: {st.session_state.selected_case_name or 'No Case Selected'}")
    st.text("You may ask questions, order tests, order medications, and request consults.")
    st.text("You can also request a hint if needed. The case will continue until you Discharge or Admit the patient.")
    st.divider() 

    main_col, right_sidebar_col = st.columns([3, 1])

    with main_col:
        st.subheader("Simulation Interface") 

        if not st.session_state.messages and not st.session_state.error_fetching_initial_case and st.session_state.selected_case_name:
            if 'selected_llm_model_widget' in st.session_state and st.session_state.selected_llm_model_widget:
                try:
                    with st.spinner(f"Preparing {st.session_state.selected_case_name} for {st.session_state.username}..."):
                        initial_messages_for_case_presentation = [
                            current_main_chat_system_message, 
                            {"role": "user", "content": "Present the case based on the details provided in your system instructions."}
                        ]
                        initial_response = litellm.completion(
                            model=st.session_state.selected_llm_model_widget,
                            messages=initial_messages_for_case_presentation,
                        )
                        assistant_initial_message = initial_response.choices[0].message.content
                        st.session_state.messages.append({"role": "assistant", "content": assistant_initial_message})
                        if st.session_state.messages:
                             formatted_history = format_chat_history_for_summary(st.session_state.messages)
                             st.session_state.case_summary = generate_case_summary(formatted_history, summarizer_llm_model_for_sim)
                        st.session_state.error_fetching_initial_case = False
                except Exception as e:
                    st.error(f"Error fetching initial case: {e}")
                    st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't load a case. Please try resetting or check the API configuration."})
                    st.session_state.case_summary = "Could not load initial case summary due to an error."
                    st.session_state.error_fetching_initial_case = True
            elif not st.session_state.selected_case_name:
                 st.warning("Please select a case from the sidebar to begin.")
            else: 
                st.warning("No LLM model selected. Please select a model to start.")

        chat_display_area = st.container(height=500, border=True) 
        with chat_display_area:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            if not st.session_state.messages and not st.session_state.error_fetching_initial_case and st.session_state.selected_case_name:
                st.info("The case will be presented shortly...")
        
        # Conditionally render the chat input
        if not st.session_state.chat_input_disabled:
            prompt_placeholder = "Type 'Done' to end interaction with this case."
            if prompt := st.chat_input(prompt_placeholder, key="chat_input_widget"): 
                if not st.session_state.selected_case_name:
                    st.error("Please select a case from the sidebar before interacting.")
                elif not st.session_state.get('selected_llm_model_widget'):
                    st.error("Please select an LLM model from the sidebar.")
                else:
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    
                    if prompt.strip().lower() == "done":
                        if st.session_state.messages: 
                            messages_to_save_before_done = [
                                msg for msg in st.session_state.messages if msg.get("content")
                            ]
                            if messages_to_save_before_done:
                                upload_to_google_drive(
                                    messages_to_save_before_done, 
                                    st.session_state.username, 
                                    st.session_state.selected_case_name
                                )
                        
                        st.session_state.chat_input_disabled = True 
                        st.session_state.messages.append({"role": "assistant", "content": "Okay, this case interaction is now concluded and saved. You can select a new case or reset."})
                        st.rerun() 
                    else:
                        messages_for_api = [current_main_chat_system_message] + copy.deepcopy(st.session_state.messages)
                        try:
                            with st.spinner(f"Loading..."):
                                response = litellm.completion(
                                    model=st.session_state.selected_llm_model_widget,
                                    messages=messages_for_api,
                                )
                                assistant_response = response.choices[0].message.content
                                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                                if st.session_state.messages: 
                                    formatted_history = format_chat_history_for_summary(st.session_state.messages)
                                    st.session_state.case_summary = generate_case_summary(formatted_history, summarizer_llm_model_for_sim)
                            st.rerun()
                        except Exception as e:
                            st.error(f"An error occurred with the main chat: {e}")
                            st.rerun()
        else: 
            st.info("Chat input removed. This case interaction is concluded. Reset or select a new case to continue.")


    with right_sidebar_col:
        st.subheader("Live Case Summary")
        summary_display_area = st.container(height=500, border=True) 
        with summary_display_area:
            if st.session_state.get("case_summary"):
                st.markdown(st.session_state.case_summary)
            else:
                st.info("Case summary will be generated as the simulation progresses.")

    st.sidebar.divider() 
    if st.sidebar.button("Save and Reset"): 
        if st.session_state.messages: 
            if not st.session_state.chat_input_disabled: 
                valid_messages_to_save = [msg for msg in st.session_state.messages if msg.get("content")]
                if valid_messages_to_save:
                    upload_to_google_drive(valid_messages_to_save, st.session_state.username, st.session_state.selected_case_name) 
                else:
                    st.sidebar.info("No messages in the current session to save.")
            elif st.session_state.chat_input_disabled: 
                st.sidebar.info("Previous interaction already saved upon typing 'Done'.")
        else:
            st.sidebar.info("No messages in the current session to save.")
        
        st.session_state.messages = []
        st.session_state.case_summary = "Summary will appear here once the new case starts." 
        st.session_state.error_fetching_initial_case = False
        st.session_state.username = "" 
        st.session_state.username_submitted = False 
        st.session_state.chat_input_disabled = False 
        
        st.session_state.selected_case_name = DEFAULT_CASE_NAME 
        if st.session_state.selected_case_name: 
            st.session_state.current_system_prompt_content = SYSTEM_PROMPT + "\n\n" + AVAILABLE_CASES[st.session_state.selected_case_name]
        else: 
            st.session_state.current_system_prompt_content = SYSTEM_PROMPT
        st.rerun() 

    st.sidebar.info(f"User: {st.session_state.username} | LLM: {st.session_state.get('selected_llm_model_widget', 'N/A')} | Case: {st.session_state.get('selected_case_name', 'None Selected')}")

