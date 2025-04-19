import streamlit as st
from llm.mcqa_generator import download_new_batch_llm_mcqa


def handle_generation_button():
    # 1) On every run, if we've already prefetched a batch, consume it now
    if st.session_state.prefetched_batch:
        st.session_state.current_batch = st.session_state.prefetched_batch
        st.session_state.prefetched_batch = []

    # 2) Only also on a fresh click, generate a brand-new batch
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
                    "⚠️ Could not process any of the selected images. They may be invalid or already processed."
                )
        else:
            st.warning(
                "✅ All uploaded local images have already been processed.\n\n"
                "Please upload new images or select the Default Dataset from the sidebar."
            )
    else:
        # on button-click in Default or City mode, always download a fresh batch
        st.session_state.current_batch = download_new_batch_llm_mcqa(
            llm_server=st.session_state.llm_server
        )
