import os
import google.generativeai as genai
from pytrends.request import TrendReq
import pandas as pd

# Configure the Gemini API key. It's best practice to set this as an environment variable.
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a Gemini model for text generation tasks
model = genai.GenerativeModel('gemini-1.5-pro')

# 🎯 Function to generate a startup idea
def generate_startup_idea(topic):
    """
    Generates a unique startup idea for a given topic using the Gemini API.
    """
    prompt = f"Suggest a unique and innovative startup idea in the field of {topic}. Give a short explanation in 3-4 sentences."
    response = model.generate_content(prompt)
    return response.text

# 🎤 Function to generate a pitch
def generate_pitch(topic):
    """
    Creates a 3-4 sentence elevator pitch using the Gemini API.
    """
    prompt = f"Create a 3-4 sentence elevator pitch for a startup in the {topic} domain. Clearly describe the problem, your solution, and key benefit."
    response = model.generate_content(prompt)
    return response.text

# 🧠 Function to suggest startup names
def suggest_names(topic):
    """
    Suggests 5 creative, brandable, and relevant startup names using the Gemini API.
    """
    prompt = f"Suggest 5 creative, brandable, and relevant startup name ideas for a business in the {topic} field. Respond only with a list of names."
    response = model.generate_content(prompt)
    return response.text

# 📊 Function to fetch trending topics using Google Trends
def get_related_trends(topic):
    """
    Fetches related trending topics from Google Trends using the pytrends library.
    """
    pytrends = TrendReq()
    try:
        pytrends.build_payload([topic], timeframe='today 12-m')
        related_queries = pytrends.related_queries()
        top_related = related_queries.get(topic, {}).get("top")
        if top_related is not None:
            return top_related.head(5)  # Return top 5 trends
        else:
            return None
    except Exception as e:
        # It's better to log the error for debugging purposes
        print(f"Error fetching Google Trends data: {e}")
        return None

# The code below is for demonstration purposes to show the functions work.
# This part would be used by your Streamlit app.
if __name__ == "__main__":
    test_topic = "sustainable fashion"
    print(f"Generating ideas for: {test_topic}")
    
    idea = generate_startup_idea(test_topic)
    print("\n--- Startup Idea ---")
    print(idea)

    pitch = generate_pitch(test_topic)
    print("\n--- Elevator Pitch ---")
    print(pitch)

    names = suggest_names(test_topic)
    print("\n--- Name Suggestions ---")
    print(names)

    trends = get_related_trends(test_topic)
    print("\n--- Related Google Trends ---")
    if trends is not None:
        print(trends)
    else:
        print("No trends found.")
