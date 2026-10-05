import os
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

from app.retrieval_schemas import (
    PolicyCitation,
    PolicyRetrievalRequest,
    PolicyRetrievalResponse,
    PolicyRetrievalResult,
    RetrievalUsage,
)
from app.vector_index import PolicyVectorIndex


class PolicyRetrievalService:
    def __init__(
        self,
        vector_index: PolicyVectorIndex,
    ):
        self.vector_index = vector_index

    @staticmethod
    def create_citation_uri(
        policy_id: str,
        document_version: str,
        section_id: str,
    ) -> str:
        return (
            f"policy://{policy_id}"
            f"/versions/{document_version}"
            f"/sections/{section_id}"
        )

    def retrieve(
        self,
        request: PolicyRetrievalRequest,
    ) -> PolicyRetrievalResponse:
        search_response = self.vector_index.search(
            query=request.query,
            top_k=request.top_k,
            service_category=request.service_category,
            minimum_score=request.minimum_score,
        )

        retrieval_results = []

        for search_result in search_response.results:
            chunk = search_result.chunk

            citation = PolicyCitation(
                citation_id=chunk.chunk_id,
                citation_uri=self.create_citation_uri(
                    policy_id=chunk.policy_id,
                    document_version=chunk.document_version,
                    section_id=chunk.section_id,
                ),
                policy_id=chunk.policy_id,
                policy_title=chunk.policy_title,
                document_version=chunk.document_version,
                dataset_version=chunk.dataset_version,
                section_id=chunk.section_id,
                section_heading=chunk.section_heading,
                service_category=chunk.service_category,
                source_filename=chunk.source_filename,
                source_sha256=chunk.source_sha256,
            )

            retrieval_results.append(
                PolicyRetrievalResult(
                    rank=search_result.rank,
                    similarity_score=round(
                        search_result.similarity_score,
                        6,
                    ),
                    content=chunk.content,
                    citation=citation,
                )
            )

        manifest = self.vector_index.manifest

        return PolicyRetrievalResponse(
            query=request.query,
            requested_top_k=request.top_k,
            returned_results=len(retrieval_results),
            index_version=manifest["index_version"],
            dataset_version=manifest["dataset_version"],
            service_category_filter=(
                request.service_category
            ),
            minimum_score_filter=request.minimum_score,
            results=retrieval_results,
            usage=RetrievalUsage(
                embedding_model=manifest[
                    "embedding_model"
                ],
                query_tokens=(
                    search_response.query_tokens
                ),
            ),
        )

    @staticmethod
    def format_citable_context(
        response: PolicyRetrievalResponse,
    ) -> str:
        blocks = []

        for result in response.results:
            citation = result.citation

            block = "\n".join(
                [
                    (
                        "<POLICY_SOURCE "
                        f"id={quoteattr(citation.citation_id)}>"
                    ),
                    f"Policy ID: {escape(citation.policy_id)}",
                    f"Title: {escape(citation.policy_title)}",
                    (
                        "Document version: "
                        f"{escape(citation.document_version)}"
                    ),
                    (
                        "Dataset version: "
                        f"{escape(citation.dataset_version)}"
                    ),
                    (
                        "Section: "
                        f"{escape(citation.section_heading)}"
                    ),
                    (
                        "Source URI: "
                        f"{escape(citation.citation_uri)}"
                    ),
                    "Content:",
                    escape(result.content),
                    "</POLICY_SOURCE>",
                ]
            )

            blocks.append(block)

        return "\n\n".join(blocks)


@lru_cache
def get_policy_retrieval_service(
) -> PolicyRetrievalService:
    dataset_version = os.getenv(
        "POLICY_DATASET_VERSION",
        "1.0.0",
    )

    project_root = Path(__file__).resolve().parents[2]

    index_directory = (
        project_root
        / "data"
        / "vector_indexes"
        / f"v{dataset_version}"
    )

    # index_directory = Path(
    #     f"data/vector_indexes/v{dataset_version}"
    # )

    vector_index = PolicyVectorIndex(
        index_directory=index_directory
    )

    return PolicyRetrievalService(
        vector_index=vector_index
    )