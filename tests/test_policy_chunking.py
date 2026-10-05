from pathlib import Path

from app.chunking import load_policy_chunks


DATASET_DIRECTORY = Path("data/policies/v1.0.0")


def test_dataset_produces_fifty_chunks():
    chunks = load_policy_chunks(DATASET_DIRECTORY)

    assert len(chunks) == 50


def test_chunk_ids_are_unique():
    chunks = load_policy_chunks(DATASET_DIRECTORY)
    chunk_ids = [chunk.chunk_id for chunk in chunks]

    assert len(chunk_ids) == len(set(chunk_ids))


def test_chunk_ids_are_stable():
    first_run = load_policy_chunks(DATASET_DIRECTORY)
    second_run = load_policy_chunks(DATASET_DIRECTORY)

    assert [
        chunk.chunk_id for chunk in first_run
    ] == [
        chunk.chunk_id for chunk in second_run
    ]


def test_chunks_preserve_source_metadata():
    chunks = load_policy_chunks(DATASET_DIRECTORY)
    chunk = chunks[0]

    assert chunk.policy_id
    assert chunk.policy_title
    assert chunk.section_id
    assert chunk.section_heading
    assert chunk.source_filename.endswith(".json")
    assert len(chunk.source_sha256) == 64


def test_embedding_text_includes_context():
    chunks = load_policy_chunks(DATASET_DIRECTORY)
    chunk = chunks[0]

    assert chunk.policy_title in chunk.embedding_text
    assert chunk.section_heading in chunk.embedding_text
    assert chunk.content in chunk.embedding_text