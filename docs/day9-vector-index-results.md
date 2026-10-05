# Day 9 — Policy Vector Index Results

## Objective

Convert the versioned synthetic policy dataset into stable,
semantically searchable chunks.

## Index Configuration

- Source dataset version: 1.0.0
- Embedding model: text-embedding-3-small
- Similarity metric: cosine similarity
- Vector storage: NumPy
- Metadata storage: JSON Lines
- Expected policies: 10
- Expected chunks: 50
- Expected dimensions: 1536

## Chunking Strategy

Each policy section becomes one chunk.

The embedded text includes:

- Policy title
- Service category
- Search keywords
- Section heading
- Section content

Each chunk retains stable policy, version, section and source-file
metadata for future citation generation.

## Verified Index Results

The saved index manifest reports creation at `2026-10-05T18:33:35.081562+00:00`,
dataset/index version `1.0.0`, and embedding model `text-embedding-3-small`.

During this review, the local validator was run from the project root:

```bash
ai-service/.venv/bin/python scripts/validate_policy_index.py
```

```text
Index validation passed
Chunks: 50
Vector shape: (50, 1536)
Embedding model: text-embedding-3-small
```

This confirms the current files exist, chunk and vector counts match the manifest,
vector dimensions match, chunk and embedding checksums match, and vector norms
pass the validator's normalization check. This was a fresh local validation,
not recovered output from an earlier terminal session. No embedding or search
API calls were made during this review.

The validator does not check unique chunk IDs, individual source-policy hashes,
or the source-manifest hash; its success should not be interpreted as verification
of every integrity control listed below. The index manifest stores embedding
`prompt_tokens` and `total_tokens` as null, so build token usage is unavailable.

## Search Results

Reviewed the five supplied command-line search outputs, each run with `--top-k 5`.
No searches were rerun for this update. A pass below means the expected policy
appeared at rank 1; it does not mean every returned section answers the query.
Scores are the displayed cosine similarities, not confidence probabilities.

| Query | Expected policy | Top result section | Rank | Score | Pass |
|---|---|---|---:|---:|---|
| Lumbar MRI documentation | Lumbar Spine MRI | Required Documentation | 1 | 0.7673 | Yes |
| CPAP sleep study | Positive Airway Pressure Equipment | Required Documentation | 1 | 0.6625 | Yes |
| Skilled home nursing | Home Health Services | Limitations and Exceptions | 1 | 0.5803 | Yes — policy match |
| Previous biologic treatment | Specialty Biologic Medication | Required Documentation | 1 | 0.5757 | Yes |
| Prior colonoscopy findings | Colonoscopy Services | Required Documentation | 1 | 0.5715 | Yes |

### Exact queries and returned chunks

All chunk IDs below use dataset version `v1.0.0`. Each result's source file is
its policy ID followed by `.json`.

| Exact query | Policy ID | Ranked sections and scores (1–5) |
|---|---|---|
| What documentation is needed for a lumbar MRI for lower-back pain? | `POL-LUMBAR-MRI-001` | `required-documentation` 0.7673; `coverage-criteria` 0.6980; `decision-boundary` 0.6539; `purpose` 0.6517; `limitations` 0.6456 |
| sleep study and equipment order for CPAP | `POL-CPAP-006` | `required-documentation` 0.6625; `coverage-criteria` 0.6353; `limitations` 0.6264; `decision-boundary` 0.5866; `purpose` 0.5461 |
| patient needs skilled nursing at home and cannot easily leave home | `POL-HOME-HEALTH-007` | `limitations` 0.5803; `coverage-criteria` 0.5472; `decision-boundary` 0.5087; `required-documentation` 0.5020; `purpose` 0.4338 |
| previous medications and contraindications for a biologic drug | `POL-BIOLOGIC-009` | `required-documentation` 0.5757; `limitations` 0.5698; `coverage-criteria` 0.5545; `decision-boundary` 0.5306; `purpose` 0.5006 |
| previous colonoscopy findings and family risk history | `POL-COLONOSCOPY-010` | `required-documentation` 0.5715; `coverage-criteria` 0.5219; `limitations` 0.5156; `decision-boundary` 0.4647; `purpose` 0.4148 |

For example, the top lumbar result was
`POL-LUMBAR-MRI-001::required-documentation::v1.0.0`, sourced from
`POL-LUMBAR-MRI-001.json`. The policy ID, section ID, and version identify each
returned chunk using this same format.

### Retrieval observations

- The expected policy ranked first in all five examples: an observed policy hit rate at rank 1 of 5/5 for this small manual sample.
- All five results for each query belonged to the expected policy (25/25 returned chunks). This establishes policy association, not that every chunk is equally relevant.
- Required Documentation ranked first for lumbar MRI, CPAP, biologic medication, and colonoscopy. The displayed content matched the requested topics: symptom and treatment details, sleep-study and equipment-order details, prior medication response and contraindications, and prior colonoscopy findings and family history, respectively.
- Home Health Services ranked correctly at the policy level, but Limitations and Exceptions outranked Coverage Criteria (rank 2) and Required Documentation (rank 4). Those lower-ranked sections more directly address the need for skilled services, ability to leave home, and homebound assessment. This is a useful section-ranking case for future evaluation.
- Generic Purpose and Decision Boundary sections appeared in every top-five result set. They provide context but can occupy retrieval slots that might otherwise carry more query-specific evidence.
- CLI content previews are truncated in several results. The captured previews do not establish that full policy text was reviewed or that a downstream answer would include all relevant requirements.

The transcript does not report search latency or query embedding token usage.
These measurements cannot be derived from similarity scores. The examples cover
five of the ten expected policies and contain no unrelated or no-match queries;
they do not establish general retrieval accuracy or a suitable score threshold.

## Integrity Controls

- Stable deterministic chunk IDs
- Unique chunk validation
- Source-policy SHA-256 hashes
- Chunk-file SHA-256 hash
- Embedding-file SHA-256 hash
- Dataset-version provenance
- Embedding-model provenance
- Vector-dimension validation
- L2-normalized vectors

## Current Limitations

- The index uses exhaustive NumPy search.
- No metadata filtering is implemented yet.
- No minimum similarity threshold is enforced yet.
- No citations are returned to the application yet.
- Retrieval has been reviewed on five manual examples; no formal evaluation set or relevance labels for every chunk have been established.
- Chunking has not yet been tuned using failed cases.

These capabilities will be developed on later days.