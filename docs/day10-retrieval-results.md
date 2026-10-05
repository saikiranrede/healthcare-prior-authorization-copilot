# Day 10 — Policy Retrieval with Citations

## Objective

Expose the Day 9 policy vector index through a reusable retrieval
service and FastAPI endpoint.

## Endpoint

`POST /retrieve-policies`

## Retrieval Pipeline

1. Validate the natural-language query.
2. Generate the query embedding.
3. Normalize the query vector.
4. Calculate cosine similarity against stored vectors.
5. Apply optional category and minimum-score filters.
6. Rank matching policy chunks.
7. Return top-k evidence with source metadata.

## Citation Design

Each policy section is a citable block.

Example citation ID:

`POL-LUMBAR-MRI-001::required-documentation::v1.0.0`

Each result includes:

- Policy ID and title
- Document version
- Dataset version
- Section ID and heading
- Source filename
- Source SHA-256 checksum
- Machine-readable policy URI
- Similarity score

## Evidence Reviewed

Reviewed six supplied cURL outputs and the captured pytest run from October 5,
2026. No API calls or tests were rerun for this report. The three full retrieval
responses identify index and dataset version `1.0.0`, cosine similarity, and
embedding model `text-embedding-3-small`. The CPAP output was projected with `jq`
and contains only ranked results. Only the two invalid-request tests captured
HTTP status headers; successful response bodies do not independently verify
HTTP status codes.

## Retrieval Results

| Query | Expected policy | Top policy | Top section | Score | Assessment |
|---|---|---|---|---:|---|
| Lumbar MRI documentation | Lumbar Spine MRI | Lumbar Spine MRI | Required Documentation | 0.757183 | Pass at rank 1; rank 3 is a different policy |
| CPAP sleep study | Positive Airway Pressure Equipment | Positive Airway Pressure Equipment | Required Documentation | 0.675126 | Pass for captured top-three results |
| Home skilled nursing | Home Health Services | Not captured | — | — | Not verified on Day 10 |
| Biologic treatment history | Specialty Biologic Medication | Not captured | — | — | Not verified on Day 10 |
| Colonoscopy history | Colonoscopy Services | Not captured | — | — | Not verified on Day 10 |

Day 9 CLI results are not substituted for missing Day 10 endpoint tests.
Similarity scores are not confidence probabilities.

### Lumbar MRI documentation

Query: `What clinical documentation is needed for a lumbar spine MRI?`
Requested and returned results: 3. No category or minimum-score filter was used.

| Rank | Policy | Section | Score |
|---|---|---|---:|
| 1 | Lumbar Spine MRI | Required Documentation | 0.757183 |
| 2 | Lumbar Spine MRI | Coverage Criteria | 0.704190 |
| 3 | Cervical Spine MRI | Required Documentation | 0.681626 |

The first result directly supplies lumbar documentation evidence. The third is
an anatomically different policy with similar terminology. A downstream answer
must not merge cervical requirements into lumbar guidance merely because they
rank highly. Both policies share `advanced-diagnostic-imaging`, so that category
filter alone would not separate them. This example supports policy-specific
selection or relevance review before answer generation.

### CPAP documentation

Query: `sleep-study results and CPAP equipment order`; `top_k: 3`.

| Rank | Policy | Section | Score |
|---|---|---|---:|
| 1 | Positive Airway Pressure Equipment | Required Documentation | 0.675126 |
| 2 | Positive Airway Pressure Equipment | Coverage Criteria | 0.630491 |
| 3 | Positive Airway Pressure Equipment | Limitations and Exceptions | 0.607945 |

All three returned citations identify `POL-CPAP-006` and version `1.0.0`.
The first citation is `POL-CPAP-006::required-documentation::v1.0.0`.
The projected output does not include content, usage, or HTTP headers.

## Filters and Request Validation

