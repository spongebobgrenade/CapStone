from huggingface_hub import InferenceClient

print("✅ Starting Hugging Face test...")

# Initialize client
client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.3")

# Send a simple query
try:
    response = client.chat_completion(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[
            {"role": "user", "content": "Give me 3 startup ideas in the food delivery sector."}
        ],
        max_tokens=200
    )
    print("✅ Response from Hugging Face:")
    print(response.choices[0].message["content"])

except Exception as e:
    print("❌ Error occurred:", e)
