import streamlit as st
import uuid


def initialize_session_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    if "current_batch" not in st.session_state:
        st.session_state.current_batch = []
    if "prefetched_batch" not in st.session_state:
        st.session_state.prefetched_batch = []
    if "local_records" not in st.session_state:
        st.session_state.local_records = []
    if "batch_size" not in st.session_state:
        st.session_state.batch_size = 3
    if "feedback_reset_counter" not in st.session_state:
        st.session_state.feedback_reset_counter = 0
    if "previous_dataset_source" not in st.session_state:
        st.session_state.previous_dataset_source = st.session_state.get("dataset_source", "Default Dataset")
    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = st.secrets.get("google_gemini_api_key", "")