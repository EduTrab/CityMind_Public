# logic/generate_logic.py

import streamlit as st
from llm.mcqa_generator import download_new_batch_llm_mcqa

def handle_generation_button():
    """
    When the user clicks "LLM closed Q&A", advance to the next batch:
      - If we've prefetched one, swap it in.
      - Otherwise, download a fresh batch.
    Also reset the 'just_submitted' flag so the UI knows this is a new batch.
    """
    if not st.button("LLM closed Q&A"):
        return

    st.session_state.question_mode = "llm_mcqa"

    if st.session_state.dataset_source == "Local Dataset":
        if st.session_state.local_records:
            batch = st.session_state.local_records[:st.session_state.batch_size]
            remaining = st.session_state.local_records[st.session_state.batch_size:]

            new_batch = download_new_batch_llm_mcqa(
                st.session_state.llm_server,
                paths=batch
            )

            if new_batch:
                st.session_state.current_batch = new_batch
                st.session_state.local_records = remaining
            else:
                st.warning(
                    "Could not process any of the selected images. "
                    "They may be invalid or already processed."
                )
        else:
            st.warning(
                "✅ All uploaded local images have already been processed.\n\n"
                "Please upload new images or select the Default Dataset from the sidebar."
            )
    else:
        # Default / City dataset
        if st.session_state.prefetched_batch:
            st.session_state.current_batch = st.session_state.prefetched_batch
            st.session_state.prefetched_batch = []
        else:
            st.session_state.current_batch = download_new_batch_llm_mcqa(
                llm_server=st.session_state.llm_server
            )

    # We’re now showing a fresh batch → clear the just_submitted marker
    st.session_state.just_submitted = False
