import os
import streamlit as st
from PIL import Image
from llm.mcqa_generator import download_new_batch_llm_mcqa
from utils.common.io_ops import save_and_move_image
from llm.refinement import iterative_refinement
from utils.common.cleanup import remove_stale_images
from ui.batch_components import render_question_card, render_feedback_block, process_submission_batch
from llm.mcqa_generator import download_new_batch_llm_mcqa


def render_batch_interface(llm_server):
    for i, record in enumerate(st.session_state.current_batch):
        render_question_card(record, i)
        render_feedback_block(record, i)

    if len(st.session_state.prefetched_batch) == 0:
        st.session_state.prefetched_batch = download_new_batch_llm_mcqa(llm_server=llm_server)

    if st.button("Submit All Answers"):
        with st.spinner("Processing submissions..."):
            process_submission_batch(st.session_state.current_batch, llm_server)
            st.session_state.feedback_reset_counter += 1
            st.rerun()
