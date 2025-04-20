import os
import streamlit as st

# UI components
from ui.intro import render_intro
from ui.sidebar import render_sidebar_controls
from ui.batch_ui import render_batch_interface
from ui.password_gate import check_password

# Session state
from utils.session.session_state import initialize_session_state

# Logic controllers
from logic.upload_logic import handle_local_upload
from logic.generate_logic import handle_generation_button

# Cleanup logic
from utils.common.cleanup import auto_clear_on_switch
from utils.streetview.geocode import resolve_city_to_coordinates

from llm.llm_service import MultiLLMService


def main():
    # 🔐 Password protection
    check_password()

    # 🧠 Header
    render_intro()

    # ⚙️ Init state
    initialize_session_state()

    # 🛠 Sidebar controls
    render_sidebar_controls()

    # 🌆 City mode geocoding
    if st.session_state.dataset_source == "City Dataset":
        if st.session_state.city_name:
            coords = resolve_city_to_coordinates(st.session_state.city_name)
            if coords:
                st.session_state.city_latlon = coords
                st.markdown(f"📍 Using coordinates: `{coords[0]:.5f}, {coords[1]:.5f}`")
            else:
                st.warning("❌ Could not resolve city. Please check spelling.")
                st.session_state.city_latlon = None

    # 🔁 Cleanup when switching dataset
    auto_clear_on_switch(
        st.session_state.previous_dataset_source,
        st.session_state.dataset_source
    )
    if st.session_state.dataset_source != "City Dataset":
        st.session_state.city_latlon = None
        st.session_state.city_name = ""
    if st.session_state.previous_dataset_source != st.session_state.dataset_source:
        st.session_state.current_batch = []
        st.session_state.prefetched_batch = []
        st.session_state.feedback_reset_counter = 0

    st.session_state.previous_dataset_source = st.session_state.dataset_source

    # 🧠 LLM setup
    llm_server = MultiLLMService(
        models_to_query=st.session_state.selected_model,
        google_genai_api_key=st.session_state.gemini_api_key
    )
    st.session_state.llm_server = llm_server

    # 📥 Local‐upload UI
    if st.session_state.dataset_source == "Local Dataset":
        handle_local_upload()

    # ▶️ “LLM closed Q&A” button logic
    handle_generation_button()

    # ─── Show either the batch UI or empty‐state message ────────────────
    if st.session_state.current_batch:
        render_batch_interface(llm_server=st.session_state.llm_server)
    else:
        # If we *just* submitted a batch, show the “saved” banner
        if st.session_state.get("just_submitted", False):
            st.success(
                "✅ Your images have been saved.  \n\n"
                "Please proceed with a new batch by pressing **LLM closed Q&A**."
            )
        else:
            st.info("No images in the current batch. Upload or download a batch to begin.")


if __name__ == "__main__":
    main()
