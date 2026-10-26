import os
import sys

from qdrant_client.models import (
    VectorParams,
    Distance,
    PayloadSchemaType,
)

# Allow imports from the project root
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from db.qdrant_client import qdrant_client


COLLECTION_NAME = "memories"
VECTOR_SIZE = 1536


def setup_qdrant():
    # Create the collection only if it doesn't exist
    if not qdrant_client.collection_exists(
        collection_name=COLLECTION_NAME
    ):
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print("Created Qdrant memories collection.")
    else:
        print("Qdrant memories collection already exists.")

    # Index user_id to support user-specific memory filtering
    qdrant_client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="user_id",
        field_schema=PayloadSchemaType.INTEGER,
    )

    # Index memory_type to support filtering by memory category
    qdrant_client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="memory_type",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    print("Qdrant setup completed successfully.")


if __name__ == "__main__":
    setup_qdrant()