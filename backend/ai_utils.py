import os
import google.generativeai as genai
from typing import List

# Configure the Gemini API
# Note: GEMINI_API_KEY should be set in environment variables
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def get_embedding(text: str) -> List[float]:
    """
    Generates a 768-dimensional embedding vector for the given text 
    using Google's text-embedding-004 model.
    """
    if not text:
        return []
    
    try:
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type="retrieval_document",
            title="Real Estate Property Description"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return empty or handle gracefully
        return []

def get_query_embedding(query: str) -> List[float]:
    """
    Specifically for search queries, using retrieval_query task type.
    """
    try:
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=query,
            task_type="retrieval_query"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        return []

def ask_property_assistant(question: str, property_context: str) -> str:
    """
    Uses Gemini Pro to answer a question based ONLY on the provided property context (RAG).
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
