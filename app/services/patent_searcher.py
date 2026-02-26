import logging

from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from sentence_transformers import CrossEncoder

from app.config import Settings
from app.models.patent_draft import SimilarPatent

logger = logging.getLogger(__name__)


def merge_and_score_results(
    docs: list[Document], scores: list[float]
) -> list[SimilarPatent]:
    if not docs:
        return []
    results = []
    for doc, score in zip(docs, scores):
        results.append(
            SimilarPatent(
                title=doc.metadata.get("title", ""),
                abstract=doc.page_content,
                application_number=doc.metadata.get("application_number", ""),
                similarity_score=round(score, 4),
            )
        )
    return results


class PatentSearcher:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def _get_vectorstore(self) -> Chroma:
        return Chroma(
            persist_directory=self.settings.CHROMA_PERSIST_DIR,
            embedding_function=self.embeddings,
            collection_name="patents",
        )

    async def search(self, query: str, top_k: int | None = None) -> list[SimilarPatent]:
        top_k = top_k or self.settings.RERANK_TOP_K
        retrieval_k = self.settings.RETRIEVAL_TOP_K

        vectorstore = self._get_vectorstore()
        collection = vectorstore._collection
        if collection.count() == 0:
            logger.warning("ChromaDB is empty. Run the ingestion script first.")
            return []

        # Dense retriever (vector search)
        dense_retriever = vectorstore.as_retriever(
            search_kwargs={"k": retrieval_k}
        )

        # Sparse retriever (BM25)
        all_docs = vectorstore.get()
        if not all_docs["documents"]:
            return []

        bm25_docs = [
            Document(
                page_content=doc,
                metadata=meta,
            )
            for doc, meta in zip(all_docs["documents"], all_docs["metadatas"])
        ]
        sparse_retriever = BM25Retriever.from_documents(bm25_docs, k=retrieval_k)

        # Ensemble (hybrid) retriever
        ensemble = EnsembleRetriever(
            retrievers=[dense_retriever, sparse_retriever],
            weights=[0.5, 0.5],
        )

        # Retrieve candidates
        candidates = await ensemble.ainvoke(query)

        if not candidates:
            return []

        # Deduplicate by content
        seen = set()
        unique_candidates = []
        for doc in candidates:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_candidates.append(doc)

        # Cross-Encoder reranking
        pairs = [[query, doc.page_content] for doc in unique_candidates]
        scores = self.reranker.predict(pairs).tolist()

        # Sort by score descending, take top_k
        scored = sorted(zip(unique_candidates, scores), key=lambda x: x[1], reverse=True)
        top_docs = [doc for doc, _ in scored[:top_k]]
        top_scores = [score for _, score in scored[:top_k]]

        # Normalize scores to 0-1 range
        max_score = max(top_scores) if top_scores else 1.0
        min_score = min(top_scores) if top_scores else 0.0
        score_range = max_score - min_score if max_score != min_score else 1.0
        normalized_scores = [(s - min_score) / score_range for s in top_scores]

        return merge_and_score_results(top_docs, normalized_scores)
