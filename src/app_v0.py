import streamlit as st
import pandas as pd
from openai import OpenAI
from case_config import SYSTEM_PROMPT

st.title("Management Reasoning Case Evaluation")
st.write(
    "Welcome to the Management Reasoning Case Evaluation tool! This tool is designed to help evaluate your management script for a given patient presentation. "
)

openai_api_key = st.secrets["openai"]["api_key"]
client = OpenAI(api_key=openai_api_key)

# Model selection
model_selection = st.selectbox(
    "Select Model",
    ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o", "o3-mini"]
)

# Gate the user behind a "Ready" button
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
        st.stop()

# Initialize conversation state if not set
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt_executed" not in st.session_state:
    st.session_state.system_prompt_executed = False

# Execute system prompt once
if not st.session_state.system_prompt_executed:
    st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})

    # Single call (no streaming) to get the assistant's first response
    response = client.chat.completions.create(
        model=model_selection,
        messages=st.session_state.messages,
    )
    first_reply = response.choices[0].message.content  # Use .content attribute

    st.session_state.messages.append({"role": "assistant", "content": first_reply})
    st.session_state.system_prompt_executed = True

# Display existing messages
for msg in st.session_state.messages:
    if msg["role"] != "system":  # hide system prompt
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Your response (as the student)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Single call for assistant’s response
    response = client.chat.completions.create(
        model=model_selection,
        messages=st.session_state.messages,
    )
    assistant_reply = response.choices[0].message.content  # Use .content attribute

    with st.chat_message("assistant"):
        st.markdown(assistant_reply)
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

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
