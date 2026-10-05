import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from app.vector_index import PolicyVectorIndex


# load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / "ai-service" / ".env")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search the synthetic policy index."
    )
    parser.add_argument(
        "--query",
        required=True,
        help="Natural-language policy search query.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return.",
    )

    arguments = parser.parse_args()

    dataset_version = os.getenv(
        "POLICY_DATASET_VERSION",
        "1.0.0",
    )

    index = PolicyVectorIndex(
        Path(
            f"data/vector_indexes/"
            f"v{dataset_version}"
        )
    )

    results = index.search(
        query=arguments.query,
        top_k=arguments.top_k,
    )

    print(f"\nQuery: {arguments.query}\n")

    for result in results:
        chunk = result.chunk

        print(
            f"{result.rank}. "
            f"{chunk.policy_title} — "
            f"{chunk.section_heading}"
        )
        print(
            f"   Score: "
            f"{result.similarity_score:.4f}"
        )
        print(f"   Chunk: {chunk.chunk_id}")
        print(f"   Source: {chunk.source_filename}")
        print(
            f"   Content: "
            f"{chunk.content[:220]}"
        )
        print()


if __name__ == "__main__":
    main()