import pytest

from app.case_workflow import (
    CitationValidationError,
    build_policy_retrieval_query,
    validate_policy_citations,
)
from app.retrieval_schemas import (
    PolicyCitation,
    PolicyRetrievalResponse,
    PolicyRetrievalResult,
    RetrievalUsage,
)
from app.schemas import (
    CaseAnalysisRequest,
    CitedPolicyFinding,
    StructuredCaseAnalysis,
)


CITATION_ID = (
    "POL-LUMBAR-MRI-001::"
    "required-documentation::v1.0.0"
)


def build_retrieval() -> PolicyRetrievalResponse:
    return PolicyRetrievalResponse(
        query="lumbar MRI documentation",
        requested_top_k=1,
        returned_results=1,
        index_version="1.0.0",
        dataset_version="1.0.0",
        service_category_filter=None,
        minimum_score_filter=None,
        results=[
            PolicyRetrievalResult(
                rank=1,
                similarity_score=0.9,
                content="Symptom duration is required.",
                citation=PolicyCitation(
                    citation_id=CITATION_ID,
                    citation_uri=(
                        "policy://POL-LUMBAR-MRI-001/"
                        "versions/1.0.0/sections/"
                        "required-documentation"
                    ),
                    policy_id="POL-LUMBAR-MRI-001",
                    policy_title="Lumbar Spine MRI",
                    document_version="1.0.0",
                    dataset_version="1.0.0",
                    section_id="required-documentation",
                    section_heading=(
                        "Required Documentation"
                    ),
                    service_category=(
                        "advanced-diagnostic-imaging"
                    ),
                    source_filename=(
                        "POL-LUMBAR-MRI-001.json"
                    ),
                    source_sha256="a" * 64,
                ),
            )
        ],
        usage=RetrievalUsage(
            embedding_model="text-embedding-3-small",
            query_tokens=10,
        ),
    )


def build_analysis(
    citation_id: str = CITATION_ID,
) -> StructuredCaseAnalysis:
    return StructuredCaseAnalysis(
        case_summary="Lumbar MRI case.",
        known_facts=[
            "The member has active eligibility."
        ],
        missing_information=[
            "Symptom duration was not supplied."
        ],
        policy_basis_status=(
            "policy_evidence_found"
        ),
        policy_findings=[
            CitedPolicyFinding(
                finding=(
                    "The policy requests symptom duration."
                ),
                citation_ids=[citation_id],
            )
        ],
        evidence_sufficiency="unclear",
        case_preparation_sufficiency="unclear",
        recommended_next_action=(
            "route_to_human_review"
        ),
        action_reason=(
            "Symptom duration is missing; human review is required."
        ),
        authorization_decision="not_determined",
        human_review_required=True,
        limitations=[
            "No authorization decision was made."
        ],
        warnings=[],
    )


def test_build_policy_retrieval_query():
    case = CaseAnalysisRequest(
        case_id="PA-1101",
        member_id="M-1001",
        provider_id="P-2001",
        requested_service="Lumbar spine MRI",
        clinical_information=["Lower-back pain."],
    )

    query = build_policy_retrieval_query(case)

    assert "Lumbar spine MRI" in query
    assert "Lower-back pain" in query


def test_accept_retrieved_citation():
    validate_policy_citations(
        analysis=build_analysis(),
        retrieval=build_retrieval(),
    )


def test_reject_invented_citation():
    analysis = build_analysis(
        citation_id="INVENTED-POLICY"
    )

    with pytest.raises(
        CitationValidationError,
        match="unknown citation",
    ):
        validate_policy_citations(
            analysis=analysis,
            retrieval=build_retrieval(),
        )


def test_reject_found_status_without_findings():
    analysis = build_analysis()
    analysis.policy_findings = []

    with pytest.raises(
        CitationValidationError,
        match="no policy findings",
    ):
        validate_policy_citations(
            analysis=analysis,
            retrieval=build_retrieval(),
        )