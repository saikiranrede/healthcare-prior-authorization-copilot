# Day 11 — Enterprise Tools and RAG

## Objective

Combine deterministic enterprise tool calling, semantic policy
retrieval and schema-validated grounded analysis in one request.

## End-to-End Workflow

1. Validate the case request.
2. Request the three enterprise tools.
3. Validate and execute each tool.
4. Verify workflow completeness.
5. Construct the policy retrieval query.
6. Retrieve top-k policy sections.
7. Format the sections as citable evidence blocks.
8. Generate structured analysis.
9. Validate authorization safety rules.
10. Validate every policy citation.
11. Return enterprise data, evidence and analysis.

## Data Sources

| Data | Authoritative source |
|---|---|
| Eligibility | Eligibility tool |
| Claims | Claims-history tool |
| Provider status | Provider-information tool |
| Policy requirements | Retrieved policy chunks |
| Authorization decision | Authorized human reviewer |


## Test Results

| Case | Tools executed | Retrieved policy | Citation review | Decision | Assessment |
|---|---:|---|---|---|---|
| Lumbar MRI — PA-1101 | 3 succeeded | Five Lumbar Spine MRI sections | All six citation references across four findings match retrieved IDs (five unique IDs) | `not_determined` | Pass for the captured workflow |
| CPAP equipment — PA-1102 | 3 succeeded | Five Positive Airway Pressure Equipment sections | All four citation references across four findings match retrieved IDs | `not_determined` | Pass for the captured workflow |

Both cases returned `policy_basis_status: policy_evidence_found`,
`evidence_sufficiency: insufficient`,
`case_preparation_sufficiency: insufficient_to_continue`,
`recommended_next_action: request_additional_information`, and
`human_review_required: true`.

## Behavioral Review

### Enterprise data

Each full response reports successful execution of `check_member_eligibility`,
`get_claim_history`, and `get_provider_information`. Both cases used member
M-1001 and provider P-2001: active ClearHealth Gold eligibility, two paid claims
(primary care and physical therapy), and an active in-network provider,
Northwest Orthopedic Clinic, with specialty Orthopedic Surgery.

The analyses did not equate active eligibility or network participation with
medical necessity, or a paid claim with treatment completion or response. The
CPAP analysis retained the provider's actual specialty without asserting that
network status establishes suitability for the requested equipment.

### Lumbar MRI

The analysis identified missing symptom course, neurologic examination,
conservative-treatment response, prior imaging/procedures, and red-flag status.
Its policy findings cited the retrieved criteria, documentation, limitations,
purpose, and decision-boundary sections. The cited text supports the reported
policy documentation topics and the distinction between a paid physical-therapy
claim and evidence of clinical response.

Warnings explicitly discouraged inference of treatment completion or medical
necessity and preserved uncertainty about red flags. No cervical policy appeared
in this captured retrieval set. This differs from the Day 10 standalone query,
but the query text also changed, so it does not establish a general fix for
cross-policy retrieval.

### CPAP equipment

The analysis requested sleep-study details, provider diagnosis documentation,
an equipment order/settings, and other documentation described in the retrieved
CPAP policy. It distinguished the submitted statement of sleep apnea from
supporting diagnostic documentation. Four findings cite documentation, criteria,
decision-boundary, and limitations sections.

The response kept continued-coverage adherence requirements conditional and
acknowledged uncertainty about initial versus replacement equipment. Applicability
of those conditional requirements still needs human review. `warnings` was empty;
this does not mean the case was complete or ready for authorization.

### Presentation observations

The retrieval queries contain Python list-style brackets and quotes around
clinical facts. Retrieval succeeded in these examples, but joining the facts as
plain text could improve readability. Minor spacing defects also appear in the
pasted output; their origin is not established by this transcript.

## Retrieval Rankings

| Rank | CPAP section | Score | Lumbar MRI section | Score |
|---|---|---:|---|---:|
| 1 | Required Documentation | 0.803357 | Coverage Criteria | 0.837706 |
| 2 | Coverage Criteria | 0.795697 | Required Documentation | 0.830208 |
| 3 | Decision Boundary | 0.751900 | Decision Boundary | 0.797390 |
| 4 | Limitations and Exceptions | 0.733793 | Limitations and Exceptions | 0.789651 |
| 5 | Purpose | 0.716983 | Purpose | 0.782658 |

All five chunks in each full response belong to the expected policy. Scores are
cosine similarities, not probabilities that the analysis is correct.

## Citation Checks and Repeat Request

The separately repeated lumbar request exposed four finding citation IDs:
`coverage-criteria`, `required-documentation`, `limitations`, and
`decision-boundary`, all under `POL-LUMBAR-MRI-001` version `1.0.0`. All four
appear in that request's five retrieved IDs; `purpose` was retrieved but not cited.
There is no requirement to cite every retrieved section.

The first full lumbar response cited five unique sections, while the repeat used
four. Citation selection can vary between calls. The repeat's complete analysis,
latency, and usage were not supplied, so only citation membership can be assessed
for that run.


## Performance and Usage

| Full response | Reported latency (ms) | Input tokens | Output tokens | Total tokens | Query embedding tokens |
|---|---:|---:|---:|---:|---:|
| CPAP — PA-1102 | 13,090 | 2,321 | 1,021 | 3,342 | 55 |
| Lumbar MRI — PA-1101 | 10,980 | 2,373 | 1,078 | 3,451 | 52 |

Token figures are copied from the top-level `token_usage` and separate
`policy_retrieval.usage` fields; embedding tokens are reported separately here.
Each enterprise tool reported `duration_ms: 0`, which should not be interpreted
as literally zero execution time. These are application-reported single-run
measurements, not independent cURL round-trip timings or a benchmark.

## Grounding Controls

The following describe intended application controls. The captured responses
support the successful paths; rejection and adversarial paths remain unverified
by this transcript.

- Enterprise data comes only from trusted tool results.
- All three enterprise tools are mandatory.
- Retrieved policies are isolated in source blocks.
- Policy findings require citations.
- Citation IDs must match retrieved chunks.
- Invented citation IDs cause request failure.
- Retrieved policy text is treated as evidence, not instructions.
- Outside coverage-policy knowledge is prohibited.
- Authorization remains not_determined.
- Human review remains required.

## Remaining Verification

- Exercise invented citations, evidence-found status without findings, and empty retrieval results.
- Test missing or duplicate enterprise tools, provider failures, and member/provider conflicts.
- Review claim-to-citation support and conditional policy applicability on more cases.
- Repeat cases and test retrieval across related policies before assessing reliability.

## Known Limitations

- Retrieval thresholds have not been tuned.
- Prompt-injection attacks inside policy documents have not yet been
  formally tested.
- The retrieval corpus contains synthetic policies only.
- Groundedness has not yet been measured against a labeled evaluation
  dataset.

Day 12 will add malicious instructions to retrieved documents and test
that the workflow rejects or isolates them.