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
    1) Show the current batch in a form
    2) On submit: ensure at least one "Not Relevant" is selected, then process/refine
    3) After rendering: prefetch the next batch in background
    """

    # ── 1) Ensure our flags exist ──────────────────────────────────────
    if "upload_notice" not in st.session_state:
        st.session_state.upload_notice = (
            "🚀 Your answers are being saved and uploaded in the background."
        )
    if "is_prefetching" not in st.session_state:
        st.session_state.is_prefetching = False

    st.markdown(f"🚀 {st.session_state.upload_notice}")

    # ── 2) Prefetch helper ────────────────────────────────────────────
    def silent_prefetch():
        st.session_state.is_prefetching = True
        st.session_state.prefetched_batch = download_new_batch_llm_mcqa(
            llm_server=llm_server
        )
        st.session_state.is_prefetching = False

    # ── 3) Render the form for the current batch ───────────────────────
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

    # ── 4) On submit: validate “Not Relevant” + process answers/refinements ──
    if submit:
        # require at least one “Not Relevant”
        # Check if at least one image is marked as "Not Relevant"
        has_not_relevant = any(r.get("user_choice") == "Not Relevant" 
                              for r in st.session_state.current_batch)
        
        # Check if we're looking at a full batch (not a refined subset)
        is_full_batch = len(st.session_state.current_batch) == st.session_state.get("batch_size", 3)
        
        # Require "Not Relevant" selection only for full batches
        if not has_not_relevant and is_full_batch:
            st.warning("⚠️ Please mark at least one image as Not Relevant before submitting.")
        else:
            with st.spinner("Processing submissions…"):
                process_submission_batch(st.session_state.current_batch, llm_server)
                st.session_state.feedback_reset_counter += 1

            # mark submission so main app can clear or re-show as needed
            st.session_state.just_submitted = True

            # re-run to redraw (either empty or with refined cards)
            st.rerun()

    # ── 5) After rendering, kick off background prefetch if needed ─────
    if (
        st.session_state.dataset_source != "Local Dataset"
        and not st.session_state.prefetched_batch
        and not st.session_state.is_prefetching
    ):
        silent_prefetch()
