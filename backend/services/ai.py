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
        print(f"❌ Error generating embedding for text '{text[:50]}...': {e}")
        return None

def get_query_embedding(query: str) -> List[float]:
    """Specifically for search queries."""
    return get_embedding(query)

def ask_property_assistant(question: str, property_context: str) -> str:
    """
    Uses Gemini Pro to answer a question based ONLY on the provided property context (RAG).
    1:1 matching original backend/ai_utils.py
    """
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    You are a professional real estate assistant.
    Use the following property details to answer the visitor's question.
    If the answer is not in the details, politely say you don't know and advise them to contact the agent.
    
    Property Details:
    {property_context}
    
    Visitor Question: {question}
    
    Answer:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in RAG generation: {e}")
        return "I'm sorry, I encountered an error while processing your request. Please try again later."
