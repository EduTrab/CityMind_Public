import os
import random
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.common.index_utils import get_next_idx
from utils.streetview.fetch import search_and_download_random



def prompt_text(n=2):
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


    topics = [
    """
    * **Scene Understanding**:
        - **Core question**: “What is the overall theme or purpose of this place?”
        - **Analyse**: global layout, dominant land-use, activity level, mood, time-of-day/season cues.
        - **Consider**: lighting, color palette, density, presence of nature vs. built form.
        - **Avoid**: zooming into single objects, conjecturing about non-visible interiors, or inferring residents’ demographics beyond what is visually evident.
    """,
    """
    * **Instance Identity**:
        - **Core question**: “What is this specific object, or does object X appear here?”
        - **Analyse**: salient shape, size, iconography, material, immediately surrounding context.
        - **Consider**: viewpoint distortions, occlusions, and class look-alikes.
        - **Avoid**: extrapolating attributes (e.g., brand, model year) unless unmistakably visible.
    """,
    """
    * **Instance Attribute**:
        - **Core question**: “Which fine-grained attributes describe object X?”
        - **Analyse**: color, texture, subtype, condition, ornamentation.
        - **Consider**: lighting effects and reflections that may alter hue/texture.
        - **Avoid**: inferring functional or hidden traits (e.g., taste, price, policy compliance).
    """,
    """
    * **Instance Localization**:
        - **Core question**: “Where is object X located in the frame?”
        - **Analyse**: relation to frame center, depth cues.
        - **Consider**: scale invariance, partial occlusion, and perspective distortion.
        - **Avoid**: narrating exact pixel coordinates unless required; semantic judgments belong to other categories.
    """,
    """
    * **Instance Interaction**:
        - **Core question**: “What is object A doing to/with object B?”
        - **Analyse**: posture, contact points, motion blur cues, tool use, shared affordances.
        - **Consider**: sequential frames if available to confirm dynamic action.
        - **Avoid**: attributing intent, emotion, or future actions not visually grounded.
    """,
    """
    * **Density and Variability**:
        - **Core question**: “How many and how diverse are the elements present?”
        - **Analyse**: Consider people/vehicles/structures, qualitative heterogeneity of types and styles.
        - **Consider**: occlusion and perspective that may hide elements.
        - **Avoid**: exact headcounts when the scene is too crowded; provide ranges instead.
    """,
    """
    * **Land Use and Built Environment**:
        - **Core question**: “Which land-use types and infrastructural elements are visible?”
        - **Analyse**: building footprints, setbacks, road hierarchy, signage indicating zoning.
        - **Consider**: transition zones (commercial ground floor, residential upper floors).
        - **Avoid**: guessing legal zoning designations unless signage explicitly shows them.
    """,
    """
    * **Social Interaction and Public Space**:
        - **Core question**: “How are people using shared outdoor areas?”
        - **Analyse**: posture (walking, sitting, gathering), group sizes, body orientation.
        - **Consider**: supportive infrastructure (benches, shade) that enables interaction.
        - **Avoid**: assumptions about conversations or social ties not visually supported.
    """,
    """
    * **Types and Character of Spaces for Social Interaction**:
        - **Core question**: “What typology best describes this gathering space?”
        - **Analyse**: enclosure ratio, edges vs. center activation, surface treatments.
        - **Consider**: temporary vs. permanent fixtures (pop-up seating, seasonal market stalls).
        - **Avoid**: conflating circulation corridors with bona-fide gathering nodes.
    """,
    """
    * **Safety and Perceived Safety**:
        - **Core question**: “What visual cues indicate safety or its absence?”
        - **Analyse**: lighting, sightlines, surveillance (eyes on the street), active frontage.
        - **Consider**: user diversity (e.g., signage readability, curb ramps).
        - **Avoid**: fear-mongering or stereotyping based on user appearance.
    """,
    """
    * **Culture and Identity**:
        - **Core question**: “Which cultural markers convey local identity?”
        - **Analyse**: murals, flags, language on signs, vernacular architecture.
        - **Consider**: temporary cultural events (street fairs, decorations).
        - **Avoid**: reducing culture to monolithic traits; acknowledge multiplicity if visible.
    """,
    """
    * **Atmosphere and Urban Dynamics**:
        - **Core question**: “What is the vibe or energy level?”
        - **Analyse**: pedestrian flow, noise cues (open mouths, musicians), lighting warmth.
        - **Consider**: weather and time affecting foot traffic.
        - **Avoid**: prescriptive value judgments (“good” or “bad” vibe) without context.
    """,
    """
    * **Livability and Quality of Life**:
        - **Core question**: “How comfortable and convenient does the environment appear?”
        - **Analyse**: shade, seating, greenery, upkeep, mixed uses within walking distance.
        - **Consider**: inclusivity of amenities (playgrounds, senior seating).
        - **Avoid**: projecting personal lifestyle preferences onto evaluation.
    """,
    """
    * **Transportation and Mobility**:
        - **Core question**: “Which transport modes and infrastructure are present?”
        - **Analyse**: sidewalks, bike lanes, transit stops, parking, traffic flow.
        - **Consider**: accessibility features (curb cuts, tactile paving).
        - **Avoid**: inferring service frequency or ridership stats beyond visible indicators.
    """,
    """
    * **Urban Design and Aesthetics**:
        - **Core question**: “How do form, proportion, and detailing contribute to streetscape?”
        - **Analyse**: façade rhythm, material palette, signage coherence, street furniture style.
        - **Consider**: visual hierarchy, maintenance level.
        - **Avoid**: equating novelty with quality; discuss aesthetics in descriptive, not prescriptive, terms.
    """,
    """
    * **Economic Activity**:
        - **Core question**: “What signs of commerce or economic vitality are visible?”
        - **Analyse**: open storefronts, market stalls, advertising density, vacancy signs.
        - **Consider**: time-of-day influence on business activity.
        - **Avoid**: projecting long-term economic health from a single snapshot.
    """,
    """
    * **Sustainability and Environmental Aspects**:
        - **Core question**: “Which sustainable features or concerns are evident?”
        - **Analyse**: green roofs, permeable pavements, bike infrastructure, tree canopy.
        - **Consider**: visible pollution sources (smoke, litter) and mitigation measures.
        - **Avoid**: claiming carbon metrics or policy compliance without data.
    """,
    """
    * **Cultural Significance**:
        - **Core question**: “Does the image show culturally significant institutions or events?”
        - **Analyse**: museums, theaters, heritage plaques, crowd behavior suggesting festivals.
        - **Consider**: contextual signage that may point to historical importance.
        - **Avoid**: overstating importance without corroborating visual evidence.
    """,
    """
    * **Accessibility and Inclusivity**:
        - **Core question**: “Is the environment welcoming and usable for diverse abilities and groups?”
        - **Analyse**: ramps, tactile strips, inclusive signage, shelter, seating diversity.
        - **Consider**: sightlines, lighting uniformity, absence of barriers.
        - **Avoid**: assuming legal compliance; focus on visible affordances.
    """,
    """
    * **Regulatory and Planning Aspects**:
        - **Core question**: “What hints of planning or regulation are observable?”
        - **Analyse**: posted permits, zoning notices, traffic-calming devices, construction hoardings.
        - **Consider**: temporary regulations (event closures, COVID signage).
        - **Avoid**: legal interpretation; stick to visible compliance indicators.
    """,
    """
    * **Materiality and Texture**:
        - **Core question**: “What materials and surface qualities define the scene?”
        - **Analyse**: masonry vs. glass vs. wood, pavement texture, patina, reflectivity.
        - **Consider**: weathering patterns that hint at age or upkeep.
        - **Avoid**: inferring structural integrity or cost from surface appearance alone.
    """
    ]


    sampled_topics = random.sample(topics, n)
    concatenated_topics = "\n".join(sampled_topics)




    prompt=f"""
    Role: You are an advanced AI model. Your task is to analyze a Street View image (provided separately) and generate a thought-provoking, cognitively challenging question that tests higher-order reasoning about the image.

    **Input:** A Street View image (provided separately).

    **Task:** Examine the provided Street View image meticulously. Based on your observations of the image alone, generate **one** challenging, closed-ended question relevant to one of the following topics, with **exactly six** answers (labeled A, B, C, D, E, and F), 1 true and 5 possibles but objectivly false for the given picture .
    The Correct answer must corresponding to letter ({correct_answer_letter}).

    **Topics for Question Generation:**
    Your question should focus on aspects observable in the image that relate to key concepts in urban analysis, such as:
    {concatenated_topics}


    **Example of Depth**:
    Poor Example (Superficial):
    "Does this image show any cars?" — Answers would be trivially observable, testing minimal reasoning.

    Better Example (Cognitively Deeper):
    "Which of the following best describes how (part of the scene) is (aspect of that part to understand) , considering ...?"

    
    This improved question requires the viewer to look for multiple visual clues  and interpret them, instead of  merely identifying a single object.

    
    **Constraints:**

    *   **Directly Observable:** The question and its answer choices MUST be answerable solely from the information visible in the provided image. Do not make assumptions or introduce information not directly observable.
    *   **Image-Dependent Questions:** Questions should be crafted so that they cannot be answered correctly by only reading the answer choices and without examining the image. The image must be essential to determining the correct answer. (For example, avoid questions where only one answer choice mentions "greenery" if the focus area is **Sustainability**. The user should need to look at the image to determine if greenery is present.)
    *   **Unambiguous Correct Answer:** Only one answer choice should be definitively correct based on the image.
    *   **Clear Reasoning:** Briefly explain why the chosen answer is the correct one, referencing specific elements in the image that support your reasoning. Also, briefly explain why the other options are incorrect.
    *   **Not Over Verbose** Pose Challenging question and answers, without being too verbose.
    **Output Format:**

    QUESTION: [Your question text]
    A) [Option 1]
    B) [Option 2]
    C) [Option 3]
    D) [Option 4]
    E) [Option 5]
    F) [Option 6]
    CORRECT_ANSWER: [A, B, C, D, E, or F]
    REASON: [Short explanation of why the answer is correct, referencing specific visual elements in the image. Also, a short explanation of why the other options are false. 
    TOPIC: [Short explanation of why you chose this topic from **Topics for Question Generation:**, especially why it is relevant for this image]

      """

    return prompt


