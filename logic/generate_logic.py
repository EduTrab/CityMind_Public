import streamlit as st
from llm.mcqa_generator import download_new_batch_llm_mcqa

def handle_generation_button():
    if "is_generating_batch" not in st.session_state:
        st.session_state.is_generating_batch = False

    # Show a notice if generation is already running
    if st.session_state.is_generating_batch:
        st.info("⚙️ Generating batch... please wait.")

    # Disable button during generation
    button_disabled = st.session_state.is_generating_batch
    clicked = st.button("LLM closed Q&A", disabled=button_disabled)

    if clicked and not button_disabled:
        st.session_state.is_generating_batch = True
        st.session_state.question_mode = "llm_mcqa"

        if st.session_state.dataset_source == "Local Dataset":
            if st.session_state.local_records:
                batch = st.session_state.local_records[:st.session_state.batch_size]
                remaining = st.session_state.local_records[st.session_state.batch_size:]

                new_batch = download_new_batch_llm_mcqa(st.session_state.llm_server, paths=batch)

                if new_batch:
                    st.session_state.current_batch = new_batch
                    st.session_state.local_records = remaining
                else:
                    st.warning("⚠️ Could not process any of the selected images. They may be invalid or already processed.")
            else:
                st.warning("✅ All uploaded local images have already been processed.\n\nPlease upload new images or select the Default Dataset from the sidebar.")
        else:
            if st.session_state.prefetched_batch:
                st.session_state.current_batch = st.session_state.prefetched_batch
                st.session_state.prefetched_batch = []
            else:
                st.session_state.current_batch = download_new_batch_llm_mcqa(llm_server=st.session_state.llm_server)

        st.session_state.is_generating_batch = False
