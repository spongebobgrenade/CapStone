from idea_generator import _chat

# Example prompt/messages for testing
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Suggest a unique startup idea in healthtech."}
]

# Call the chat function
response = _chat(messages)

print("Hugging Face response:")
print(response)