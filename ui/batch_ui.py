# ui/batch_ui.py
import streamlit as st
from llm.mcqa_generator import download_new_batch_llm_mcqa
from ui.batch_components import render_question_card, render_feedback_block, process_submission_batch

def render_batch_interface(llm_server):
    # 1) One‑time defaults
    if "upload_notice" not in st.session_state:
        st.session_state.upload_notice = "🚀 Your answers are being saved and uploaded in the background."
    if "is_prefetching" not in st.session_state:
        st.session_state.is_prefetching = False

    st.markdown(f"🚀 {st.session_state.upload_notice}")

    # 2) Helper to fetch in background
    def silent_prefetch():
        st.session_state.is_prefetching = True
        st.session_state.prefetched_batch = download_new_batch_llm_mcqa(llm_server)
        st.session_state.is_prefetching = False

    # 3) Run one silent prefetch *before* showing the form
    if (
        st.session_state.dataset_source != "Local Dataset"
        and not st.session_state.prefetched_batch
        and not st.session_state.is_prefetching
    ):
        silent_prefetch()

    # 4) All your questions + feedback + the **only** submit button
    with st.form("batch_form"):
        for i, record in enumerate(st.session_state.current_batch):
            render_question_card(record, i)
            render_feedback_block(record, i)

        submit = st.form_submit_button(
            "Submit All Answers",
            disabled=st.session_state.is_prefetching,
            help=(
                "⏳ Still downloading the next batch…"
                if st.session_state.is_prefetching else None
            )
        )

    # 5) When they click inside-the-form “Submit All Answers”:
    if submit:
        # a) Process & save/refine everything
        with st.spinner("Processing submissions…"):
            process_submission_batch(st.session_state.current_batch, llm_server)
            st.session_state.feedback_reset_counter += 1

        # b) Swap in the batch we already prefetched (or download live)
        if st.session_state.prefetched_batch:
            st.session_state.current_batch = st.session_state.prefetched_batch
            st.session_state.prefetched_batch = []
        else:
            st.session_state.current_batch = download_new_batch_llm_mcqa(llm_server)

        # c) Kick off the next background fetch
        if st.session_state.dataset_source != "Local Dataset":
            silent_prefetch()

        # d) Finally, rerun so the UI immediately shows the new batch
        st.experimental_rerun()
