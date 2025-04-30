import os
import random
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.common.index_utils import get_next_idx
from utils.streetview.fetch import search_and_download_random_maps, search_and_download_random_mly



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



# Combined catalogue: every topic immediately followed by ONE illustrative
# few-shot example in the exact target layout.
# -----------------------------------------------------------------------

    topics = [
        # 1 ─ Density & Variability
        """
    * **Density & Variability**
    - **Ask** : “How diverse or crowded are the visible elements?”
    - **Look for** : variety of people/vehicles/buildings, differences in style or size,
        foreground vs. background occlusion.
    - **Mind** : don’t demand exact counts when objects overlap—use ranges or relative terms.

    QUESTION: Which description best matches the variety of vehicle types visible on the street?
    A) Only passenger cars can be seen
    B) A mix of cars, bicycles, and a delivery van
    C) Two buses dominate the scene
    D) Exclusive presence of motorcycles
    E) Freight trains pass behind the buildings
    F) No vehicles are present
    CORRECT_ANSWER: B
    REASON: Cars, several cyclists, and a white delivery van are clearly visible; no buses, trains, or motor-only situation.
    TOPIC: Density & Variability — element diversity assessment
    """,
        # 2 ─ Land-Use & Built Form
        """
    * **Land-Use & Built Form**
    - **Ask** : “Which land-use types or structural features appear?”
    - **Look for** : façades, signage, setbacks, driveway widths, mixed-use clues
        (retail ground floor, residential above).
    - **Mind** : never guess legal zoning; only reference what signage or form proves.

    QUESTION: What land-use is most clearly indicated by the ground-floor units on the right?
    A) Residential flats
    B) Light industrial workshops
    C) Retail shops with signage
    D) Agricultural storage barns
    E) Government offices
    F) School classrooms
    CORRECT_ANSWER: C
    REASON: Glass storefronts with sale signs line the right façade; no flats, industry, barns, offices or school rooms evident.
    TOPIC: Land-Use & Built Form — retail presence
    """,
        # 3 ─ Public-Space Use & Social Interaction
        """
    * **Public-Space Use & Social Interaction**
    - **Ask** : “How are people engaging with shared outdoor space?”
    - **Look for** : posture (walking, sitting, queuing), grouping, orientation,
        supporting furniture (benches, shade).
    - **Mind** : don’t infer conversations or relationships you can’t see/hear.

    QUESTION: What primary social activity is occurring around the fountain?
    A) People standing in a queue
    B) Joggers passing without stopping
    C) Children playing and splashing water
    D) Street vendors setting up stalls
    E) Cyclists repairing bikes
    F) No one near the fountain
    CORRECT_ANSWER: C
    REASON: Four children are playing in water jets; no queue, joggers, vendors, cyclists, or emptiness observed.
    TOPIC: Public-Space Use & Social Interaction — play behaviour
    """,
        # 4 ─ Gathering-Space Typology
        """
    * **Gathering-Space Typology**
    - **Ask** : “Which space type best labels this gathering spot?”
    - **Look for** : enclosure, edge vs. centre activity, surface treatment,
        temporary vs. permanent fixtures.
    - **Mind** : don’t call a circulation corridor a plaza unless people linger there.

    QUESTION: Which typology best describes the paved area in front of the museum entrance?
    A) Linear transit corridor
    B) Pocket park
    C) Pedestrian plaza
    D) Highway interchange
    E) Private courtyard
    F) Rooftop terrace
    CORRECT_ANSWER: C
    REASON: Wide paved expanse with seating and standing pedestrians denotes plaza; not a corridor, interchange, park, etc.
    TOPIC: Gathering-Space Typology — plaza identification
    """,
        # 5 ─ Safety & Perceived Safety
        """
    * **Safety & Perceived Safety**
    - **Ask** : “What cues suggest safety or risk?”
    - **Look for** : lighting, clear sight-lines, active frontages, surveillance cameras,
        accessible kerbs.
    - **Mind** : avoid stereotyping users or fear-mongering language.

    QUESTION: Which element most directly enhances nighttime safety on this street?
    A) Overhead LED streetlights
    B) High concrete barriers
    C) Dense tree canopy blocking view
    D) Broken windows on shops
    E) Absence of pedestrians
    F) Garbage piled against walls
    CORRECT_ANSWER: A
    REASON: Bright LED poles line both kerbs; barriers, canopy, broken windows, emptiness, garbage do not boost safety.
    TOPIC: Safety & Perceived Safety — lighting cue
    """,
        # 6 ─ Culture & Identity
        """
    * **Culture & Identity**
    - **Ask** : “Which cultural markers express local identity?”
    - **Look for** : murals, flags, language on signs, vernacular materials,
        festival decor.
    - **Mind** : acknowledge multiple cultures if visible; don’t over-generalise.

    QUESTION: Which cultural marker stands out on the bakery façade?
    A) A large national flag banner
    B) Graffiti tags in multiple languages
    C) Traditional mosaic of local fruit motif
    D) Neon sign in generic English font
    E) Corporate franchise logo
    F) No cultural marker present
    CORRECT_ANSWER: C
    REASON: Coloured tile mosaic of regional fruit decorates façade; not flag, graffiti, neon, franchise logo or nothing.
    TOPIC: Culture & Identity — vernacular decoration
    """,
        # 7 ─ Atmosphere & Urban Dynamics
        """
    * **Atmosphere & Urban Dynamics**
    - **Ask** : “What is the energy level or vibe?”
    - **Look for** : pedestrian flow, musicians, open mouths (talking/singing),
        warm/cool lighting.
    - **Mind** : describe, don’t judge (“lively” vs. “good/bad”).

    QUESTION: Which phrase best captures the overall vibe of the scene?
    A) Quiet residential cul-de-sac
    B) Bustling commercial high street
    C) Deserted industrial park
    D) Night-time festival crowd
    E) Suburban strip mall at dawn
    F) Rural farmland lane
    CORRECT_ANSWER: B
    REASON: Crowds, open shops, and heavy foot traffic create a bustling commercial feel; other descriptions mismatch.
    TOPIC: Atmosphere & Urban Dynamics — energy level inference
    """,
        # 8 ─ Livability & Comfort
        """
    * **Livability & Comfort**
    - **Ask** : “How comfortable or convenient does it appear?”
    - **Look for** : shade, seating, greenery, overall upkeep, mixed amenities.
    - **Mind** : don’t project personal lifestyle preferences.

    QUESTION: Which amenity most improves pedestrian comfort along this block?
    A) Continuous shade from awnings
    B) Loud construction noise
    C) Lack of any seating
    D) Closed shop shutters
    E) Overflowing trash bins
    F) Potholes in the sidewalk
    CORRECT_ANSWER: A
    REASON: Fabric awnings span storefronts providing shade; others describe negative or absent features.
    TOPIC: Livability & Comfort — shading amenity
    """,
        # 9 ─ Transport & Mobility
        """
    * **Transport & Mobility**
    - **Ask** : “Which travel modes and infrastructures are present?”
    - **Look for** : sidewalks, bike lanes, bus stops, parking, curb cuts.
    - **Mind** : don’t infer service frequency or usage stats.

    QUESTION: What piece of transport infrastructure is clearly visible near the intersection?
    A) Marked bicycle lane
    B) Helipad
    C) Subway station entrance
    D) Shipping dock
    E) Airport runway sign
    F) Horse carriage stand
    CORRECT_ANSWER: A
    REASON: Painted bike symbols and green pavement appear curbside; no helipad, subway entrance, docks, runway, or carriages evident.
    TOPIC: Transport & Mobility — cycle facility
    """,
        #10 ─ Urban Design & Aesthetics
        """
    * **Urban Design & Aesthetics**
    - **Ask** : “How do form, proportion and details shape the streetscape?”
    - **Look for** : façade rhythm, material palette, signage coherence,
        street furniture style.
    - **Mind** : use neutral descriptive language, not value judgements.

    QUESTION: How are the shopfront signs along the left façade arranged?
    A) Irregular sizes and random heights
    B) Uniform height and consistent serif font
    C) Neon script stacked vertically
    D) Digital billboards rotating adverts
    E) Hand-painted signs on shutters
    F) No signs present
    CORRECT_ANSWER: B
    REASON: All signs sit on the same lintel line and share matching serif font; others incorrect.
    TOPIC: Urban Design & Aesthetics — façade rhythm
    """,
        #11 ─ Economic Activity
        """
    * **Economic Activity**
    - **Ask** : “What signs of commerce or economic vitality are visible?”
    - **Look for** : open storefronts, street vendors, advertising density, vacancy signs.
    - **Mind** : don’t forecast long-term economics from one snapshot.

    QUESTION: Which indicator suggests strong street-level commerce in the image?
    A) Multiple open shop doors with customers
    B) Boarded-up windows
    C) Empty display shelves
    D) For-lease banners on every unit
    E) Closed metal shutters
    F) No built structures at all
    CORRECT_ANSWER: A
    REASON: Several shops have doors open, customers inside; other options conflict with visible activity.
    TOPIC: Economic Activity — open retail units
    """,
        #12 ─ Sustainability & Environment
        """
    * **Sustainability & Environment**
    - **Ask** : “Which sustainable features or concerns are evident?”
    - **Look for** : tree canopy, bike infrastructure, permeable paving, solar panels,
        litter or smoke.
    - **Mind** : don’t quote carbon metrics or policies you can’t see.

    QUESTION: Which sustainability feature is prominently visible on the building roofs?
    A) Extensive green roofs with vegetation
    B) Large diesel generators
    C) Rooftop swimming pools
    D) Piles of construction debris
    E) Satellite dishes only
    F) Nothing installed on roofs
    CORRECT_ANSWER: A
    REASON: Lush green roof gardens cover rooftops; no generators, pools, debris, dishes-only or blank roofs seen.
    TOPIC: Sustainability & Environment — green roof presence
    """,
        #13 ─ Accessibility & Inclusivity
        """
    * **Accessibility & Inclusivity**
    - **Ask** : “Is the setting welcoming for diverse abilities?”
    - **Look for** : ramps, tactile strips, inclusive signage, varied seating.
    - **Mind** : focus on visible affordances, not legal compliance claims.

    QUESTION: Which accessibility element can be observed at the mid-block crossing?
    A) Curb ramps with tactile paving
    B) Steep uncut kerbs
    C) Staircase leading directly to road
    D) Chain barrier blocking access
    E) No crossing treatment
    F) Construction trench
    CORRECT_ANSWER: A
    REASON: Sloped ramps with dotted tactile strips flank zebra lines; other listed impediments absent.
    TOPIC: Accessibility & Inclusivity — curb-ramp feature
    """,
        #14 ─ Regulation & Planning Cues
        """
    * **Regulation & Planning Cues**
    - **Ask** : “What hints of planning or regulation are observable?”
    - **Look for** : permits, zoning notices, traffic-calming devices,
        construction hoardings.
    - **Mind** : don’t interpret legal text; just note its presence.

    QUESTION: What planning notice is posted on the construction fence?
    A) Permit board detailing approved redevelopment
    B) Concert advertisement poster
    C) Welcome mural by local school
    D) Political campaign banner
    E) Graffiti tag only
    F) No signage at all
    CORRECT_ANSWER: A
    REASON: Official permit board lists project details; other items (concert, mural, banner, graffiti, none) not present.
    TOPIC: Regulation & Planning Cues — permit signage
    """,
        #15 ─ Materiality & Texture
        """
    * **Materiality & Texture**
    - **Ask** : “Which materials and surface qualities dominate?”
    - **Look for** : masonry, glass, timber, pavement texture, patina.
    - **Mind** : avoid inferring structural integrity or cost.

    QUESTION: Which paving material covers the main pedestrian walkway?
    A) Red clay bricks
    B) Polished granite slabs
    C) Weathered timber boards
    D) Gravel surface
    E) Asphalt only
    F) Sand beach
    CORRECT_ANSWER: B
    REASON: Smooth reflective granite slabs are visible underfoot; no bricks, timber, gravel, asphalt-only or sand evident.
    TOPIC: Materiality & Texture — pavement finish
    """
    ]

    topics_high_level = [
    "Density & Variability – assess how diverse or crowded the visible elements are (people, vehicles, buildings) using relative terms rather than exact counts.",
    "Land-Use & Built Form – identify land-use types and structural cues from façades, signage, and form, without guessing legal zoning.",
    "Public-Space Use & Social Interaction – observe how people occupy and interact within shared outdoor spaces (posture, grouping, furniture).",
    "Gathering-Space Typology – classify the kind of public space (plaza, park, corridor, etc.) based on enclosure, activity, and fixtures.",
    "Safety & Perceived Safety – note features that influence perceived safety such as lighting, visibility, active frontages, and upkeep.",
    "Culture & Identity – recognise cultural markers (murals, flags, language, vernacular materials) that express local identity.",
    "Atmosphere & Urban Dynamics – gauge the overall vibe or energy level from pedestrian flow, activity intensity, and ambient cues.",
    "Livability & Comfort – look for comfort-enhancing amenities like shade, seating, greenery, and general maintenance quality.",
    "Transport & Mobility – detect present travel modes and infrastructures (sidewalks, bike lanes, bus stops, parking).",
    "Urban Design & Aesthetics – describe formal and aesthetic qualities such as façade rhythm, material palette, and signage coherence.",
    "Economic Activity – spot visible signs of commerce and vitality (open shops, street vendors, advertising density, vacancies).",
    "Sustainability & Environment – observe sustainable features or concerns (tree canopy, green roofs, bike infra, litter, smoke).",
    "Accessibility & Inclusivity – identify visible affordances that support diverse abilities (ramps, tactile strips, inclusive signage).",
    "Regulation & Planning Cues – note any observable planning or regulatory indicators (permit boards, zoning notices, traffic calming).",
    "Materiality & Texture – describe the dominant materials and surface textures in buildings and pavements (masonry, glass, timber, patina)."
]



    sampled_topics = random.sample(topics_high_level, n)
    concatenated_topics = "\n".join(sampled_topics)




    prompt = f"""ROLE
    You are a senior “visual-question author” for an urban-analytics dataset.
    You will see **one** Street-View image and must write **one** 
    multiple-choice question that can be answered *only* by inspecting that image.

    INPUTS
    • image   : a Street-View panorama (supplied separately)  
    • topics  : {concatenated_topics}  
    • letter  : {correct_answer_letter}   ← the option that MUST be correct

    TASK
    1. Build a precise mental scene graph (objects, counts, positions, relations).  
    2. Choose **one** suitable domain from *topics*.  
    3. Craft a closed-ended question that demands careful visual reasoning.  
    4. Write **exactly six** answer choices (A–F): **one** true (its letter == *letter*),
    **five** clearly false for this image.  
    5. Add a brief reason: why the true option is correct and each other is false,
    citing concrete visual cues.

    QUALITY BAR  
    ✓ Image-dependent – cannot be answered without the photo.  
    ✓ Unambiguous – only one option fits.  
    ✓ Non-trivial – deeper than “Is there a car?”.  
    ✓ Concise – ≤ 2 short sentences per field.

    OUTPUT FORMAT  (write nothing else!)

    QUESTION: <one interrogative sentence>
    A) <answer text>
    B) <answer text>
    C) <answer text>
    D) <answer text>
    E) <answer text>
    F) <answer text>
    CORRECT_ANSWER: <A|B|C|D|E|F>      ← must equal {correct_answer_letter}
    REASON: <why correct; why others wrong – reference specific visual cues>
    TOPIC: <chosen topic from list + why it fits>

    EXAMPLES  (observe the exact layout)

    QUESTION: Which side of the street features the only visible bus-stop shelter?
    A) North side
    B) South side
    C) East side
    D) West side
    E) Both sides
    F) No bus-stop visible
    CORRECT_ANSWER: B
    REASON: A blue shelter and bus-stop pole stand on the south pavement; no shelter elsewhere.
    TOPIC: Transit accessibility – stop placement

    QUESTION: What obstructs the dedicated cycle lane closest to the camera?
    A) A parked van
    B) Rubbish bins
    C) Outdoor café tables
    D) Road-works cones
    E) Nothing – it is clear
    F) Police barrier tape
    CORRECT_ANSWER: A
    REASON: A white delivery van is parked fully over the green cycle lane; no bins, cones or tape present.
    TOPIC: Active mobility – cycle-lane blockage

    QUESTION: Which building material dominates the façades on the left side?
    A) Red brick
    B) Exposed concrete
    C) Glass curtain-wall
    D) Timber cladding
    E) Polished granite
    F) White stucco
    CORRECT_ANSWER: C
    REASON: The left row is a continuous glass-clad office block; other materials are absent.
    TOPIC: Architectural style – façade materials
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
                    executor.submit(search_and_download_random_mly, start_idx + i, coords=coords_list[i] if coords_list else None)
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
                    prompt=prompt_text(n=2),
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


