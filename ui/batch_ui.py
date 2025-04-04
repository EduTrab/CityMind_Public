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

    for i, record in enumerate(st.session_state.current_batch):
        render_question_card(record, i)
        render_feedback_block(record, i)

    def trigger_prefetch():
        st.session_state.is_prefetching = True
        st.session_state.prefetched_batch = download_new_batch_llm_mcqa(llm_server=llm_server)
        st.session_state.is_prefetching = False

    if not st.session_state.prefetched_batch and not st.session_state.is_prefetching:
        st.markdown("🔄 Downloading next batch... Submition possible in a few seconds ⏳")
        trigger_prefetch()

    submit_disabled = st.session_state.is_prefetching
    submit_label = "Submit All Answers" if not submit_disabled else "⏳ Prefetching next batch..."
    submit_help = None if not submit_disabled else "Wait for the new batch to finish downloading before submitting."

    # Display submit button (always visible)
    st.button(
        label=submit_label,
        key="submit_batch_button",
        disabled=submit_disabled,
        help=submit_help
    )

    # ✅ Extra confirmation if ready
    if not submit_disabled:
        st.caption("✅ Next batch ready. You can submit now.")

    # Handle button click manually (when not disabled)
    if not submit_disabled and st.session_state.get("submit_batch_button"):
        with st.spinner("Processing submissions..."):
            process_submission_batch(st.session_state.current_batch, llm_server)
            st.session_state.feedback_reset_counter += 1
            st.rerun()
