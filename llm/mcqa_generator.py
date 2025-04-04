import os
import random
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.common.index_utils import get_next_idx
from utils.streetview.fetch import search_and_download_random



def prompt_text(n=20):
    correct_answer_number= random.randint(1,6)
    absurdum_answer_number=random.randint(1,6)


    while absurdum_answer_number==correct_answer_number:
        absurdum_answer_number=random.randint(1,6)


    number_to_letter={
        1:"A",
        2:'B',
        3:'C',
        4:'D',
        5:'E',
        6:'F'
    }
    correct_answer_letter=number_to_letter[correct_answer_number]
    absurdum_answer_letter=number_to_letter[absurdum_answer_number]

    topics=["""
    * **Density and Variability**:
    - How many structures, people, or elements are present
    - Presence or absence of specific features
    """,
    """
    * **Position and Relationship**:
    - The spatial arrangement of elements
    - Proximity and orientation of buildings, sidewalks, public furniture, etc.
    """,
    """
    * **Land Use and Built Environment**:
    - Building types, density, architectural styles, apparent zoning (commercial vs. residential)
    - Infrastructure (roads, sidewalks, utilities), presence of green space
    - Signs of decay, renovation, or development
    """,
    """
    * **Social Interaction and Public Space**:
    - How people might use the space (walking, cycling, gathering)
    - Evidence of social activity, accessibility, and inclusivity
    - Presence of street furniture, seating, or gathering spots
    """,
    """
    * **Types and Character of Spaces for Social Interaction**:
    - Identifiable typologies (plazas, squares, parks, multipurpose areas)
    - Physical or spatial features encouraging or hindering interaction (benches, raised platforms, variations in level)
    """,
    """
    * **Safety and Perceived Safety**:
    - Visual cues indicating safety or unsafety (lighting, visibility, foot traffic)
    - Consideration of different user perspectives (e.g., young female, older adults, etc.)
    """,
    """
    * **Culture and Identity**:
    - Local landmarks, cultural markers, public art
    - Ephemeral elements that contribute to a neighborhood’s identity
    """,
    """
    * **Atmosphere and Urban Dynamics**:
    - Overall vibe or liveliness
    - Indicators of gentrification, urban renewal processes, or community changes
    """,
    """
    * **Livability and Quality of Life**:
    - Comfort, convenience, and well-being factors observed
    - Amenities, cleanliness, environmental quality
    """,
    """
    * **Transportation and Mobility**:
    - Modes of transport visible
    - Traffic flow, pedestrian infrastructure, parking availability
    - Accessibility for different mobility needs
    """,
    """
    * **Urban Design and Aesthetics**:
    - Overall visual character, streetscape design
    - Presence of public art, signage, landscaping, cleanliness
    """,
    """
    * **Economic Activity**:
    - Types of businesses present
    - Signs of economic vitality or decline
    - Presence of advertising or commercial activity
    """,
    """
    * **Sustainability and Environmental Aspects**:
    - Presence of green infrastructure (trees, parks, green roofs)
    - Evidence of sustainable practices (bike lanes, solar panels)
    - Potential environmental concerns (pollution, lack of greenery)
    """,
    """
    * **Cultural Significance**:
    - Presence of cultural institutions (museums, theaters)
    - Evidence of diverse communities, cultural events, or celebrations
    """,
    """
    * **Accessibility and Inclusivity**:
    - Features for people with disabilities (ramps, wide sidewalks)
    - Indications the space is welcoming to diverse groups (signage, language use, etc.)
    """,
    """
    * **Regulatory and Planning Aspects**:
    - Evidence of zoning regulations (signage, building heights)
    - Traffic calming measures, public notices about planning
    - Construction permits, posted regulations
    """,
    """
    * **Temporality and Change**:
    - Indicators of the time of day or season
    - Signs of construction or renovation
    - Temporary installations or events
    """,
    """
    * **Materiality and Texture**:
    - Types of materials used in buildings and streetscape
    - Condition of surfaces (pavement, walls)
    - The interplay of light and shadow
    """
    ]

    sampled_topics = random.sample(topics, int(len(topics) * n / 100))
    concatenated_topics = "\n".join(sampled_topics)




    prompt=f"""
    Role: You are an advanced AI model. Your task is to analyze a Street View image (provided separately) and generate a thought-provoking, cognitively challenging question that tests higher-order reasoning about the image.

    **Input:** A Street View image (provided separately).

    **Task:** Examine the provided Street View image meticulously. Based on your observations of the image alone, generate **one** challenging, closed-ended question relevant to one of the following topics, with **exactly six** answers (labeled A, B, C, D, E, and F), 1 true, 4 possibles but objectivly false for the given picture and 1 absurdum answers.
    The Correct answer must corresponding to letter ({correct_answer_letter}), while the absurdum to letter ({absurdum_answer_letter}).

    **Topics for Question Generation:**
    Your question should focus on aspects observable in the image that relate to key concepts in urban analysis, such as:
    {concatenated_topics}


    **Constraints:**

    *   **Directly Observable:** The question and its answer choices MUST be answerable solely from the information visible in the provided image. Do not make assumptions or introduce information not directly observable.
    *   **Image-Dependent Questions:** Questions should be crafted so that they cannot be answered correctly by only reading the answer choices and without examining the image. The image must be essential to determining the correct answer. (For example, avoid questions where only one answer choice mentions "greenery" if the focus area is **Sustainability**. The user should need to look at the image to determine if greenery is present.)
    *   **Challenging:** The question should require careful observation and analysis of the image, not just a superficial description.
    *   **Unambiguous Correct Answer:** Only one answer choice should be definitively correct based on the image.
    *   **Clear Reasoning:** Briefly explain why the chosen answer is the correct one, referencing specific elements in the image that support your reasoning. Also, briefly explain why the other options are incorrect.

    **Output Format:**

    QUESTION: [Your question text]
    A) [Option 1]
    B) [Option 2]
    C) [Option 3]
    D) [Option 4]
    E) [Option 5]
    F) [Option 6]
    CORRECT_ANSWER: [A, B, C, D, E, or F]
    REASON: [Short explanation of why the answer is correct, referencing specific visual elements in the image. Also, a short explanation of why the other options are false. Mention which of the  options is the absurdum clearly false]


    **Key Changes and Explanations:**

    *   **"Directly Observable"** instead of "Direct Observable": Added the "ly" to make it an adverb.
    *   **"Image-Dependent Questions"** instead of "Image-Based Only":  Reworded this constraint to be clearer and more active. Also changed explanation, removed a repetition ("only") and fixed a misspelling ("eaven").
    *   **Combined Constraints:** Combined the first two original constraints to avoid redundancy, as they essentially convey the same idea.
    *   **"of why the answer is correct"** added in the REASON part of the output format.
    *   **"Also, a short explanation..."** added in the REASON part to clarify that the reasoning should also address why the other options are wrong.
    *   **Minor wording tweaks:** Made small changes throughout for better readability (e.g., "the true question" changed to "why the answer is correct").

    **Example of Depth**:
    Poor Example (Superficial):
    "Does this image show any cars?" — Answers would be trivially observable, testing minimal reasoning.

    Better Example (Cognitively Deeper):
    "Which of the following best describes how (part of the scene) is (aspect of that part to understand) , considering ...?"

    This improved question requires the viewer to look for multiple visual clues  and interpret them, instead of  merely identifying a single object.


    Your goal: Produce an insightful, multi-faceted urban studies question that tests the model’s cognitive prowess by integrating specific observations into a unified, closed-ended question with six choices, and only one well-supported correct answer in Letter({correct_answer_letter}).
    """

    return prompt



