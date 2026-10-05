import hashlib
import json
from pathlib import Path

from app.policy_schemas import PolicyDocument


DATASET_VERSION = "1.0.0"
OUTPUT_DIRECTORY = Path(f"data/policies/v{DATASET_VERSION}")


def make_sections(
    coverage_criteria: list[str],
    required_documentation: list[str],
    limitations: list[str],
) -> list[dict]:
    return [
        {
            "section_id": "purpose",
            "heading": "Purpose",
            "text": (
                "This synthetic policy identifies information used to "
                "prepare a service request for human review."
            ),
        },
        {
            "section_id": "coverage-criteria",
            "heading": "Coverage Criteria",
            "text": "\n".join(
                f"- {criterion}"
                for criterion in coverage_criteria
            ),
        },
        {
            "section_id": "required-documentation",
            "heading": "Required Documentation",
            "text": "\n".join(
                f"- {item}"
                for item in required_documentation
            ),
        },
        {
            "section_id": "limitations",
            "heading": "Limitations and Exceptions",
            "text": "\n".join(
                f"- {item}"
                for item in limitations
            ),
        },
        {
            "section_id": "decision-boundary",
            "heading": "Decision Boundary",
            "text": (
                "Meeting the listed criteria does not automatically "
                "approve the request. Eligibility, benefits, exclusions, "
                "clinical context and applicable requirements must be "
                "reviewed by an authorized human reviewer."
            ),
        },
    ]


def make_policy(
    policy_id: str,
    title: str,
    service_category: str,
    keywords: list[str],
    coverage_criteria: list[str],
    required_documentation: list[str],
    limitations: list[str],
) -> dict:
    return {
        "policy_id": policy_id,
        "title": title,
        "document_version": "1.0.0",
        "dataset_version": DATASET_VERSION,
        "effective_date": "2026-01-01",
        "last_reviewed_date": "2026-09-01",
        "status": "active",
        "policy_type": "synthetic",
        "service_category": service_category,
        "jurisdiction": "synthetic-national",
        "keywords": keywords,
        "sections": make_sections(
            coverage_criteria,
            required_documentation,
            limitations,
        ),
        "human_review_required": True,
        "authorization_decision_supported": False,
        "disclaimer": (
            "Synthetic policy created for software demonstration and "
            "evaluation. It is not medical or insurance guidance."
        ),
    }


