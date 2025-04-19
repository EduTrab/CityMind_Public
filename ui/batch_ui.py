# ui/batch_ui.py
import streamlit as st
from llm.mcqa_generator import download_new_batch_llm_mcqa
from ui.batch_components import (
    render_question_card,
    render_feedback_block,
    process_submission_batch
)

def render_batch_interface(llm_server):
    # ─── 1) Setup flags ────────────────────────────────────────────────────
    if "upload_notice" not in st.session_state:
        st.session_state.upload_notice = (
            "🚀 Your answers are being saved and uploaded in the background."
        )
    if "is_prefetching" not in st.session_state:
        st.session_state.is_prefetching = False

    st.markdown(f"🚀 {st.session_state.upload_notice}")

    # ─── 2) Helpers ────────────────────────────────────────────────────────
    def silent_prefetch():
        """Download the next batch into prefetched_batch."""
        st.session_state.is_prefetching = True
        st.session_state.prefetched_batch = download_new_batch_llm_mcqa(
            llm_server=llm_server
        )
        st.session_state.is_prefetching = False

    def load_next_batch():
        """Swap in prefetched_batch or download fresh."""
        if st.session_state.prefetched_batch:
            st.session_state.current_batch = st.session_state.prefetched_batch
            st.session_state.prefetched_batch = []
        else:
            st.session_state.current_batch = download_new_batch_llm_mcqa(
                llm_server=llm_server
            )

    # ─── 3) Initial background prefetch ────────────────────────────────────
    #    Only if we're not in Local mode, haven't already prefetched, and not mid‑prefetch.
    if (
        st.session_state.dataset_source != "Local Dataset"
        and not st.session_state.prefetched_batch
        and not st.session_state.is_prefetching
    ):
        silent_prefetch()

    # ─── 4) Render the form ─────────────────────────────────────────────────
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

    # ─── 5) On form submit ──────────────────────────────────────────────────
    if submit:
        # a) Save/refine
        with st.spinner("Processing submissions…"):
            process_submission_batch(st.session_state.current_batch, llm_server)
            st.session_state.feedback_reset_counter += 1

        # b) Swap in the batch we prefetched (or download live)
        load_next_batch()

        # c) Kick off the next background prefetch
        if st.session_state.dataset_source != "Local Dataset":
            silent_prefetch()

        # d) Rerun so the UI immediately shows the new batch
        st.experimental_rerun()
