# Prior Authorization Workflow

## Current-State Workflow

1. A healthcare provider submits a prior-authorization request.
2. An intake system creates a case.
3. A reviewer verifies member eligibility in a separate system.
4. The reviewer checks whether the service requires authorization.
5. The reviewer searches for the applicable coverage policy.
6. The reviewer examines clinical documents manually.
7. The reviewer searches claim history when additional context is needed.
8. Missing information is identified.
9. The reviewer contacts the provider for additional documentation.
10. Complete cases are prepared for clinical review.
11. Complex or uncertain cases are escalated.
12. The final outcome and supporting evidence are recorded.

## Current Pain Points

- Reviewers switch between multiple systems.
- Coverage policies can be lengthy and difficult to search.
- Different reviewers may locate different policy sections.
- Missing documentation may be found late in the process.
- Manual case summaries consume reviewer time.
- Supporting evidence may not be recorded consistently.
- Audit reconstruction can require reviewing several systems.
- High-volume periods increase turnaround times.

## Discovery Assumption

These pain points are working assumptions for the portfolio project. In a real
client engagement, they would be validated through stakeholder interviews,
workflow observation, operational data, and sample-case analysis.

## Proposed AI-Assisted Workflow

1. The application receives a synthetic prior-authorization case.
2. The request is validated against a defined schema.
3. Sensitive fields are masked or excluded from the model request.
4. The system calls an eligibility API.
5. The system retrieves applicable coverage-policy sections.
6. The system calls claim-history and provider-information APIs when needed.
7. The LLM analyzes the available evidence.
8. The application validates the response against a strict output schema.
9. The copilot presents:
   - Relevant policy citations
   - Missing documentation
   - Case summary
   - Recommended next action
   - Confidence and escalation reasons
10. A human reviewer accepts, modifies, or rejects the recommendation.
11. Only an authorized user can update the case.
12. The application records inputs, retrieved evidence, tool calls, model version,
    prompt version, reviewer action, latency, and outcome.

## Human and AI responsibilities

| AI may assist with                | Human remains responsible for                 |
| --------------------------------- | --------------------------------------------- |
| Summarizing case information      | Making the final coverage decision            |
| Retrieving policy sections        | Interpreting ambiguous clinical circumstances |
| Detecting missing fields          | Approving or denying the request              |
| Suggesting the next workflow step | Overriding incorrect recommendations          |
| Preparing a cited recommendation  | Handling appeals and exceptions               |
| Routing uncertain cases           | Accepting accountability for final action     |

