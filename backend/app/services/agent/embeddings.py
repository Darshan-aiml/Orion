from langchain_openai import OpenAIEmbeddings
from app.core.config import settings

def get_embedding(text: str) -> list[float]:
    """
    Generates an embedding vector for a given text using OpenAI.
    Fallback to a dummy vector if API key is not set.
    """
    if not settings.OPENAI_API_KEY:
        # Return a dummy vector of 1536 dimensions for local testing without an API key
        return [0.0] * 1536
        
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    return embeddings.embed_query(text)
