import streamlit as st
import csv
import os
from datetime import datetime
import pandas as pd
from idea_generator import (
    build_persona,
    generate_ideas,
    assess_feasibility,
    suggest_names,
    generate_pitch,
    get_related_trends
)

# ---------------------------
# Page Setup & Styling
# ---------------------------
st.set_page_config(page_title="Startup Ideation Chatbot", page_icon="🚀", layout="wide")

st.markdown(
    """
    <style>
      .main { background-color: #fafafa; }
      .stButton>button {
          border-radius: 10px; padding: 0.6rem 1rem; font-weight: 600;
          border: 1px solid rgba(0,0,0,0.08); box-shadow: 0 2px 8px rgba(0,0,0,0.05);
      }
      .block-title { font-size: 20px; font-weight: 700; margin-top: 1rem; }
      .subtle { color: #666; }
      .card {
          background: #fff; border-radius: 14px; padding: 16px 18px; 
          border: 1px solid rgba(0,0,0,0.06); box-shadow: 0 1px 8px rgba(0,0,0,0.04);
      }
      .fit-badge {
          background:#eef8f1; color:#0f5132; padding:2px 8px; border-radius:999px; font-size:12px;
      }
      .gap-badge {
          background:#fff3cd; color:#664d03; padding:2px 8px; border-radius:999px; font-size:12px;
      }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🚀 Startup Ideation Chatbot")
st.caption("Persona-first ideation • Feasibility mapping • Names & pitch")

# ---------------------------
# Sidebar Controls
# ---------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    model = st.text_input("HF Model", os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3"))
    temp_persona = st.slider("Temperature (Persona)", 0.0, 1.2, 0.5, 0.1)
    temp_ideas = st.slider("Temperature (Ideas)", 0.0, 1.2, 0.7, 0.1)
    temp_names = st.slider("Temperature (Names)", 0.0, 1.2, 0.9, 0.1)
    st.markdown("---")
    st.info("Tip: set your `.env` with `HF_TOKEN` and `HF_MODEL`.\nYou can also change the model above for experiments.")

# ---------------------------
# Session State
# ---------------------------
if "persona" not in st.session_state:
    st.session_state.persona = None
if "persona_text" not in st.session_state:
    st.session_state.persona_text = ""
if "ideas" not in st.session_state:
    st.session_state.ideas = []
if "fit" not in st.session_state:
    st.session_state.fit = []
if "picked_index" not in st.session_state:
    st.session_state.picked_index = 0

# ---------------------------
# Input Form (Persona)
# ---------------------------
st.markdown("### 1) Tell me about yourself")
with st.form("persona_form"):
    col1, col2 = st.columns(2)
    with col1:
        background = st.text_area("Background", placeholder="e.g., MBA + 1 year in D2C marketing")
        skills = st.text_area("Skills", placeholder="e.g., Python, SQL, UX, GTM, partnerships")
        interests = st.text_area("Interests", placeholder="e.g., healthtech, supply chain, climate")
    with col2:
        experiences = st.text_area("Past Experiences", placeholder="e.g., Built a campus app; interned at HRIPL")
        current_position = st.text_input("Current Position", placeholder="e.g., Final-year MBA")
        goals = st.text_area("Goals / Motives", placeholder="e.g., financial freedom, social impact, autonomy")
        aspirations = st.text_area("Future Aspirations", placeholder="e.g., build a global AI-enabled skincare brand")

    build = st.form_submit_button("🧩 Build Persona")

if build:
    with st.spinner("Crafting your persona..."):
        person_in = {
            "background": background,
            "skills": skills,
            "interests": interests,
            "experiences": experiences,
            "current_position": current_position,
            "goals": goals,
            "aspirations": aspirations,
        }
        persona, persona_text = build_persona(person_in, temperature=temp_persona)
        st.session_state.persona = persona
        st.session_state.persona_text = persona_text

if st.session_state.persona:
    st.markdown("### 👤 Your Persona")
    st.markdown(st.session_state.persona_text)

# ---------------------------
# Idea Inputs
# ---------------------------
st.markdown("### 2) Context for Ideas")
colA, colB = st.columns([2, 1])
with colA:
    industry = st.text_input("Industry", placeholder="e.g., Beauty & Personal Care, Fintech, Edtech")
    problem = st.text_area("Problem statement", placeholder="e.g., Indian Tier-2 shoppers struggle to discover safe lip-care options")
with colB:
    n_ideas = st.number_input("How many ideas?", min_value=1, max_value=6, value=3, step=1)
generate_btn = st.button("💡 Generate Tailored Ideas", disabled=not bool(st.session_state.persona and industry and problem))

if generate_btn:
    with st.spinner("Generating tailored ideas..."):
        ideas = generate_ideas(
            st.session_state.persona,
            industry=industry,
            problem=problem,
            n_ideas=int(n_ideas),
            temperature=temp_ideas
        )
        st.session_state.ideas = ideas
        st.session_state.fit = assess_feasibility(st.session_state.persona, ideas)

# ---------------------------
# Output Tabs
# ---------------------------
tabs = st.tabs(["💡 Ideas", "🧮 Feasibility", "🏷️ Names & Pitch", "📊 Trends", "📥 Exports"])

# --- Tab 1: Ideas ---
with tabs[0]:
    if not st.session_state.ideas:
        st.info("Generate ideas to see them here.")
    else:
        for i, idea in enumerate(st.session_state.ideas):
            with st.container(border=True):
                st.markdown(f"#### {i+1}. {idea.get('title','(untitled)')}")
                st.caption(idea.get("elevator_pitch",""))
                st.write(idea.get("description",""))
                st.markdown("**Why it fits you**")
                st.write(idea.get("why_fit",""))
                comps = idea.get("competencies_required", [])
                if comps:
                    st.markdown("**Competencies required**")
                    st.write(", ".join(comps))
        st.session_state.picked_index = st.number_input(
            "Pick an idea for names & pitch (index)", min_value=1, max_value=len(st.session_state.ideas), value=1
        ) - 1

# --- Tab 2: Feasibility ---
with tabs[1]:
    fit = st.session_state.fit or []
    if not fit:
        st.info("Feasibility appears after ideas are generated.")
    else:
        rows = []
        for item in fit:
            rows.append({
                "Idea": item.get("title",""),
                "Fit Score": item.get("fit_score", 0),
                "Matched Strengths": " | ".join(item.get("matched_strengths", [])),
                "Key Gaps": " | ".join(item.get("gaps", [])),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        with st.expander("📅 90-day plans (per idea)"):
            for item in fit:
                st.markdown(f"**{item.get('title','')}**")
                plan = item.get("ninety_day_plan", [])
                st.write("\n".join([f"- {p}" for p in plan]) if plan else "—")

# --- Tab 3: Names & Pitch ---
with tabs[2]:
    if not st.session_state.ideas:
        st.info("Generate ideas first.")
    else:
        idx = st.session_state.picked_index
        picked = st.session_state.ideas[idx]
        st.markdown(f"#### Selected Idea: {picked.get('title','')}")
        kw = st.text_input("Optional keywords for names", value="")
        colx, coly = st.columns(2)
        with colx:
            if st.button("✨ Suggest Names"):
                with st.spinner("Finding brandable names..."):
                    names = suggest_names(picked.get("title",""), keywords=kw)
                    if names:
                        st.success("Here are some options:")
                        st.write(", ".join(names))
                    else:
                        st.warning("Name suggestions not available this time.")
        with coly:
            pitch_tone = st.selectbox("Pitch tone", ["crisp, benefit-led", "visionary", "casual", "premium"])
            if st.button("📝 Generate Pitch"):
                with st.spinner("Drafting pitch..."):
                    pitch = generate_pitch(picked, tone=pitch_tone)
                    st.info(pitch)

# --- Tab 4: Trends ---
with tabs[3]:
    topic = st.text_input("Topic for Google Trends (optional)", value=industry if 'industry' in locals() else "")
    if st.button("🔎 Fetch Trends") and topic.strip():
        with st.spinner("Fetching related queries..."):
            trends_df = get_related_trends(topic)
            if trends_df is not None:
                st.markdown("##### Related Google Trends (Top)")
                st.table(trends_df)
            else:
                st.warning("No trends found or topic not tracked.")

# --- Tab 5: Exports ---
with tabs[4]:
    if st.session_state.ideas:
        csv_path = "startup_ideas.csv"
        try:
            top = st.session_state.ideas[st.session_state.picked_index]
        except Exception:
            top = st.session_state.ideas[0]

        row = [
            datetime.now().isoformat(timespec="seconds"),
            st.session_state.persona.get("summary",""),
            top.get("title",""),
            top.get("elevator_pitch",""),
            top.get("description",""),
            "|".join(top.get("competencies_required", [])),
        ]

        try:
            exists = os.path.exists(csv_path)
            with open(csv_path, "a", newline="") as f:
                writer = csv.writer(f)
                if not exists:
                    writer.writerow(["timestamp","persona_summary","idea_title","elevator_pitch","description","competencies"])
                writer.writerow(row)
            with open(csv_path, "rb") as f:
                st.download_button("📥 Download Ideas CSV", f, file_name="startup_ideas.csv", mime="text/csv")
            st.caption("New entry appended to startup_ideas.csv")
        except Exception as e:
            st.error(f"Could not write CSV: {e}")
    else:
        st.info("Generate at least one idea to enable exports.")