import streamlit as st
from utils.streetview.geocode import geocode_city_to_candidates

def render_sidebar_controls():
    # ─── Batch size ─────────────────────────────────────────────────────
    st.session_state.batch_size = st.sidebar.number_input(
        "Batch size", min_value=1, max_value=200, value=st.session_state.get("batch_size", 3), step=1
    )

    # ─── Model selection ─────────────────────────────────────────────────
    model_options = [
        "gemini-2.5-flash-preview-04-17"
    ]
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "gemini-2.5-flash-preview-04-17"
    st.session_state.selected_model = st.sidebar.selectbox(
        "LLM Model",
        options=model_options,
        index=model_options.index(st.session_state.selected_model)
    )

    # ─── Dataset source ─────────────────────────────────────────────────
    dataset_options = ["Default Dataset", "Local Dataset", "City Dataset"]
    if "dataset_source" not in st.session_state:
        st.session_state.dataset_source = dataset_options[0]
    st.session_state.dataset_source = st.sidebar.selectbox(
        "Select Dataset Source",
        options=dataset_options,
        index=dataset_options.index(st.session_state.dataset_source)
    )

    # ─── City Dataset: text → geocode → dropdown of candidates ──────────
    if st.session_state.dataset_source == "City Dataset":
        city_input = st.sidebar.text_input(
            "Enter city name",
            value=st.session_state.get("city_name", "")
        )
        st.session_state.city_name = city_input

        if city_input:
            candidates = geocode_city_to_candidates(city_input)
            if candidates:
                descriptions = [c["description"] for c in candidates]
                choice = st.sidebar.selectbox(
                    "Select the correct city",
                    descriptions
                )
                sel = next(c for c in candidates if c["description"] == choice)
                st.session_state.city_latlon = (sel["lat"], sel["lng"])
                st.sidebar.markdown(
                    f"📍 Using coordinates: **{sel['lat']:.5f}, {sel['lng']:.5f}**"
                )
            else:
                st.sidebar.warning(
                    "❌ No matching cities found. Please refine your entry."
                )
                st.session_state.city_latlon = None
        else:
            # cleared out
            st.session_state.city_latlon = None

    # ─── API keys (for Gemini) ───────────────────────────────────────────
    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = st.secrets.get("google_gemini_api_key", "")
