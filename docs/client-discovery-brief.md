# Client Discovery Brief

## Project

Healthcare Prior Authorization Copilot

## Purpose

This document captures the client problem, stakeholders, current workflow,
business constraints, solution boundaries, risks, assumptions, and measurable
outcomes for an AI-assisted prior-authorization workflow.

## Client Profile

ClearHealth Plans is a fictional regional healthcare payer serving approximately
500,000 members through commercial and Medicare Advantage plans.

The organization receives prior-authorization requests from hospitals, physician
offices, imaging centers, and other healthcare providers. Reviewers use several
systems to verify member eligibility, inspect submitted documentation, examine
claim history, and locate the appropriate coverage policy.

All project data is synthetic. ClearHealth Plans is not a real organization.

## Stakeholders

| Stakeholder                     | Primary need                  | Current difficulty                        | Desired outcome                      |
| ------------------------------- | ----------------------------- | ----------------------------------------- | ------------------------------------ |
| Utilization-management reviewer | Prepare cases accurately      | Information is distributed across systems | Consolidated case summary            |
| UM nurse                        | Evaluate documentation        | Missing documents are discovered late     | Early missing-document detection     |
| Medical director                | Review escalated cases        | Time spent reconstructing evidence        | Clear evidence and policy citations  |
| Provider representative         | Receive timely status         | Delayed or unclear responses              | Faster, consistent communication     |
| Operations manager              | Improve turnaround time       | Limited visibility into bottlenecks       | Measurable workflow performance      |
| Compliance officer              | Verify correct processing     | Difficult audit reconstruction            | Complete decision audit trail        |
| Security team                   | Protect sensitive information | Potential AI data exposure                | Controlled and traceable data access |
| Platform engineer               | Operate the application       | New model-related failure modes           | Observable and supportable services  |

## Working Assumptions

- The client already has APIs for eligibility, claims, providers, and case status.
- Coverage policies are available as versioned electronic documents.
- Final decisions must remain under human control.
- The first release supports case preparation rather than autonomous adjudication.
- The portfolio implementation uses synthetic healthcare information.
- English-language policies and documents are sufficient for the initial release.

## Open Discovery Questions

1. Which case categories create the largest review backlog?
2. What is the current average and P95 turnaround time?
3. How frequently do reviewers discover missing documentation?
4. Which systems contain eligibility, claim, provider, and policy information?
5. Are stable APIs available for those systems?
6. Which steps legally or operationally require human review?
7. What evidence must be retained for an audit?
8. What accuracy level is required before a recommendation is displayed?
9. What should happen when the model or retrieval system is unavailable?
10. Which users can view, modify, approve, or override a recommendation?
11. What data may be sent to the selected model provider?
12. How will the client evaluate a pilot before production approval?