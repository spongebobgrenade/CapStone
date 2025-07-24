import streamlit as st
import csv
from datetime import datetime
from idea_generator import (
    generate_startup_idea,
    generate_pitch,
    suggest_names,
    get_related_trends
)

# Page setup
st.set_page_config(page_title="Startup Ideation Chatbot", page_icon="💡", layout="centered")
st.title("🚀 Startup Ideation Chatbot")
st.subheader("Turn your passion into a startup idea!")

# Input from user
user_topic = st.text_input("🔍 Enter a topic or field you're interested in:")

# Initialize storage variables
idea = pitch = names = None

# Generate all outputs if user clicks button
if st.button("💡 Generate Full Startup Idea", key="full_idea_btn"):
    if user_topic.strip() == "":
        st.error("Please enter a topic first!")
    else:
        with st.spinner("Thinking of the next unicorn..."):
            idea = generate_startup_idea(user_topic)
            pitch = generate_pitch(user_topic)
            names = suggest_names(user_topic)

        st.success("Here’s your personalized startup kit!")
        st.markdown("### 🧠 Startup Idea")
        st.write(idea)

        st.markdown("### 🎤 Elevator Pitch")
        st.info(pitch)

        st.markdown("### 🏷️ Name Suggestions")
        st.write(names)

        # Save to CSV
        def save_to_csv(topic, idea, pitch, names):
            with open("startup_ideas.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([datetime.now(), topic, idea, pitch, names])

        save_to_csv(user_topic, idea, pitch, names)

# Google Trends (Optional)
if st.button("📊 Show Related Trending Topics", key="trends_btn"):
    if user_topic.strip() == "":
        st.error("Please enter a topic first!")
    else:
        with st.spinner("Fetching trend data..."):
            trends = get_related_trends(user_topic)

        if trends is not None:
            st.markdown("### 📈 Related Google Trends")
            st.table(trends)
        else:
            st.warning("No trends found or topic not tracked on Google Trends.")

# Downloadable CSV (Optional)
try:
    with open("startup_ideas.csv", "r") as file:
        st.download_button("📥 Download Your Ideas (CSV)", file, "startup_ideas.csv", "text/csv")
except FileNotFoundError:
    pass

# Footer
st.markdown("---")
st.caption("Built with ❤️ by [You]")