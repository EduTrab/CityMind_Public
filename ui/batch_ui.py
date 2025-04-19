import streamlit as st
from ui.batch_components import (
    render_question_card,
    render_feedback_block,
    process_submission_batch
)

def render_batch_interface(llm_server):

    # 2) All questions + feedback in one form
    with st.form("batch_form"):
        for i, record in enumerate(st.session_state.current_batch):
            render_question_card(record, i)
            render_feedback_block(record, i)

        submit = st.form_submit_button("Submit All Answers")

    # 3) On form submit: save/refine, bump counter, then rerun
    if submit:
        process_submission_batch(st.session_state.current_batch, llm_server)
        st.session_state.feedback_reset_counter += 1
        st.experimental_rerun()
