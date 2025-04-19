import os
import streamlit as st
from PIL import Image
from utils.common.io_ops import save_and_move_image
from llm.refinement import iterative_refinement

def render_question_card(record, i):
    image_path = record["image_path"]
    qmode = record["question_mode"]

    if os.path.exists(image_path):
        st.image(
            Image.open(image_path),
            caption=f"Image #{os.path.basename(image_path)}",
            use_container_width=True
        )

    if qmode == "llm_mcqa":
        question_text = record.get("mc_question", "No MC question found.")
        options = record.get("mc_options", {})
        correct_ans = record.get("mc_correct", "?")
        reason_text = record.get("mc_reason", "")

        st.markdown(f"**MC Question (image #{i+1})**:\n\n{question_text}")
        answer_choices = list(options.keys()) + ["Not Relevant"]
        displayed = [f"{letter}) {options.get(letter, '')}" for letter in answer_choices]
        
        # Pre-select the user's previous choice, or fall back to first option
        user_choice = record.get("user_choice") or answer_choices[0]

        radio_key = f"llm_mcqa_radio_{i}"
        with st.container():
            st.markdown(f"<label for='{radio_key}'>Select answer (image {i+1}):</label>", unsafe_allow_html=True)
            chosen = st.radio(
                label="",
                options=displayed,
                index=answer_choices.index(user_choice) if user_choice in answer_choices else 0,
                key=radio_key
            )

        record["user_choice"] = chosen.split(")", 1)[0].strip()
        print(f"[UI] User selected for Q{i}: {record['user_choice']} (key={radio_key})")

        with st.expander("View LLM Responds"):
            st.write(f"**LLM's Reason:** {reason_text}")
            st.write(f"**Correct Answer (LLM):** {correct_ans}")
    else:
        st.warning(f"Unknown question_mode: {qmode}")

def render_feedback_block(record, i):
    feedback_text = st.text_area(
        label=f"Feedback to refine question (image {i+1}):",
        key=f"feedback_{i}_{st.session_state.feedback_reset_counter}",
        help="Provide feedback to improve the generated question. Leave empty if not needed."
    )
    record["feedback"] = feedback_text


def get_corresponding_lightweight_models(model): 
    if model=="gemini-reasoning":
        return "gemini-1.5-flash-002"
    raise F"THE GIVEN MODEL {model} is not supported. ADD IT"

def process_submission_batch(records, llm_server):
    current_model = st.session_state.selected_model
    lightweight_model = get_corresponding_lightweight_models(current_model)

    records_no_feedback = [r for r in records if not r.get("feedback", "").strip()]
    records_with_feedback = [r for r in records if r.get("feedback", "").strip()]

    # ✅ Collect user answers from widget state just before saving
    for i, record in enumerate(records_no_feedback):
        key = f"llm_mcqa_radio_{i}"
        selected_raw = st.session_state.get(key)
        if selected_raw:
            record["user_choice"] = selected_raw.split(")", 1)[0].strip()
        else:
            record["user_choice"] = "?"  # fallback

        st.write(f"📥 [NO FEEDBACK] Q{i} | `{os.path.basename(record['image_path'])}` | user_choice = `{record['user_choice']}`")
        save_and_move_image(record)

    # ✅ Process refined questions (feedback present)
    updated_records = []
    # ✅ Collect user answers from widget state just before saving
    for i, record in enumerate(records_no_feedback):
        key = f"llm_mcqa_radio_{i}"
        selected_raw = st.session_state.get(key)

        # ⛳️ DEBUG PRINTS
        st.write("----")
        st.write(f"🔑 Widget key: {key}")
        st.write(f"📥 Widget raw value: {selected_raw}")
        st.write(f"🖼️  Image path: {record.get('image_path')}")
        st.write(f"📋  MCQ: {record.get('mc_question', '')[:40]}...")

        if selected_raw:
            record["user_choice"] = selected_raw.split(")", 1)[0].strip()
        else:
            record["user_choice"] = "?"

        st.write(f"✅ Final choice: {record['user_choice']}")

        save_and_move_image(record)


    # Save updated records into session
    st.session_state.current_batch = updated_records
