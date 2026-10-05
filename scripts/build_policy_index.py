import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

from app.chunking import load_policy_chunks


# load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / "ai-service" / ".env")

DATASET_VERSION = os.getenv(
    "POLICY_DATASET_VERSION",
    "1.0.0",
)
EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small",
)

DATASET_DIRECTORY = Path(
    f"data/policies/v{DATASET_VERSION}"
)
INDEX_DIRECTORY = Path(
    f"data/vector_indexes/v{DATASET_VERSION}"
)

CHUNKS_PATH = INDEX_DIRECTORY / "chunks.jsonl"
EMBEDDINGS_PATH = INDEX_DIRECTORY / "embeddings.npy"
INDEX_MANIFEST_PATH = (
    INDEX_DIRECTORY / "index_manifest.json"
)
POLICY_MANIFEST_PATH = DATASET_DIRECTORY / "manifest.json"


def calculate_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(
        vectors,
        axis=1,
        keepdims=True,
    )

    if np.any(norms == 0):
        raise ValueError("A zero-length embedding was returned.")

    return vectors / norms


def main() -> None:
    if not POLICY_MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"Policy manifest not found: {POLICY_MANIFEST_PATH}"
        )

    chunks = load_policy_chunks(DATASET_DIRECTORY)

    if not chunks:
        raise ValueError("No policy chunks were generated.")

    embedding_inputs = [
        chunk.embedding_text
        for chunk in chunks
    ]

    print(f"Dataset version: {DATASET_VERSION}")
    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Chunks to embed: {len(chunks)}")

    client = OpenAI()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=embedding_inputs,
        encoding_format="float",
    )

    ordered_embeddings = sorted(
        response.data,
        key=lambda item: item.index,
    )

    if len(ordered_embeddings) != len(chunks):
        raise ValueError(
            "Embedding count does not match chunk count."
        )

    vectors = np.asarray(
        [
            item.embedding
            for item in ordered_embeddings
        ],
        dtype=np.float32,
    )

    vectors = normalize_vectors(vectors)

    INDEX_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    np.save(EMBEDDINGS_PATH, vectors)

    with CHUNKS_PATH.open(
        "w",
        encoding="utf-8",
    ) as output_file:
        for chunk in chunks:
            output_file.write(
                chunk.model_dump_json()
                + "\n"
            )

    token_usage = getattr(response, "token_usage", None)

    manifest = {
        "index_name": "synthetic-healthcare-policy-index",
        "index_version": DATASET_VERSION,
        "dataset_version": DATASET_VERSION,
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dimensions": int(vectors.shape[1]),
        "chunk_count": int(vectors.shape[0]),
        "vector_dtype": str(vectors.dtype),
        "vectors_normalized": True,
        "similarity_metric": "cosine",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_policy_manifest": str(
            POLICY_MANIFEST_PATH
        ),
        "source_policy_manifest_sha256": (
            calculate_sha256(POLICY_MANIFEST_PATH)
        ),
        "chunks_filename": CHUNKS_PATH.name,
        "chunks_sha256": calculate_sha256(CHUNKS_PATH),
        "embeddings_filename": EMBEDDINGS_PATH.name,
        "embeddings_sha256": calculate_sha256(
            EMBEDDINGS_PATH
        ),
        "embedding_usage": {
            "prompt_tokens": (
                token_usage.prompt_tokens
                if token_usage is not None
                else None
            ),
            "total_tokens": (
                token_usage.total_tokens
                if token_usage is not None
                else None
            ),
        },
    }

    INDEX_MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Vector index created")
    print(f"Vector shape: {vectors.shape}")
    print(f"Chunks: {CHUNKS_PATH}")
    print(f"Embeddings: {EMBEDDINGS_PATH}")
    print(f"Manifest: {INDEX_MANIFEST_PATH}")


if __name__ == "__main__":
    main()