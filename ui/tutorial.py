import streamlit as st

def render_tutorial():
    st.title("📘 How to Use CityMind")
    
    st.markdown("### 💡 Overview")
    st.markdown("""
CityMind generates visual reasoning questions from Street View images using powerful LLMs.  
You’ll interact with batches of 3–10 images at a time and select the most accurate multiple-choice answer for each.

""")

    st.markdown("### 📂 Dataset Modes")
    st.markdown("""
#### 1. **Default Dataset**
- Downloads random images from global cities
- Click **LLM closed Q&A** to begin
- Prefetches the next batch while you answer the current one

#### 2. **Local Dataset**
- Upload your own `.jpg` / `.png` images (optionally with `.json`)
- Click **LLM closed Q&A** to generate questions

**Duplicate Detection Workflow:**
- If your uploaded file already exists in `answered_images/`, you’ll see:
  - A warning message listing duplicates
  - A multiselect where you can choose which to rename
  - A button: **Force Upload Selected Duplicates** to rename & reprocess
- Afterwards, click **LLM closed Q&A** again to process the renamed images

#### 3. **City Dataset**
- Enter a city name in the sidebar (e.g. `Helsinki`, `Bangkok`)
- System will download Street View images from that location
""")

    st.markdown("---")
    st.markdown("### 📸 What Makes a Good Image?")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("✅ **Good:**")
        st.markdown("""
- Clear, outdoor street-level image  
- Multiple urban elements (buildings, sidewalks, vegetation, people)  
- Daytime lighting  
- Public space with identifiable structures
        """)
    with col2:
        st.markdown("❌ **Bad:**")
        st.markdown("""
- Indoors (offices, hallways)  
- Zoomed too close (signs, walls)  
- Blurry or dark  
- Mostly sky or empty fields  
""")

    st.markdown("---")
    st.markdown("### 🧠 What Makes a Good Question?")
    st.markdown("""
CityMind uses a **fixed MCQA structure** per image:
- Exactly **6 options** (A–F)
  - ✅ 1 Correct
  - ⚠️ 4 Plausible but wrong
  - 🤡 1 Absurd (clearly false)

A good question:
- ✅ Must be **answerable from the image only**
- ✅ Requires reasoning, not spotting
- ✅ Makes sense **even without the answer options**

**Common Topics the AI uses:**
- 🏙️ Density, land use, building types  
- 🚲 Public space, social interaction  
- 🌱 Sustainability, vegetation, green space  
- ✨ Atmosphere, culture, identity  
- ♿ Accessibility, inclusivity  
- 🚧 Safety, mobility, traffic separation  
""")

    st.markdown("### ✍️ Examples")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**❌ Poor Question:**")
        st.code("Are there trees?")
        st.caption("Too obvious — requires no reasoning")
    with col2:
        st.markdown("**✅ Better Question:**")
        st.code("Which element best conveys the area's sustainable design?")
        st.caption("Requires observation of materials, layout, vegetation")

    st.markdown("### 🗂️ Urban Topics Used by the AI")
    st.markdown("Some of the key domains sampled randomly for each question:")

    st.markdown("""
- **Density and Variability**: building count, land use  
- **Public Space**: furniture, interaction, gathering  
- **Safety and Comfort**: lighting, visibility, separation  
- **Culture and Identity**: landmarks, signs, public art  
- **Accessibility**: ramps, inclusive signage, barriers  
- **Atmosphere**: lively vs. empty, signs of renewal  
""")

    st.markdown("### ⚙️ Settings & Tips")
    st.markdown("""
- **Recommended Batch Size:** 3–5 images (Max 10)  
- ✅ Answer all questions before clicking **Submit All Answers**
- ⚠️ Don’t click **Submit** while “Prefetching...” is shown  
- Use **City Dataset** for targeted urban areas  
""")


