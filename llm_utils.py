import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load HF API token from .env
load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Initialize the LLM (Meta-Llama-3-8B-Instruct)
LLM_REPO = "meta-llama/Meta-Llama-3-8B-Instruct"

# Initialize the InferenceClient
client = InferenceClient(model=LLM_REPO, token=HF_API_TOKEN)

def call_llm(prompt: str, max_tokens: int = 3500) -> str:
    """
    Call the LLM via Hugging Face Inference API using Chat Completion.
    """
    try:
        messages = [{"role": "user", "content": prompt}]
        response = client.chat_completion(
            messages=messages, 
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error calling LLM: {str(e)}"
