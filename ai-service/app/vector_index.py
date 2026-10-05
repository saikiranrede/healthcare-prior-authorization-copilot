import json
from pathlib import Path

import numpy as np
from openai import OpenAI

from app.chunking import PolicyChunk


class PolicySearchResult:
    def __init__(
        self,
        chunk: PolicyChunk,
        similarity_score: float,
        rank: int,
    ):
        self.chunk = chunk
        self.similarity_score = similarity_score
        self.rank = rank


class PolicyVectorIndex:
    def __init__(
        self,
        index_directory: Path,
        client: OpenAI | None = None,
    ):
        self.index_directory = index_directory
        self.client = client or OpenAI()

        manifest_path = (
            index_directory / "index_manifest.json"
        )
        chunks_path = index_directory / "chunks.jsonl"
        embeddings_path = (
            index_directory / "embeddings.npy"
        )

        self.manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        self.chunks = [
            PolicyChunk.model_validate_json(line)
            for line in chunks_path.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]

        self.vectors = np.load(embeddings_path)

        if len(self.chunks) != self.vectors.shape[0]:
            raise ValueError(
                "Chunk count does not match vector count."
            )

        expected_dimensions = self.manifest[
            "embedding_dimensions"
        ]

        if self.vectors.shape[1] != expected_dimensions:
            raise ValueError(
                "Vector dimensions do not match manifest."
            )

    @staticmethod
    def normalize_vector(
        vector: np.ndarray,
    ) -> np.ndarray:
        norm = np.linalg.norm(vector)

        if norm == 0:
            raise ValueError(
                "Cannot normalize a zero-length vector."
            )

        return vector / norm

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[PolicySearchResult]:
        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError(
                "Search query cannot be blank."
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be at least 1."
            )

        response = self.client.embeddings.create(
            model=self.manifest["embedding_model"],
            input=normalized_query,
            encoding_format="float",
        )

        query_vector = np.asarray(
            response.data[0].embedding,
            dtype=np.float32,
        )

        query_vector = self.normalize_vector(
            query_vector
        )

        # Stored vectors and the query are normalized.
        # Their dot product is cosine similarity.
        scores = self.vectors @ query_vector

        result_count = min(
            top_k,
            len(self.chunks),
        )

        ranked_indexes = np.argsort(
            scores
        )[::-1][:result_count]

        return [
            PolicySearchResult(
                chunk=self.chunks[index],
                similarity_score=float(scores[index]),
                rank=rank,
            )
            for rank, index in enumerate(
                ranked_indexes,
                start=1,
            )
        ]