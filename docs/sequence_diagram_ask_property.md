# Sequence Diagram — "Ask About Property" Functionality

This document details the sequence of interactions between the Client (User), Telegram, n8n Workflow Automation, the Langchain Smart Agent, the FastAPI Backend, Ollama (Vector Embedding Service), and PostgreSQL (pgvector Database) during a semantic property inquiry.

## 📌 Workflow Overview

1. **Inquiry Trigger**: The client interacts with the Telegram bot.
2. **Intent Parsing & Tool Calling**: The n8n Langchain Agent processes the query and decides to call the `search_properties` HTTP tool.
3. **Retrieval-Augmented Generation (RAG) Context Generation**:
   * The Backend requests a vector representation of the query from Ollama.
   * The Backend searches PostgreSQL using pgvector cosine/L2-distance similarity.
   * Relevant property details are assembled into a context payload.
4. **Response Generation**: The Smart Agent uses Gemini LLM to synthesize a natural language response based on the retrieved context.
5. **Dispatch**: The response is sent back to the client via Telegram.

---

```mermaid
sequenceDiagram
    autonumber
    actor Client as Client (User)
    participant Telegram as Telegram Bot API
    box n8n Workflow Platform
        participant Workflow as n8n Workflow Trigger
        participant Agent as Smart Agent (Langchain)
        participant Tool as search_properties (HTTP Tool)
        participant Memory as Postgres Memory
    end
    box Backend Services
        participant Backend as FastAPI Backend
        participant Ollama as Ollama Service
        participant DB as PostgreSQL (pgvector)
    end

    Client->>Telegram: Sends query ("Looking for a rental villa in Tunis with pool < 3000 TND")
    Telegram->>Workflow: Forwards webhook request (Message Details)
    Workflow->>Agent: Activates agent pipeline with user message
    
    critical Initialize Session Memory
        Agent->>Memory: Retrieve previous chat history
        Memory-->>Agent: Return active chat context
    end

    Note over Agent: Parses intent and determines<br/>it needs property data.<br/>Decides to call search_properties.

    Agent->>Tool: Executes search_properties(query)
    
    Tool->>Backend: HTTP POST /search/rag<br/>{"query": "villas for rent in Tunis with pool < 3000 TND"}
    
    activate Backend
    Backend->>Ollama: HTTP POST /api/embeddings<br/>{"model": "nomic-embed-text", "prompt": "..."}
    activate Ollama
    Ollama-->>Backend: Returns 768-dimension query embedding vector
    deactivate Ollama

    Backend->>DB: Query properties ranked by L2 similarity<br/>ORDER BY description_vector <=> query_embedding<br/>WHERE status = 'available'
    activate DB
    DB-->>Backend: Returns top matching Property records with Features
    deactivate DB

    Note over Backend: Assembles matching properties into<br/>RAG Context text block and JSON metadata.

    Backend-->>Tool: Returns JSON {"context": "...", "properties": [...]}
    deactivate Backend

    Tool-->>Agent: Returns search result payload
    
    Note over Agent: Combines retrieved RAG context<br/>with original query and session history.

    Agent->>Agent: Invokes Gemini Model (gemini-2.0-flash)<br/>to synthesize natural response
    Agent->>Memory: Save current query & response to session log
    Agent-->>Workflow: Returns final reply text
    
    Workflow->>Telegram: HTTP POST /sendMessage (Response message)
    Telegram-->>Client: Displays response ("I found 2 villas for you: Villa A...")
```

## 🛠️ Key Execution Steps

* **Vector Embedding Injection**: The FastAPI Backend transforms the natural language text into a machine-readable vector via Ollama's `nomic-embed-text` model.
* **Semantic Retrieval**: Rather than standard keyword searching, PostgreSQL employs vector distance calculation (`l2_distance` or `<=>`) directly on the `description_vector` column to identify properties matching the conceptual query.
* **Contextual Grounding**: By injecting the matching property facts into the Gemini prompt context, the Smart Agent generates factual, hallucination-free property information with direct contact options.
