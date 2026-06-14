import os
import requests
from typing import List

def get_embedding(text: str) -> List[float]:
    """
    Generates embedding using Ollama nomic-embed-text (Ollama service).
    1:1 matching backend/utils/embeddings.py
    """
    ollama_host = os.environ.get("OLLAMA_HOST", "host.docker.internal")
    base_url = f"http://{ollama_host}" if ":" in ollama_host else f"http://{ollama_host}:11434"
    try:
        response = requests.post(
            f"{base_url}/api/embeddings",
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

def build_property_search_text(prop) -> str:
    """
    Builds a structured search text representing all attributes of a property.
    Handles dict, Pydantic model, or SQLAlchemy model.
    """
    if isinstance(prop, dict):
        title = prop.get("title", "")
        p_type = prop.get("property_type") or prop.get("type", "")
        listing_type = prop.get("listing_type") or prop.get("listing", "")
        price = prop.get("price", 0)
        currency = prop.get("currency", "TND")
        city = prop.get("city", "")
        state = prop.get("state", "")
        country = prop.get("country", "")
        neighborhood = prop.get("neighborhood", "")
        address = prop.get("address", "")
        bedrooms = prop.get("bedrooms", 0)
        bathrooms = prop.get("bathrooms", 0)
        kitchens = prop.get("kitchens", 0)
        living_rooms = prop.get("living_rooms") or prop.get("livingrooms", 0)
        area = prop.get("area", 0)
        description = prop.get("description", "")
        
        # features list
        features = prop.get("features", [])
        features_str = ", ".join([f.name if hasattr(f, "name") else str(f) for f in features])
    else:
        # Pydantic or SQLAlchemy
        title = getattr(prop, "title", "")
        p_type = getattr(prop, "property_type", "")
        listing_type = getattr(prop, "listing_type", "")
        price = getattr(prop, "price", 0)
        currency = getattr(prop, "currency", "TND")
        city = getattr(prop, "city", "")
        state = getattr(prop, "state", "")
        country = getattr(prop, "country", "")
        neighborhood = getattr(prop, "neighborhood", "")
        address = getattr(prop, "address", "")
        bedrooms = getattr(prop, "bedrooms", 0)
        bathrooms = getattr(prop, "bathrooms", 0)
        kitchens = getattr(prop, "kitchens", 0)
        living_rooms = getattr(prop, "living_rooms", 0)
        area = getattr(prop, "area", 0)
        description = getattr(prop, "description", "")
        
        features = getattr(prop, "features", [])
        features_str = ", ".join([f.name if hasattr(f, "name") else str(f) for f in features])

    parts = [
        f"Title: {title}",
        f"Type: {p_type} for {listing_type}",
        f"Price: {price} {currency}",
        f"Location: {', '.join(filter(None, [neighborhood, city, state, country]))}",
        f"Address: {address}" if address else "",
        f"Structure: {bedrooms} bedrooms, {bathrooms} bathrooms, {kitchens} kitchens, {living_rooms} living rooms, {area} sqm",
        f"Features: {features_str}" if features_str else "",
        f"Description: {description}"
    ]
    return "\n".join([p for p in parts if p])

def generate_property_embedding(prop) -> List[float]:
    """Generates embedding for a property using its structured search text."""
    search_text = build_property_search_text(prop)
    return get_embedding(search_text)



