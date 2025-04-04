import streamlit as st




def render_sidebar_controls():
    # Batch size
    st.session_state.batch_size = st.sidebar.number_input("Batch size", min_value=1, max_value=200, value=3, step=1)

    # Model
    model_options = [
        "gpt-4o", "gpt-4-turbo", "gpt-4o-mini", "llama3.2-vision",
        "llava", "qnguyen3/nanollava", "claude-3-opus-20240229", "gemini-reasoning"
    ]
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "gemini-reasoning"
    st.session_state.selected_model = st.sidebar.selectbox(
        "Choose LLM Model",
        options=model_options,
        index=model_options.index(st.session_state.selected_model)
    )

    # Dataset source
    dataset_options = ["Default Dataset", "Local Dataset", "City Dataset"]
    if "dataset_source" not in st.session_state:
        st.session_state.dataset_source = dataset_options[0]
    st.session_state.dataset_source = st.sidebar.selectbox(
        "Select Dataset Source",
        options=dataset_options,
        index=dataset_options.index(st.session_state.dataset_source)
    )
    if st.session_state.dataset_source == "City Dataset":
        city_input = st.sidebar.text_input("Enter City Name", value=st.session_state.get("city_name", ""))
        st.session_state.city_name = city_input

        # Show coordinate feedback right after input
        if "city_latlon" in st.session_state and st.session_state.city_latlon:
            lat, lon = st.session_state.city_latlon
            st.sidebar.markdown(f"📍 Using coordinates: **{lat:.5f}, {lon:.5f}**")

    # API keys
    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = st.secrets.get("google_gemini_api_key", "")