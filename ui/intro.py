import streamlit as st

def render_intro():
    st.title("Street View Image Labeling - LLM Generate Closed-Ended Q&A")
    st.markdown(
        """
        **Instructions**:
        1. Choose a batch size from the sidebar.
        2. Select a dataset source:
           - **Default Dataset**: Downloads images from Street View.
           - **Local Dataset**: Upload your own images.
           - **City Dataset**: Choose the City you want to analyse.
        3. Click **LLM closed Q&A** to process images.
        4. Review (and optionally refine) the generated MCQs, then click **Submit All Answers**.
        5. **IMPORTANT** : At least 1 image per batch needs to be selected as **not relevant**.
        """
    )