POLICIES = [
    make_policy(
        policy_id="POL-LUMBAR-MRI-001",
        title="Lumbar Spine MRI",
        service_category="advanced-diagnostic-imaging",
        keywords=[
            "lumbar MRI",
            "lower-back pain",
            "radiculopathy",
            "neurologic deficit",
        ],
        coverage_criteria=[
            "The request identifies the clinical indication for imaging.",
            "For non-urgent symptoms, the record describes symptom duration and prior conservative management.",
            "Requests involving neurologic deficits or documented red-flag findings may require expedited clinical review.",
        ],
        required_documentation=[
            "Symptom onset, duration, severity and progression",
            "Relevant physical and neurologic examination findings",
            "Conservative treatments attempted and the response",
            "Relevant prior imaging, procedures or surgery",
            "Presence or absence of documented red-flag findings",
        ],
        limitations=[
            "Eligibility does not establish medical necessity.",
            "A prior physical-therapy claim does not prove completion or clinical response.",
            "The policy does not support automatic approval or denial.",
        ],
    ),
    make_policy(
        policy_id="POL-CERVICAL-MRI-002",
        title="Cervical Spine MRI",
        service_category="advanced-diagnostic-imaging",
        keywords=[
            "cervical MRI",
            "neck pain",
            "radiculopathy",
            "upper-extremity weakness",
        ],
        coverage_criteria=[
            "The record identifies the suspected cervical condition and purpose of imaging.",
            "Non-urgent requests describe symptom duration and conservative management.",
            "Progressive neurologic findings may require expedited clinical review.",
        ],
        required_documentation=[
            "Duration and progression of neck or upper-extremity symptoms",
            "Motor, sensory and reflex examination findings",
            "Treatments attempted and documented response",
            "Previous cervical imaging or procedures",
            "Relevant trauma, infection or malignancy history",
        ],
        limitations=[
            "Neck pain alone may not provide sufficient case information.",
            "Claims data cannot replace the clinical examination.",
            "Final determination requires human review.",
        ],
    ),
    make_policy(
        policy_id="POL-KNEE-MRI-003",
        title="Knee MRI",
        service_category="advanced-diagnostic-imaging",
        keywords=[
            "knee MRI",
            "knee pain",
            "meniscal injury",
            "ligament injury",
        ],
        coverage_criteria=[
            "The request documents the suspected internal knee condition.",
            "The record describes examination findings and prior evaluation.",
            "Non-urgent requests describe conservative treatment and response.",
        ],
        required_documentation=[
            "Mechanism and date of injury when applicable",
            "Range-of-motion, instability and examination findings",
            "Prior radiograph or other imaging results",
            "Medication, activity modification or therapy history",
            "Functional limitations caused by the condition",
        ],
        limitations=[
            "A claim containing a knee diagnosis does not establish the requested indication.",
            "Acute injuries may require a different review pathway.",
            "The policy does not make an authorization decision.",
        ],
    ),
    make_policy(
        policy_id="POL-CHEST-CT-004",
        title="Chest CT",
        service_category="advanced-diagnostic-imaging",
        keywords=[
            "chest CT",
            "pulmonary nodule",
            "abnormal chest radiograph",
            "thoracic imaging",
        ],
        coverage_criteria=[
            "The request states the diagnostic question the CT is intended to address.",
            "Relevant prior imaging or clinical findings are identified.",
            "The requested study and use of contrast are clinically explained.",
        ],
        required_documentation=[
            "Relevant symptoms and duration",
            "Prior chest imaging findings",
            "Known risk factors and relevant medical history",
            "Reason for contrast or non-contrast study",
            "Requested follow-up interval when applicable",
        ],
        limitations=[
            "An abnormal prior study should be described rather than merely referenced.",
            "Screening and diagnostic requests may follow different review paths.",
            "Final review remains a human responsibility.",
        ],
    ),
    make_policy(
        policy_id="POL-PHYSICAL-THERAPY-005",
        title="Outpatient Physical Therapy",
        service_category="rehabilitation",
        keywords=[
            "physical therapy",
            "rehabilitation",
            "functional limitation",
            "plan of care",
        ],
        coverage_criteria=[
            "The record identifies a condition associated with measurable functional limitations.",
            "The plan of care contains measurable treatment goals.",
            "Continued-service requests describe objective progress or barriers to progress.",
        ],
        required_documentation=[
            "Diagnosis and functional limitations",
            "Initial assessment findings",
            "Frequency and duration of the proposed plan",
            "Measurable short-term and long-term goals",
            "Progress notes for continued-service requests",
        ],
        limitations=[
            "A paid therapy claim does not establish completion of a therapy course.",
            "Maintenance services may require separate benefit review.",
            "Benefits and visit limits must be checked independently.",
        ],
    ),
    make_policy(
        policy_id="POL-CPAP-006",
        title="Positive Airway Pressure Equipment",
        service_category="durable-medical-equipment",
        keywords=[
            "CPAP",
            "positive airway pressure",
            "sleep apnea",
            "sleep study",
        ],
        coverage_criteria=[
            "The request includes a documented sleep-related diagnosis.",
            "The record references an appropriate diagnostic sleep evaluation.",
            "The requested equipment and settings are supported by a treating-provider order.",
        ],
        required_documentation=[
            "Sleep-study type, date and summarized results",
            "Treating-provider diagnosis",
            "Equipment order and requested settings",
            "Relevant symptoms and comorbidities",
            "Usage or adherence information for continued coverage",
        ],
        limitations=[
            "An equipment order alone does not establish all coverage requirements.",
            "Replacement equipment may require previous-device information.",
            "Benefit coverage must be checked separately.",
        ],
    ),
    make_policy(
        policy_id="POL-HOME-HEALTH-007",
        title="Home Health Services",
        service_category="home-health",
        keywords=[
            "home health",
            "skilled nursing",
            "homebound",
            "plan of care",
        ],
        coverage_criteria=[
            "The request describes why skilled services are needed in the home.",
            "The record includes a treating-provider order and plan of care.",
            "The documentation explains the member's functional limitations and ability to leave home.",
        ],
        required_documentation=[
            "Ordering provider and order date",
            "Requested skilled services and frequency",
            "Homebound assessment",
            "Functional and safety limitations",
            "Goals, expected duration and discharge plan",
        ],
        limitations=[
            "Need for general assistance alone may not establish a skilled-service requirement.",
            "Custodial and skilled services must be distinguished.",
            "Human clinical and benefit review is required.",
        ],
    ),
    make_policy(
        policy_id="POL-INPATIENT-008",
        title="Elective Inpatient Admission",
        service_category="facility-admission",
        keywords=[
            "inpatient admission",
            "elective admission",
            "severity of illness",
            "hospital care",
        ],
        coverage_criteria=[
            "The request identifies the reason inpatient-level care is being considered.",
            "The record describes severity, monitoring needs and planned interventions.",
            "The documentation explains why a lower level of care may be insufficient.",
        ],
        required_documentation=[
            "Primary diagnosis and relevant comorbidities",
            "Current symptoms, examination and test results",
            "Planned treatments, procedures and monitoring",
            "Expected length of stay",
            "Reason outpatient or observation care may be insufficient",
        ],
        limitations=[
            "Network status does not establish the appropriate level of care.",
            "Emergency admissions may follow a separate notification workflow.",
            "An authorized reviewer makes the final determination.",
        ],
    ),
    make_policy(
        policy_id="POL-BIOLOGIC-009",
        title="Specialty Biologic Medication",
        service_category="specialty-pharmacy",
        keywords=[
            "biologic",
            "specialty medication",
            "step therapy",
            "prior treatment",
        ],
        coverage_criteria=[
            "The request identifies the diagnosis and severity of the condition.",
            "Previous therapies, outcomes and relevant contraindications are documented.",
            "The requested medication, dose and frequency are included.",
        ],
        required_documentation=[
            "Confirmed diagnosis and severity assessment",
            "Previous medications, duration and response",
            "Contraindications or intolerance when applicable",
            "Relevant laboratory or screening results",
            "Requested drug, dose, frequency and treatment plan",
        ],
        limitations=[
            "Formulary and benefit rules must be evaluated separately.",
            "A previous medication claim does not establish adherence or treatment failure.",
            "The synthetic policy does not recommend a specific medication.",
        ],
    ),
    make_policy(
        policy_id="POL-COLONOSCOPY-010",
        title="Colonoscopy Services",
        service_category="gastroenterology",
        keywords=[
            "colonoscopy",
            "screening",
            "diagnostic colonoscopy",
            "gastrointestinal symptoms",
        ],
        coverage_criteria=[
            "The request distinguishes screening, surveillance and diagnostic indications.",
            "The record includes relevant symptoms, risk factors or previous findings.",
            "Previous procedure dates and results are identified when applicable.",
        ],
        required_documentation=[
            "Reason for the requested procedure",
            "Relevant symptoms and duration",
            "Personal and family risk history",
            "Previous colonoscopy date and summarized findings",
            "Relevant laboratory, imaging or specialist findings",
        ],
        limitations=[
            "Screening and diagnostic benefits may differ.",
            "Prior procedure history should be verified when available.",
            "This policy supports case preparation only.",
        ],
    ),
]


def calculate_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    manifest_entries = []

    for raw_policy in POLICIES:
        policy = PolicyDocument.model_validate(raw_policy)

        filename = f"{policy.policy_id}.json"
        policy_path = OUTPUT_DIRECTORY / filename

        policy_path.write_text(
            json.dumps(
                policy.model_dump(mode="json"),
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        manifest_entries.append(
            {
                "policy_id": policy.policy_id,
                "title": policy.title,
                "document_version": policy.document_version,
                "filename": filename,
                "sha256": calculate_sha256(policy_path),
            }
        )

    manifest = {
        "dataset_name": "synthetic-healthcare-policies",
        "dataset_version": DATASET_VERSION,
        "policy_count": len(manifest_entries),
        "created_for": "healthcare-fde-portfolio",
        "contains_real_phi": False,
        "contains_real_payer_policies": False,
        "policies": manifest_entries,
    }

    manifest_path = OUTPUT_DIRECTORY / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"Created {len(manifest_entries)} policies "
        f"in {OUTPUT_DIRECTORY}"
    )


if __name__ == "__main__":
    main()