# Learning Log

## Day 2 — Client Discovery and Requirements

### What I completed

- Defined the fictional healthcare payer and stakeholders
- Documented the current and proposed workflows
- Separated AI responsibilities from human responsibilities
- Created functional and nonfunctional requirements
- Identified assumptions and discovery questions
- Defined business, technical, and safety metrics

### Key lesson

A Forward Deployed Engineer must convert an ambiguous business problem into
measurable requirements before selecting or implementing AI technology.

### Remaining uncertainty

The proposed pain points and target metrics are hypotheses that would require
validation with real client stakeholders and operational data.


## Day 3 — First LLM API Experiments

### What I completed

- Configured the OpenAI Python SDK
- Sent requests through the Responses API
- Separated high-level instructions from case input
- Measured latency and token usage
- Compared four instruction strategies
- Tested a conflicting user instruction
- Manually scored groundedness and instruction following

### Key lessons

- LLM output is nondeterministic and must be evaluated.
- Detailed instructions improve behavior but do not guarantee correctness.
- Model input and high-level application instructions serve different purposes.
- Token usage affects cost and latency.
- Safety requires application controls in addition to prompting.

### Remaining questions

- How can responses be forced into a validated schema?
- How should transient API failures be handled?
- How can these tests become automated evaluations?


## Day 4 — FastAPI LLM Service

### What I completed

- Created a FastAPI application
- Added health and case-analysis endpoints
- Added Pydantic request validation
- Added a stable API response model
- Integrated the OpenAI Responses API
- Reused grounded and injection-resistant instructions
- Captured latency and token usage
- Translated provider errors into controlled HTTP responses
- Tested valid, invalid, and adversarial requests

### Key lessons

- Request validation should happen before an LLM call.
- Client input must be treated as untrusted data.
- API consumers need a stable contract even when model output is nondeterministic.
- Model-provider failures must be translated into controlled service responses.
- Prompt instructions are only one part of application safety.

### Remaining questions

- How can the LLM response be constrained to a strict schema?
- How should the endpoint be tested without making a real API call?
- How should prompts and schemas be versioned?
- How should retries and timeouts be configured?


## Day 5 — Structured LLM Outputs

### What I completed

- Designed a structured prior-authorization analysis schema
- Added constrained enum values for evidence and workflow actions
- Prevented the schema from representing approval or denial
- Replaced `responses.create` with `responses.parse`
- Parsed model output directly into a Pydantic object
- Added a schema version to the API response
- Tested incomplete, more complete, and adversarial cases
- Verified that Pydantic rejects invalid decision values

### Key lessons

- Valid JSON is not the same as schema-valid JSON.
- Structured Outputs provide shape and type guarantees, not factual guarantees.
- The schema should make unsafe states difficult or impossible to represent.
- Business decision boundaries should exist in application types as well as prompts.
- Model refusals and incomplete responses must be handled explicitly.

### Remaining questions

- How should structured output be evaluated automatically?
- How should refusals and incomplete model responses be distinguished?
- How will the application obtain policy evidence?
- How should API schemas be versioned as the product evolves?