import os
import streamlit as st
from PIL import Image
from llm.mcqa_generator import download_new_batch_llm_mcqa
from utils.common.io_ops import save_and_move_image
from llm.refinement import iterative_refinement
from ui.batch_components import render_question_card, render_feedback_block, process_submission_batch

def render_batch_interface(llm_server):
    if "upload_notice" not in st.session_state:
        st.session_state.upload_notice = "🚀 Your answers are being saved and uploaded in the background."
    if "is_prefetching" not in st.session_state:
        st.session_state.is_prefetching = False

    st.markdown(f"🚀 {st.session_state.upload_notice}")

    # ⛱️ Prefetch next batch only if Default or City dataset
    def trigger_prefetch():
        st.session_state.is_prefetching = True
        st.session_state.prefetched_batch = download_new_batch_llm_mcqa(llm_server=llm_server)
        st.session_state.is_prefetching = False

    if (
        st.session_state.dataset_source != "Local Dataset"
        and not st.session_state.prefetched_batch
        and not st.session_state.is_prefetching
    ):
        st.markdown("🔄 Downloading next batch... Submission possible in a few seconds ⏳")
        trigger_prefetch()

    # ✅ Begin single form to avoid reruns on interaction
    with st.form(key="batch_form", clear_on_submit=False):
        for i, record in enumerate(st.session_state.current_batch):
            render_question_card(record, i)
            render_feedback_block(record, i)

        # Control submit button state
        submit_disabled = st.session_state.get("is_prefetching", False)
        submit_label = "Submit All Answers"
        submit_help = "Downloading next batch in the background. Please wait..." if submit_disabled else None

        # Always visible button (disabled if needed)
        submitted = st.form_submit_button(
            label=submit_label,
            disabled=submit_disabled,
            help=submit_help
        )

    # ✅ Only run after prefetch completes and user clicks button
    if submitted and not submit_disabled:
        with st.spinner("Processing submissions..."):
            process_submission_batch(st.session_state.current_batch, llm_server)
            st.session_state.feedback_reset_counter += 1
            st.rerun()
