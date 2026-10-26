import json
import uuid
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from db import qdrant_client
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue

load_dotenv()

client = OpenAI()

def save_memory(user_id: int, memory_type: str, content: str, metadata: dict) -> str:
    """
    Saves a memory point to the 'memories' Qdrant collection for a specific user.
    """
    if not user_id:
        return "Error saving memory: 'user_id' is required."

    try:
        # Create text embedding representation using memory_type, title, category, and description
        title = metadata.get("title", "") if metadata else ""
        category = metadata.get("category", "") if metadata else ""
        description = metadata.get("description", "") if metadata else ""
        text_to_embed = f"Type: {memory_type}\nTitle: {title}\nCategory: {category}\nDescription: {description}"
        
        response = client.embeddings.create(
            input=text_to_embed,
            model="text-embedding-3-small"
        )
        vector = response.data[0].embedding
        
        point_id = str(uuid.uuid4())
        qdrant_client.upsert(
            collection_name="memories",
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "user_id": user_id,
                        "memory_type": memory_type,
                        "content": content,
                        "metadata": metadata or {}
                    }
                )
            ]
        )
        return f"Successfully saved memory of type '{memory_type}'."
    except Exception as e:
        return f"Error saving memory: {str(e)}"


def search_memory(user_id: int, query: str, memory_type: Optional[str] = None) -> str:
    """
    Searches the 'memories' collection using vector similarity for a specific user.
    """
    if not user_id:
        return "Error searching memory: 'user_id' is required."

    try:
        response = client.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        query_vector = response.data[0].embedding
        
        # Build filter enforcing user isolation and optional memory_type
        must_conditions = [
            FieldCondition(
                key="user_id",
                match=MatchValue(value=user_id)
            )
        ]
        if memory_type:
            must_conditions.append(
                FieldCondition(
                    key="memory_type",
                    match=MatchValue(value=memory_type)
                )
            )
        query_filter = Filter(must=must_conditions)
            
        try:
            search_results = qdrant_client.query_points(
                collection_name="memories",
                query=query_vector,
                query_filter=query_filter,
                limit=5
            )
            points = search_results.points
        except Exception as filter_err:
            # Fallback to post-filtering if index filter fails
            print(f"Filter query failed: {filter_err}. Retrying with post-filtering...")
            search_results = qdrant_client.query_points(
                collection_name="memories",
                query=query_vector,
                limit=20
            )
            points = [p for p in search_results.points if p.payload.get("user_id") == user_id]
            if memory_type:
                points = [p for p in points if p.payload.get("memory_type") == memory_type]
            points = points[:5]
        
        matches = []
        for point in points:
            matches.append({
                "score": point.score,
                "memory_type": point.payload.get("memory_type"),
                "content": point.payload.get("content"),
                "metadata": point.payload.get("metadata", {})
            })
            
        return json.dumps(matches)
    except Exception as e:
        return f"Error searching memory: {str(e)}"