# *   **Clear Markdown Formatting:** Format your text using markdown to higlight the most important words of your question, and guide the user to navigate the text. Format using bold and color red  ":red[text to highlight]". 
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
                # model_response = llm_server.send_query(
                #     image_path=img,
                #     prompt = f"""
                #     # TASK  
                #     You are given the following model output describing an image:

                #     {model_response}

                #     ## Objectives  
                #     1. **Refine** the text so it is strictly relevant to the image.  
                #     2. **Format** the result with Markdown for easy skimming:  
                #     * Use headings, lists, or short paragraphs.  
                #     * Highlight critical words with the custom syntax `:red[important text]`.  
                #     3. **Trim verbosity**—make the question concise, precise, and intellectually engaging without being over-complicated.

                #      **Constraints:**

                #     *   **Directly Observable:** The question and its answer choices MUST be answerable solely from the information visible in the provided image. Do not make assumptions or introduce information not directly observable.
                #     *   **Image-Dependent Questions:** Questions should be crafted so that they cannot be answered correctly by only reading the answer choices and without examining the image. The image must be essential to determining the correct answer. (For example, avoid questions where only one answer choice mentions "greenery" if the focus area is **Sustainability**. The user should need to look at the image to determine if greenery is present.)
                #     *   **Unambiguous Correct Answer:** Only one answer choice should be definitively correct based on the image.
                #     *   **Clear Reasoning:** Briefly explain why the chosen answer is the correct one, referencing specific elements in the image that support your reasoning. Also, briefly explain why the other options are incorrect.

                #     **Output Format:**

                #     QUESTION: [Your question text]
                #     A) [Option 1]
                #     B) [Option 2]
                #     C) [Option 3]
                #     D) [Option 4]
                #     E) [Option 5]
                #     F) [Option 6]
                #     CORRECT_ANSWER: [A, B, C, D, E, or F]
                #     REASON: [Short explanation of why the answer is correct, referencing specific visual elements in the image. Also, a short explanation of why the other options are false. 
                #     TOPIC: [Short explanation of why you chose this topic from **Topics for Question Generation:**, especially why it is relevant for this image]


                #     Return only the refined, formatted text.
                #     """,
                #     model=current_model
                # )
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


