import streamlit as st

def render_tutorial():
    st.title("📘 How to Use CityMind")

    st.markdown("## 💡 What is CityMind?")
    st.markdown("""
CityMind is a tool for generating **closed-ended urban observation questions** from Street View images using Large Language Models (LLMs).  
Each batch contains 3–10 images, and your goal is to label each with the best multiple-choice answer from 6 options.
    """)

    st.markdown("---")
    st.markdown("## 🗂️ Dataset Modes and Use Cases")

    st.markdown("""
CityMind supports 3 types of datasets:

### 🔹 1. Default Dataset
- Automatically downloads random Street View images from diverse global cities
- Click **LLM closed Q&A** to generate questions
- Background prefetch prepares the next batch while you label

### 🔹 2. Local Dataset
- Upload your own `.jpg` or `.png` images (optionally with `.json` metadata)
- Click **LLM closed Q&A** to generate questions

**Duplicate Detection Flow:**
- Already-processed filenames will trigger a warning
- Select duplicates using the multiselect shown
- Click **Force Upload Selected Duplicates** to rename and reprocess
- Then click **LLM closed Q&A** again to process them

### 🔹 3. City Dataset
- Enter a city name (e.g. _Istanbul_, _Nairobi_) in the sidebar
- Images are fetched directly from that location using Street View
""")

    st.markdown("---")
    st.markdown("## 📸 What Makes a Good Image?")
    st.markdown("Good input images are crucial for useful questions.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("✅ **Good Image**")
        st.markdown("""
- Outdoor, street-level scene  
- Daytime lighting  
- Clear sidewalks, buildings, vegetation, or public space  
- Moderate zoom (not extreme close-up or drone-level)

Examples:
- A busy plaza with people and seating
- A side street with varied building heights
- A residential zone showing entrances and greenery
        """)
    with col2:
        st.markdown("❌ **Bad Image**")
        st.markdown("""
- Indoor rooms, stairwells  
- Blurry or low resolution  
- Mostly sky, or blank walls  
- Extreme zoom on signs or faces

Avoid:
- Images that only show sky or ground
- Blank parking lots with no context
- Crowded interiors where urban logic is unclear
        """)

    st.markdown("---")
    st.markdown("## 🧠 What Makes a Good Question?")
    st.markdown("""
Each image is turned into one **MCQA (Multiple-Choice Question with 6 Options)**:
- A, B, C, D, E, F
- ✅ 1 **Correct**
- ⚠️ 4 **Plausible but wrong**
- 🤡 1 **Absurdum** (clearly false)

### A Good Question...
- ✅ Is **answerable using the image only**
- ✅ Involves reasoning (not spotting)
- ✅ Can be understood even without seeing the options
- ✅ Tests spatial logic, relationships, or typologies

""")

    st.markdown("### 💬 Good vs Bad Example")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("❌ **Poor Question**")
        st.code("Are there benches?")
        st.caption("Too simple. Doesn’t require reasoning.")
    with col2:
        st.markdown("✅ **Better Question**")
        st.code("Which element most supports the space being used for resting or gathering?")
        st.caption("Requires identifying spatial design, seating, and context clues.")

    st.markdown("### 🏗️ Question Format Summary")
    st.markdown("""
| Type | Meaning |
|------|---------|
| ✅ 1 Correct | Supported by clear visual evidence |
| ⚠️ 4 Plausible | Sound possible, but not supported by the image |
| 🤡 1 Absurdum | Visibly ridiculous or impossible (e.g., airport runway in a narrow alley) |
""")

    st.markdown("### 🌍 Topics Chosen by the AI")
    st.markdown("""
Questions are generated from real urban theory topics:

- **Density & Land Use** — residential, mixed-use, commercial
- **Urban Design & Aesthetics** — signage, materials, layout
- **Mobility & Transport** — car access, walkability, transit
- **Public Space Typologies** — plaza, market, intersection, park
- **Atmosphere & Social Use** — activity levels, seating, shade
- **Cultural Markers** — flags, murals, statues, religious architecture
- **Accessibility** — ramps, curbs, clear signage
- **Safety & Comfort** — lighting, separation, openness
""")

    st.markdown("---")
    st.markdown("## ⚙️ Recommended Settings and Flow")
    st.markdown("""
- **Batch Size**: 3–5 images recommended (Max = 10)
- **Prefetch**: App will fetch next batch silently in background
- ✅ Wait for prefetch to finish before submitting
- Use sidebar to:
    - Switch dataset source
    - Set batch size
    - Choose LLM model (Gemini, GPT-4, etc.)
- Use password gate to control public access
""")

    st.markdown("## 🔁 Summary Workflow")
    st.markdown("""
1. Pick your dataset mode (Default, Local, City)  
2. Upload files or choose a city  
3. Click **LLM closed Q&A**  
4. Wait for questions to appear  
5. Answer each using the **radio buttons**  
6. Click **Submit All Answers** (only available after prefetch finishes)  
7. Answers and JSONs are uploaded to Google Drive  
""")
