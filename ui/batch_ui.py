# ui/batch_ui.py
import os
import streamlit as st
from llm.mcqa_generator import download_new_batch_llm_mcqa
from ui.batch_components import render_question_card, render_feedback_block, process_submission_batch

def render_batch_interface(llm_server):
    # ————————————————————————————————————————————————————————————————————————————————————
    # 1) Make sure we have our flags in session_state
    if "upload_notice" not in st.session_state:
        st.session_state.upload_notice = "🚀 Your answers are being saved and uploaded in the background."
    if "is_prefetching" not in st.session_state:
        st.session_state.is_prefetching = False

    st.markdown(f"🚀 {st.session_state.upload_notice}")

    # ————————————————————————————————————————————————————————————————————————————————————
    # 2) Silent prefetch helper
    def silent_prefetch():
        st.session_state.is_prefetching = True
        st.session_state.prefetched_batch = download_new_batch_llm_mcqa(llm_server=llm_server)
        st.session_state.is_prefetching = False

    # 3) Trigger exactly-once background prefetch if:
    #    • We're not on Local Dataset
    #    • There's a current batch in play
    #    • We haven't already prefetched
    #    • And we're not already mid‑prefetch
    if (
        st.session_state.dataset_source != "Local Dataset"
        and st.session_state.current_batch
        and not st.session_state.prefetched_batch
        and not st.session_state.is_prefetching
    ):
        silent_prefetch()

    # ————————————————————————————————————————————————————————————————————————————————————
    # 4) All questions + feedback inside one form, with its own active submit button
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

    # ————————————————————————————————————————————————————————————————————————————————————
    # 5) When they hit that form’s submit:
    if submit:
        # a) Process + save/refine
        with st.spinner("Processing submissions…"):
            process_submission_batch(st.session_state.current_batch, llm_server)
            st.session_state.feedback_reset_counter += 1

        # b) Swap in the batch we prefetched earlier (or fall back to live download)
        if st.session_state.prefetched_batch:
            st.session_state.current_batch = st.session_state.prefetched_batch
            st.session_state.prefetched_batch = []
        else:
            st.session_state.current_batch = download_new_batch_llm_mcqa(
                llm_server=llm_server
            )

        # c) Immediately fire off the next background prefetch
        if st.session_state.dataset_source != "Local Dataset":
            silent_prefetch()

        # d) Rerun so the UI shows the new questions
        st.experimental_rerun()
