import streamlit as st
from llm.mcqa_generator import download_new_batch_llm_mcqa
from ui.batch_components import (
    render_question_card,
    render_feedback_block,
    process_submission_batch
)

def render_batch_interface(llm_server):
    # ── Setup flags ─────────────────────────────────────────────────────
    if "upload_notice" not in st.session_state:
        st.session_state.upload_notice = (
            "🚀 Your answers are being saved and uploaded in the background."
        )
    if "is_prefetching" not in st.session_state:
        st.session_state.is_prefetching = False

    st.markdown(f"🚀 {st.session_state.upload_notice}")

    # ── Helpers ──────────────────────────────────────────────────────────
    def silent_prefetch():
        """Download the next batch into prefetched_batch."""
        st.session_state.is_prefetching = True
        st.session_state.prefetched_batch = download_new_batch_llm_mcqa(
            llm_server=llm_server
        )
        st.session_state.is_prefetching = False

    # ── 1) Render the form & current batch ───────────────────────────────
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

    # ── 2) On form submit: process answers and rerun ────────────────────
    if submit:
        with st.spinner("Processing submissions…"):
            process_submission_batch(st.session_state.current_batch, llm_server)
            st.session_state.feedback_reset_counter += 1

        # The next run will swap in whatever is in prefetched_batch
        st.experimental_rerun()

    # ── 3) Only after the UI is drawn, kick off background prefetch ──────
    #     (so the “Downloading…” logs appear *after* the questions)
    if (
        st.session_state.dataset_source != "Local Dataset"
        and not st.session_state.prefetched_batch
        and not st.session_state.is_prefetching
    ):
        silent_prefetch()