def generate_city_perturbations(base_lat, base_lon, n, radius_km=1.0):
    # Approx conversion: 1km ≈ 0.009 degrees
    max_offset = radius_km * 0.009
    return [
        (
            base_lat + random.uniform(-max_offset, max_offset),
            base_lon + random.uniform(-max_offset, max_offset)
        )
        for _ in range(n)
    ]


# ----------------------------------------------------
# DOWNLOAD & INITIAL PROCESSING
# ----------------------------------------------------
def download_new_batch_llm_mcqa(llm_server, paths=None, model=None, batch_size=None):
    """
    Generates a batch of MCQs using LLM closed-ended question mode.

    Parameters:
        llm_server (MultiLLMService): LLM interface.
        paths (optional): List of file paths or pre-structured record dicts.
        model (optional): Which model to use.
        batch_size (optional): Defaults to current Streamlit session batch size.

    Returns:
        new_batch (list): MCQ records with metadata.
    """
    if model is None:
        model = st.session_state.get("selected_model", "gemini-reasoning")
    if batch_size is None:
        batch_size = int(st.session_state.get("batch_size", 3))
    start_idx = get_next_idx()
    current_model = model

    # Step 1: Get image/JSON pairs
    if paths is None:
        print("🧪 download_new_batch_llm_mcqa() called with paths=None (=> Street View)")

        # 🔁 Generate N varied coordinates from base city point
        coords_list = None
        if "city_latlon" in st.session_state and st.session_state.city_latlon:
            base_lat, base_lon = st.session_state.city_latlon
            coords_list = generate_city_perturbations(base_lat, base_lon, batch_size)

        downloaded = []
        with st.spinner("Downloading images..."):
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(search_and_download_random, start_idx + i, coords=coords_list[i] if coords_list else None)
                    for i in range(batch_size)
                ]
                for future in as_completed(futures):
                    img, jsn = future.result()
                    if img and jsn:
                        downloaded.append((img, jsn))
        st.success(f"Downloaded {len(downloaded)} images.")
    else:
        print("🧪 download_new_batch_llm_mcqa() received", len(paths), "records")
        downloaded = []

        if isinstance(paths[0], dict):
            downloaded = [(rec["image_path"], rec["json_path"]) for rec in paths[:batch_size]]
        else:
            json_files = [p for p in paths if p.lower().endswith('.json')]
            image_extensions = ['.png', '.jpg', '.jpeg']
            if json_files:
                for json_path in json_files:
                    base = os.path.splitext(json_path)[0]
                    image_path = None
                    for ext in image_extensions:
                        temp_image_path = f"{base}{ext}"
                        if os.path.exists(temp_image_path):
                            image_path = temp_image_path
                            break
                    if image_path:
                        downloaded.append((image_path, json_path))
                    else:
                        st.warning(f"Image file for {json_path} not found.")
            else:
                image_files = [p for p in paths if p.lower().endswith(tuple(image_extensions))]
                downloaded.extend([(img_path, None) for img_path in image_files])

    # Step 2: LLM MCQA generation
    with st.spinner("Generating MCQs..."):
        def process_image(img, jsn):
            print(f"⚙️ Processing image: {img}, JSON: {jsn}")
            max_retries = 3
            for attempt in range(max_retries):
                if not os.path.exists(img):
                    print("🚫 Image file not found:", img)
                    return None
                if jsn and not os.path.exists(jsn):
                    print("⚠️ JSON file not found (ok if not required):", jsn)

                model_response = llm_server.send_query(
                    image_path=img,
                    prompt=prompt_text(),
                    model=current_model
                )
                if not model_response:
                    print("❌ Empty LLM response")

                print(model_response)
                print("________")
                mc_question = None
                mc_options = {"A": "", "B": "", "C": "", "D": "", "E": "", "F": ""}
                mc_correct = "?"
                mc_reason = ""
                lines = model_response.splitlines()
                for ind, line in enumerate(lines):
                    line_strip = line.strip()
                    lcase = line_strip.lower()
                    if lcase.startswith("question:"):
                        mc_question = line_strip.split(":", 1)[1].strip()
                    elif lcase.startswith("a)"):
                        mc_options["A"] = line_strip[2:].strip()
                    elif lcase.startswith("b)"):
                        mc_options["B"] = line_strip[2:].strip()
                    elif lcase.startswith("c)"):
                        mc_options["C"] = line_strip[2:].strip()
                    elif lcase.startswith("d)"):
                        mc_options["D"] = line_strip[2:].strip()
                    elif lcase.startswith("e)"):
                        mc_options["E"] = line_strip[2:].strip()
                    elif lcase.startswith("f)"):
                        mc_options["F"] = line_strip[2:].strip()
                    elif lcase.startswith("correct_answer:"):
                        chunk = line_strip.split(":", 1)[1].strip()
                        if chunk and chunk[0].upper() in ["A", "B", "C", "D", "E", "F"]:
                            mc_correct = chunk[0].upper()
                    elif lcase.startswith("reason:"):
                        mc_reason = "\n".join(lines[ind:])
                        break
                if mc_question:
                    return {
                        "image_path": img,
                        "json_path": jsn,
                        "question_mode": "llm_mcqa",
                        "mc_question": mc_question,
                        "mc_options": mc_options,
                        "mc_correct": mc_correct,
                        "mc_reason": mc_reason,
                        "user_choice": None,
                        "feedback": ""
                    }
            print(f"[DEBUG] Failed to parse question for {img}")
            return None

        new_batch = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_image, img, jsn) for img, jsn in downloaded]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    new_batch.append(result)

    st.success(f"Generated {len(new_batch)} MCQs (mode: llm_mcqa).")

    if paths is None:
        from utils.common.cleanup import remove_stale_images
        remove_stale_images()

    return new_batch


