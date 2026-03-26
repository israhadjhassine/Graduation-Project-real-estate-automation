import requests

def get_embedding(text: str):
    try:
        response = requests.post(
            "http://host.docker.internal:11434/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def get_query_embedding(query: str):
    return get_embedding(query)
