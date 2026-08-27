import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")


client = genai.Client(
    api_key=GEMINI_API_KEY
)


EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 1536


def generate_embedding(text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Cannot generate embedding for empty text")

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )

    if not response.embeddings:
        raise RuntimeError(
            "Gemini returned no embedding"
        )

    values = response.embeddings[0].values

    if len(values) != EMBEDDING_DIMENSIONS:
        raise RuntimeError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
            f"got {len(values)}"
        )

    return values
