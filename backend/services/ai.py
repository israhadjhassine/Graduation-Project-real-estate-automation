import os
import requests
import google.generativeai as genai
from typing import List

# Configure the Gemini API for the assistant part
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def get_embedding(text: str) -> List[float]:
    """
    Generates embedding using Ollama nomic-embed-text (Ollama service).
    1:1 matching backend/utils/embeddings.py
    """
    ollama_host = os.environ.get("OLLAMA_HOST", "host.docker.internal")
    try:
        response = requests.post(
            f"http://{ollama_host}:11434/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return None

def get_query_embedding(query: str) -> List[float]:
    """Specifically for search queries."""
    return get_embedding(query)


