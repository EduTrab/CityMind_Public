import streamlit as st
from llm.mcqa_generator import download_new_batch_llm_mcqa

def handle_generation_button():
    # 1) Guard: only run when the user clicks the button
    if not st.button("LLM closed Q&A"):
        return

    st.session_state.question_mode = "llm_mcqa"

    # 2) Swap in a ready‐to‐go prefetched_batch if we have one…
    if st.session_state.prefetched_batch:
        st.session_state.current_batch = st.session_state.prefetched_batch
        st.session_state.prefetched_batch = []
    else:
        # …otherwise download a fresh batch right now
        st.session_state.current_batch = download_new_batch_llm_mcqa(
            llm_server=st.session_state.llm_server
        )

    # 3) Immediately kick off the next‐batch download in the background
    st.session_state.is_prefetching = True
    st.session_state.prefetched_batch = download_new_batch_llm_mcqa(
        llm_server=st.session_state.llm_server
    )
    st.session_state.is_prefetching = False
