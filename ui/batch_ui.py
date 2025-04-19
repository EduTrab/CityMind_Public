# ui/batch_ui.py

import streamlit as st
from llm.mcqa_generator import download_new_batch_llm_mcqa
from ui.batch_components import (
    render_question_card,
    render_feedback_block,
    process_submission_batch
)

def render_batch_interface(llm_server):
    """
    Display the current batch in a form, handle Submit All Answers
    (including LLM‐driven refinements), and prefetch the next batch.
    """

    # ── 1) One‑time setup ────────────────────────────────────────────────
    if "upload_notice" not in st.session_state:
        st.session_state.upload_notice = (
            "🚀 Your answers are being saved and uploaded in the background."
        )
    if "is_prefetching" not in st.session_state:
        st.session_state.is_prefetching = False

    st.markdown(f"🚀 {st.session_state.upload_notice}")

    # ── 2) Prefetch helper ───────────────────────────────────────────────
    def silent_prefetch():
        st.session_state.is_prefetching = True
        st.session_state.prefetched_batch = download_new_batch_llm_mcqa(
            llm_server=llm_server
        )
        st.session_state.is_prefetching = False

    # ── 3) Render form for the current batch ─────────────────────────────
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

    # ── 4) On submit: process answers/refinements ────────────────────────
    if submit:
        with st.spinner("Processing submissions…"):
            # This will:
            #  • Save & remove any records without feedback
            #  • Refine & keep any records with feedback (updating their questions/options)
            process_submission_batch(st.session_state.current_batch, llm_server)
            # Reset feedback inputs
            st.session_state.feedback_reset_counter += 1
        # **No explicit rerun or manual clearing**—the form will naturally rerun
        # and re-render using the new st.session_state.current_batch.

    # ── 5) After UI draws, kick off background prefetch if needed ────────
    if (
        st.session_state.dataset_source != "Local Dataset"
        and not st.session_state.prefetched_batch
        and not st.session_state.is_prefetching
    ):
        silent_prefetch()
