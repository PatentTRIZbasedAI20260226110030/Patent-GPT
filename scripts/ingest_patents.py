"""Fetch patents from KIPRISplus and ingest into ChromaDB."""
import argparse
import asyncio
import logging

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from app.config import get_settings
from app.utils.kipris_client import KIPRISClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest(keyword: str, max_patents: int = 100):
    settings = get_settings()
    client = KIPRISClient(settings)
    embeddings = OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )

    logger.info(f"Fetching patents for keyword: {keyword}")
    patents = await client.search_patents(keyword, num_of_rows=max_patents)
    await client.close()

    if not patents:
        logger.warning("No patents found. Check your KIPRIS_API_KEY and keyword.")
        return 0

    documents = [
        Document(
            page_content=f"{p['title']}\n\n{p['abstract']}",
            metadata={
                "title": p["title"],
                "application_number": p["application_number"],
                "source": "kipris",
            },
        )
        for p in patents
        if p["title"] and p["abstract"]
    ]

    logger.info(f"Embedding and storing {len(documents)} patents into ChromaDB...")
    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR,
        collection_name="patents",
    )

    logger.info(f"Successfully ingested {len(documents)} patents.")
    return len(documents)


def main():
    parser = argparse.ArgumentParser(description="Ingest patents from KIPRISplus into ChromaDB")
    parser.add_argument("keyword", help="Search keyword (e.g., '방열 구조')")
    parser.add_argument("--max", type=int, default=100, help="Max patents to fetch")
    args = parser.parse_args()
    asyncio.run(ingest(args.keyword, args.max))


if __name__ == "__main__":
    main()
