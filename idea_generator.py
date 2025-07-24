import openai
import os
from pytrends.request import TrendReq

openai.api_key = os.getenv("OPENAI_API_KEY")

# 🎯 Function to generate a startup idea
def generate_startup_idea(topic):
    prompt = f"Suggest a unique and innovative startup idea in the field of {topic}. Give a short explanation in 3-4 sentences."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a startup expert and innovation mentor."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# 🎤 Function to generate a pitch
def generate_pitch(topic):
    prompt = f"Create a 3-4 sentence elevator pitch for a startup in the {topic} domain. Clearly describe the problem, your solution, and key benefit."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# 🧠 Function to suggest startup names
def suggest_names(topic):
    prompt = f"Suggest 5 creative, brandable, and relevant startup name ideas for a business in the {topic} field."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# 📊 Function to fetch trending topics using Google Trends
def get_related_trends(topic):
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
        print("Trend Error:", e)
        return None