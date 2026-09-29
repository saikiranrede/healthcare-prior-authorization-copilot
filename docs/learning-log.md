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