import json
from types import SimpleNamespace
from pathlib import Path

import numpy as np

from app.retrieval import PolicyRetrievalService
from app.retrieval_schemas import PolicyRetrievalRequest
from app.vector_index import PolicyVectorIndex


INDEX_DIRECTORY = Path(
    "data/vector_indexes/v1.0.0"
)


class FakeEmbeddings:
    def __init__(self, vector: list[float]):
        self.vector = vector

    def create(self, **kwargs):
        return SimpleNamespace(
            data=[
                SimpleNamespace(
                    index=0,
                    embedding=self.vector,
                )
            ],
            usage=SimpleNamespace(
                prompt_tokens=5,
            ),
        )


class FakeClient:
    def __init__(self, vector: list[float]):
        self.embeddings = FakeEmbeddings(vector)


def load_exact_chunk_vector(
    chunk_id: str,
) -> list[float]:
    chunks_path = INDEX_DIRECTORY / "chunks.jsonl"
    vectors_path = INDEX_DIRECTORY / "embeddings.npy"

    chunks = [
        json.loads(line)
        for line in chunks_path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    vectors = np.load(vectors_path)

    for index, chunk in enumerate(chunks):
        if chunk["chunk_id"] == chunk_id:
            return vectors[index].tolist()

    raise AssertionError(
        f"Chunk not found: {chunk_id}"
    )


def create_service_for_chunk(
    chunk_id: str,
) -> PolicyRetrievalService:
    vector = load_exact_chunk_vector(chunk_id)

    index = PolicyVectorIndex(
        index_directory=INDEX_DIRECTORY,
        client=FakeClient(vector),
    )

    return PolicyRetrievalService(index)


def test_exact_vector_returns_expected_chunk():
    expected_chunk_id = (
        "POL-LUMBAR-MRI-001::"
        "required-documentation::v1.0.0"
    )

    service = create_service_for_chunk(
        expected_chunk_id
    )

    response = service.retrieve(
        PolicyRetrievalRequest(
            query="lumbar documentation",
            top_k=1,
        )
    )

    assert response.returned_results == 1
    assert (
        response.results[0].citation.citation_id
        == expected_chunk_id
    )
    assert response.results[0].rank == 1


def test_citation_contains_source_metadata():
    expected_chunk_id = (
        "POL-CPAP-006::"
        "required-documentation::v1.0.0"
    )

    service = create_service_for_chunk(
        expected_chunk_id
    )

    response = service.retrieve(
        PolicyRetrievalRequest(
            query="CPAP documentation",
            top_k=1,
        )
    )

    citation = response.results[0].citation

    assert citation.policy_id == "POL-CPAP-006"
    assert citation.document_version == "1.0.0"
    assert citation.dataset_version == "1.0.0"
    assert citation.source_filename.endswith(".json")
    assert len(citation.source_sha256) == 64


def test_service_category_filter():
    expected_chunk_id = (
        "POL-CPAP-006::"
        "required-documentation::v1.0.0"
    )

    service = create_service_for_chunk(
        expected_chunk_id
    )

    response = service.retrieve(
        PolicyRetrievalRequest(
            query="equipment documentation",
            top_k=5,
            service_category=(
                "durable-medical-equipment"
            ),
        )
    )

    assert response.returned_results > 0

    assert all(
        result.citation.service_category
        == "durable-medical-equipment"
        for result in response.results
    )


def test_unknown_category_returns_no_results():
    expected_chunk_id = (
        "POL-CPAP-006::"
        "required-documentation::v1.0.0"
    )

    service = create_service_for_chunk(
        expected_chunk_id
    )

    response = service.retrieve(
        PolicyRetrievalRequest(
            query="equipment documentation",
            top_k=5,
            service_category="unknown-category",
        )
    )

    assert response.returned_results == 0
    assert response.results == []


def test_citable_context_contains_stable_id():
    expected_chunk_id = (
        "POL-LUMBAR-MRI-001::"
        "coverage-criteria::v1.0.0"
    )

    service = create_service_for_chunk(
        expected_chunk_id
    )

    response = service.retrieve(
        PolicyRetrievalRequest(
            query="lumbar criteria",
            top_k=1,
        )
    )

    context = service.format_citable_context(response)

    assert "<POLICY_SOURCE" in context
    assert expected_chunk_id in context
    assert "Lumbar Spine MRI" in context
    assert "</POLICY_SOURCE>" in context