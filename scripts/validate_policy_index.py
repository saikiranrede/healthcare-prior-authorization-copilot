import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np


DATASET_VERSION = os.getenv(
    "POLICY_DATASET_VERSION",
    "1.0.0",
)

INDEX_DIRECTORY = Path(
    f"data/vector_indexes/v{DATASET_VERSION}"
)

MANIFEST_PATH = (
    INDEX_DIRECTORY / "index_manifest.json"
)
CHUNKS_PATH = INDEX_DIRECTORY / "chunks.jsonl"
EMBEDDINGS_PATH = (
    INDEX_DIRECTORY / "embeddings.npy"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    errors = []

    for path in [
        MANIFEST_PATH,
        CHUNKS_PATH,
        EMBEDDINGS_PATH,
    ]:
        if not path.exists():
            errors.append(f"Missing file: {path}")

    if errors:
        for error in errors:
            print(f"- {error}")

        sys.exit(1)

    manifest = json.loads(
        MANIFEST_PATH.read_text(encoding="utf-8")
    )
    vectors = np.load(EMBEDDINGS_PATH)

    chunk_lines = [
        line
        for line in CHUNKS_PATH.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    if len(chunk_lines) != manifest["chunk_count"]:
        errors.append(
            "Chunk count does not match manifest."
        )

    if vectors.shape[0] != manifest["chunk_count"]:
        errors.append(
            "Vector count does not match manifest."
        )

    if vectors.shape[1] != manifest[
        "embedding_dimensions"
    ]:
        errors.append(
            "Vector dimensions do not match manifest."
        )

    if sha256(CHUNKS_PATH) != manifest[
        "chunks_sha256"
    ]:
        errors.append(
            "Chunk metadata checksum mismatch."
        )

    if sha256(EMBEDDINGS_PATH) != manifest[
        "embeddings_sha256"
    ]:
        errors.append(
            "Embedding checksum mismatch."
        )

    norms = np.linalg.norm(vectors, axis=1)

    if not np.allclose(
        norms,
        1.0,
        atol=1e-5,
    ):
        errors.append(
            "Stored vectors are not normalized."
        )

    if errors:
        print("Index validation failed:")

        for error in errors:
            print(f"- {error}")

        sys.exit(1)

    print("Index validation passed")
    print(f"Chunks: {len(chunk_lines)}")
    print(f"Vector shape: {vectors.shape}")
    print(
        f"Embedding model: "
        f'{manifest["embedding_model"]}'
    )


if __name__ == "__main__":
    main()