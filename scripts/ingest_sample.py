"""Generate sample Korean heat-exchanger patent data via OpenAI and ingest into ChromaDB.

Use this when KIPRIS API key is unavailable or expired.

Usage:
    python scripts/ingest_sample.py
    python scripts/ingest_sample.py --topic "배터리 냉각" --count 20
"""

import argparse
import asyncio
import json
import logging

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GENERATE_PROMPT = """\
You are a Korean patent data generator for testing purposes.
Generate {count} realistic Korean patent entries about "{topic}".

Each entry must have:
- title: Korean patent title (발명의 명칭), 10-30 characters
- abstract: Korean abstract (요약), 100-300 characters, technically detailed
- application_number: fake but realistic format like "10-2024-0012345"

Return a JSON array of objects with keys: title, abstract, application_number.
Return ONLY the JSON array, no other text."""


async def generate_sample_patents(topic: str, count: int, api_key: str) -> list[dict]:
    """Generate synthetic patent data using OpenAI."""
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.8)
    response = await llm.ainvoke(GENERATE_PROMPT.format(topic=topic, count=count))
    text = response.content.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text)


async def ingest_sample(topic: str = "열교환기", count: int = 30):
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is required for sample data generation.")
        return 0

    embeddings = OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )

    logger.info(f"Generating {count} sample patents about '{topic}' via OpenAI...")
    patents = await generate_sample_patents(topic, count, settings.OPENAI_API_KEY)
    logger.info(f"Generated {len(patents)} patents")

    documents = [
        Document(
            page_content=f"{p['title']}\n\n{p['abstract']}",
            metadata={
                "title": p["title"],
                "application_number": p["application_number"],
                "source": "sample",
            },
        )
        for p in patents
        if p.get("title") and p.get("abstract")
    ]

    logger.info(f"Embedding and storing {len(documents)} patents into ChromaDB...")
    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR,
        collection_name="patents",
    )

    logger.info(f"Successfully ingested {len(documents)} sample patents.")
    return len(documents)


def main():
    parser = argparse.ArgumentParser(description="Ingest sample patents into ChromaDB via OpenAI")
    parser.add_argument("--topic", default="열교환기", help="Patent topic (default: 열교환기)")
    parser.add_argument("--count", type=int, default=30, help="Number of patents to generate")
    args = parser.parse_args()
    asyncio.run(ingest_sample(args.topic, args.count))


if __name__ == "__main__":
    main()
