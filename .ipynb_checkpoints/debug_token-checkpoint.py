import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# 1. Load Token
load_dotenv()
token = os.getenv("HF_API_TOKEN")

print(f"--- Token Diagnosis ---")
if not token:
    print("❌ Error: HF_API_TOKEN is missing from environment.")
    exit()

print(f"Token found? Yes")
print(f"Token length: {len(token)}")
print(f"Starts with 'hf_'? {token.startswith('hf_')}")

# 2. Test Connection
print("\n--- Testing Connection to Llama 3 ---")
client = InferenceClient(token=token)
try:
    # We pass the model directly in the call to avoid router pre-checks
    response = client.chat_completion(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[{"role": "user", "content": "Hello, are you working?"}],
        max_tokens=50
    )
    print("✅ Success! The API is working.")
    print("Response:", response.choices[0].message.content)
except Exception as e:
    print(f"❌ Connection Failed: {e}")