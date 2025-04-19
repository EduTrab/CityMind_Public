import streamlit as st
from llm.mcqa_generator import download_new_batch_llm_mcqa
from ui.batch_components import render_question_card, render_feedback_block, process_submission_batch


def render_batch_interface(llm_server):
    # Initialize upload notice and prefetch state
    if "upload_notice" not in st.session_state:
        st.session_state.upload_notice = "🚀 Your answers are being saved and uploaded in the background."
    if "is_prefetching" not in st.session_state:
        st.session_state.is_prefetching = False

    # Display notice
    st.markdown(f"🚀 {st.session_state.upload_notice}")

    # Wrap questions + feedback in a form with its own submit button
    with st.form("batch_form"):
        for i, record in enumerate(st.session_state.current_batch):
            render_question_card(record, i)
            render_feedback_block(record, i)

        submit = st.form_submit_button(
            label="Submit All Answers",
            disabled=st.session_state.is_prefetching,
            help=(
                "Please wait until next batch is downloaded before submitting."
                if st.session_state.is_prefetching else None
            )
        )

    # When the form is submitted:
    if submit:
        # 1) Process and save their answers
        with st.spinner("Processing submissions…"):
            process_submission_batch(st.session_state.current_batch, llm_server)
            # Increment the counter for feedback keys if still in use
            st.session_state.feedback_reset_counter = st.session_state.get("feedback_reset_counter", 0) + 1

        # 2) Immediately prefetch your next batch
        st.session_state.is_prefetching = True
        st.session_state.prefetched_batch = download_new_batch_llm_mcqa(llm_server=llm_server)
        st.session_state.is_prefetching = False

        # 3) Refresh UI to show new batch
        st.experimental_rerun()
