# Day 8 — Synthetic Healthcare Policy Dataset

## Objective

Create a versioned set of 10 synthetic healthcare policies that can
serve as the retrieval knowledge base for the case-preparation system.

## Dataset

- Dataset name: synthetic-healthcare-policies
- Dataset version: 1.0.0
- Policy count: 10
- Real PHI: No
- Real payer policies: No
- Autonomous authorization supported: No

## Policies

| Policy ID | Title | Category |
|---|---|---|
| POL-LUMBAR-MRI-001 | Lumbar Spine MRI | Advanced diagnostic imaging |
| POL-CERVICAL-MRI-002 | Cervical Spine MRI | Advanced diagnostic imaging |
| POL-KNEE-MRI-003 | Knee MRI | Advanced diagnostic imaging |
| POL-CHEST-CT-004 | Chest CT | Advanced diagnostic imaging |
| POL-PHYSICAL-THERAPY-005 | Outpatient Physical Therapy | Rehabilitation |
| POL-CPAP-006 | Positive Airway Pressure Equipment | Durable medical equipment |
| POL-HOME-HEALTH-007 | Home Health Services | Home health |
| POL-INPATIENT-008 | Elective Inpatient Admission | Facility admission |
| POL-BIOLOGIC-009 | Specialty Biologic Medication | Specialty pharmacy |
| POL-COLONOSCOPY-010 | Colonoscopy Services | Gastroenterology |

## Versioning Strategy

Dataset releases use semantic versioning.

- Major: incompatible schema or policy redesign
- Minor: new policies or backward-compatible fields
- Patch: corrections that do not change the schema

Each document includes its own document version and the version of the
dataset in which it was published.

## Integrity Controls

The manifest records each policy filename, policy ID, document version
and SHA-256 checksum.

The validation script checks:

- Policy count
- Unique policy IDs
- Required sections
- Dataset-version consistency
- Synthetic-data declaration
- Human-review requirement
- Autonomous-decision prohibition
- File checksums

## Safety Boundary

These policies are fictional and are intended solely for software
development and evaluation. They do not represent medical advice,
coverage guidance or the policies of a real payer.

The policies may identify information relevant to case preparation, but
they cannot approve or deny a request.