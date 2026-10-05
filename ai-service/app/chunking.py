import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, Field

from app.policy_schemas import PolicyDocument


class PolicyChunk(BaseModel):
    chunk_id: str = Field(min_length=1)
    policy_id: str
    policy_title: str
    document_version: str
    dataset_version: str
    service_category: str

    section_id: str
    section_heading: str

    keywords: list[str]
    content: str
    embedding_text: str

    source_filename: str
    source_sha256: str


def calculate_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_embedding_text(
    policy: PolicyDocument,
    section_heading: str,
    section_text: str,
) -> str:
    keywords = ", ".join(policy.keywords)

    return "\n".join(
        [
            f"Policy title: {policy.title}",
            f"Service category: {policy.service_category}",
            f"Keywords: {keywords}",
            f"Section: {section_heading}",
            "",
            section_text,
        ]
    )


def chunk_policy_file(policy_path: Path) -> list[PolicyChunk]:
    policy_data = json.loads(
        policy_path.read_text(encoding="utf-8")
    )
    policy = PolicyDocument.model_validate(policy_data)

    source_hash = calculate_sha256(policy_path)
    chunks = []

    for section in policy.sections:
        chunk_id = (
            f"{policy.policy_id}::"
            f"{section.section_id}::"
            f"v{policy.document_version}"
        )

        chunks.append(
            PolicyChunk(
                chunk_id=chunk_id,
                policy_id=policy.policy_id,
                policy_title=policy.title,
                document_version=policy.document_version,
                dataset_version=policy.dataset_version,
                service_category=policy.service_category,
                section_id=section.section_id,
                section_heading=section.heading,
                keywords=policy.keywords,
                content=section.text,
                embedding_text=build_embedding_text(
                    policy=policy,
                    section_heading=section.heading,
                    section_text=section.text,
                ),
                source_filename=policy_path.name,
                source_sha256=source_hash,
            )
        )

    return chunks


def load_policy_chunks(
    dataset_directory: Path,
) -> list[PolicyChunk]:
    chunks = []

    for policy_path in sorted(
        dataset_directory.glob("POL-*.json")
    ):
        chunks.extend(chunk_policy_file(policy_path))

    chunk_ids = [chunk.chunk_id for chunk in chunks]

    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("Duplicate policy chunk IDs detected.")

    return chunks