| Scenario | Observed result | Assessment |
|---|---|---|
| Generic query with `durable-medical-equipment`, `top_k: 5` | Five CPAP chunks, all in the requested category | Category filter worked in this example |
| `unknown-category`, `top_k: 5` | `returned_results: 0`, `results: []` | Empty result handled without fabricated citations |
| Whitespace-only query | HTTP 422; `value_error` at `body.query`, minimum three-character message | Invalid query rejected |
| `top_k: 100` | HTTP 422; `less_than_equal` at `body.top_k`, maximum 10 | Upper bound enforced |

The filtered query was `What information is required before reviewing this service?`.
Its ranked sections were Decision Boundary (0.425887), Required Documentation
(0.423850), Purpose (0.416612), Coverage Criteria (0.358371), and Limitations and
Exceptions (0.338864). Category restriction worked, but a generic boundary section
ranked above the documentation section. Filter correctness does not establish
ideal section relevance.

The unknown-category query was `What documentation is needed?`. It returned an
empty retrieval response rather than a validation error. No minimum-score filter
was exercised in the supplied requests.

## Citations and Usage

The full nonempty responses include stable chunk IDs, policy URIs, policy titles,
section identifiers, document/dataset versions, categories, filenames, and source
SHA-256 values. For example:

```text
policy://POL-LUMBAR-MRI-001/versions/1.0.0/sections/required-documentation
```

These fields support traceability. Their presence does not prove source hashes
were recomputed during retrieval or that a policy URI has a working resolver.

| Request | Reported query embedding tokens |
|---|---:|
| Lumbar MRI documentation | 12 |
| Durable-medical-equipment filter | 9 |
| Unknown category | 5 |
| CPAP documentation | Not captured |

The unknown-category request still reported embedding usage, consistent with
embedding the query before category filtering. No request latency or cost was
captured. Minor spacing issues appear in the pasted content, such as
`requestedsettings`; the transcript alone does not establish their origin.

## Automated Tests

The supplied command was:

```bash
PYTHONPATH=ai-service ai-service/.venv/bin/pytest tests/test_retrieval.py -v
```

Captured result: **5 passed in 1.16s**, on Python 3.13.15 and pytest 9.1.1.

| Test | Verified behavior |
|---|---|
| `test_exact_vector_returns_expected_chunk` | An injected stored vector retrieves its expected chunk at rank 1 |
| `test_citation_contains_source_metadata` | Expected policy/version fields, JSON filename suffix, and 64-character source hash |
| `test_service_category_filter` | Returned results all match the requested category |
| `test_unknown_category_returns_no_results` | Unknown category yields an empty result list |
| `test_citable_context_contains_stable_id` | Formatted context includes source tags, stable ID, and policy title |

These tests use a fake embedding client with vectors loaded from the saved index.
They verify retrieval mechanics without live API calls; they do not establish
semantic relevance of real query embeddings or test the HTTP route. The metadata
test checks hash length, not checksum correctness. The context test checks tags
and identifiers, not adversarial escaping or injection resistance.

## Safety and Grounding Controls

- Empty queries are rejected.
- Top-k is limited to 10.
- Unknown metadata categories return no results.
- No source is fabricated when retrieval returns nothing.
- Citation IDs come directly from indexed chunks.
- Policy and dataset versions are preserved.
- Source checksums allow retrieved content to be verified.
- The context formatter escapes retrieved text; adversarial escaping was not exercised by the supplied test suite.
- Retrieval does not make an authorization decision.

## Remaining Verification

- Capture HTTP status codes for nonempty and empty retrieval responses.
- Run the home-health, biologic, and colonoscopy endpoint scenarios.
- Test minimum-score filtering, boundary values, and valid queries that yield no relevant evidence.
- Test missing/corrupt indexes and provider failures.
- Add adversarial context-escaping tests and verify source hashes against source files.
- Evaluate cross-policy contamination, including lumbar versus cervical MRI results.

## Current Limitations

- Retrieval does not yet generate a case analysis.
- No LLM uses the retrieved context today.
- Similarity thresholds have not been tuned.
- Retrieval accuracy has not been evaluated against a labeled dataset.
- Prompt-injection documents have not yet been added.

Day 11 will combine this retrieval service with the three enterprise
tools and structured case analysis.