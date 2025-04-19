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

    # Wrap everything in one form, with its own submit button
    with st.form("batch_form"):
        for i, record in enumerate(st.session_state.current_batch):
            render_question_card(record, i)
            render_feedback_block(record, i)

        # This is the button that *actually* submits the form
        submit = st.form_submit_button(
            label="Submit All Answers",
            disabled=st.session_state.is_prefetching,
            help=(
                "Please wait until next batch is downloaded before submitting."
                if st.session_state.is_prefetching else None
            )
        )

    if submit:
        # 1️⃣ Process and save their answers
        with st.spinner("Processing submissions…"):
            process_submission_batch(st.session_state.current_batch, llm_server)
            st.session_state.feedback_reset_counter += 1

        # 2️⃣ Immediately prefetch your next batch
        st.session_state.is_prefetching = True
        st.session_state.prefetched_batch = download_new_batch_llm_mcqa(llm_server=llm_server)
        st.session_state.is_prefetching = False

        # 3️⃣ Reset the form (so our next render starts fresh)
        st.experimental_rerun()

