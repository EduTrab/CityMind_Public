import streamlit as st

def render_intro():
    st.title("Street View Image Labeling - LLM Generate Closed-Ended Q&A")
    st.markdown(
        """
        **Instructions**:
        1. Choose a batch size and LLM model from the sidebar.
        2. Select a dataset source:
           - **Default Dataset**: Downloads images from Street View.
           - **Local Dataset**: Upload your own images.
        3. Click **LLM closed Q&A** to process images.
        4. Review (and optionally refine) the generated MCQs, then click **Submit All Answers**.
        """
    )
