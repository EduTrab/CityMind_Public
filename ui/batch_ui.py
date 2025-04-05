import os
import streamlit as st
from PIL import Image
from llm.mcqa_generator import download_new_batch_llm_mcqa
from utils.common.io_ops import save_and_move_image
from llm.refinement import iterative_refinement
from utils.common.cleanup import remove_stale_images
from ui.batch_components import render_question_card, render_feedback_block, process_submission_batch

def render_batch_interface(llm_server):
    if "upload_notice" not in st.session_state:
        st.session_state.upload_notice = "🚀 Your answers are being saved and uploaded in the background."
    if "is_prefetching" not in st.session_state:
        st.session_state.is_prefetching = False

    st.markdown(f"🚀 {st.session_state.upload_notice}")

    # Wrap questions + feedback in a form to suppress reruns on radio changes
    with st.form("batch_form"):
        for i, record in enumerate(st.session_state.current_batch):
            render_question_card(record, i)
            render_feedback_block(record, i)
        st.form_submit_button("Answers saved", disabled=True)

    # Trigger background prefetch silently (⚠️ NO user-visible logs)
    def silent_prefetch():
        st.session_state.is_prefetching = True
        st.session_state.prefetched_batch = download_new_batch_llm_mcqa(llm_server=llm_server)
        st.session_state.is_prefetching = False

    if (
        st.session_state.dataset_source != "Local Dataset"
        and not st.session_state.prefetched_batch
        and not st.session_state.is_prefetching
    ):
        silent_prefetch()

    # OUTSIDE the form: Real Submit Button
    submit_disabled = st.session_state.get("is_prefetching", False)
    submit_label = "Submit All Answers" if not submit_disabled else "⏳ Prefetching next batch..."
    submit_help = None if not submit_disabled else "Wait until next batch is downloaded before submitting."

    if submit_disabled:
        st.caption("🔒 Please wait — next batch is still being prepared...")

    if st.button(label=submit_label, disabled=submit_disabled, help=submit_help):
        with st.spinner("Processing submissions..."):
            process_submission_batch(st.session_state.current_batch, llm_server)
            st.session_state.feedback_reset_counter += 1
            st.rerun()
