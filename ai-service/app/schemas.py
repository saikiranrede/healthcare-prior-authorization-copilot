from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CaseAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    member_id: str = Field(min_length=1)

    provider_id: str = Field(min_length=1)

    case_id: str = Field(
        min_length=1,
        max_length=50,
        description="Synthetic prior-authorization case identifier",
        examples=["PA-1001"],
    )
    requested_service: str = Field(
        min_length=2,
        max_length=200,
        description="Healthcare service requiring review",
        examples=["Lumbar spine MRI"],
    )
    clinical_information: list[str] = Field(
        min_length=1,
        max_length=20,
        description="Synthetic clinical facts supplied with the case",
        examples=[
            [
                "Patient reports lower-back pain.",
                "Symptom duration was not supplied.",
                "Previous conservative treatment was not supplied.",
            ]
        ],
    )


class StructuredCaseAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_summary: str = Field(
        description=(
            "A short summary using only facts explicitly supplied "
            "in the case"
        )
    )

    known_facts: list[str] = Field(
        description=(
            "Facts explicitly present in the submitted case; "
            "do not include assumptions"
        )
    )

    missing_information: list[str] = Field(
        description=(
            "Information explicitly identified as absent, or information "
            "required by a supplied policy but absent from the case"
        )
    )

    evidence_sufficiency: Literal[
        "sufficient",
        "insufficient",
        "unclear",
    ] = Field(
        description=(
            "Whether the supplied evidence is sufficient for the next "
            "case-preparation step; this is not a coverage decision"
        )
    )

    recommended_next_action: Literal[
        "request_additional_information",
        "route_to_human_review",
        "continue_case_preparation",
    ] = Field(
        description="The recommended operational workflow action"
    )

    action_reason: str = Field(
        description=(
            "A concise explanation of why the workflow action "
            "was recommended"
        )
    )

    authorization_decision: Literal[
        "not_determined"
    ] = Field(
        description=(
            "The AI must not approve or deny an authorization request"
        )
    )

    human_review_required: bool = Field(
        description=(
            "Whether a human reviewer is required before any "
            "coverage-related action"
        )
    )

    limitations: list[str] = Field(
        description=(
            "Limitations of the analysis, including missing policy "
            "or insufficient evidence"
        )
    )

    warnings: list[str] = Field(
        description=(
            "Potentially conflicting, irrelevant, or unsafe content "
            "found in the submitted case"
        )
    )


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class HealthResponse(BaseModel):
    status: Literal["healthy"]
    service: str


class EligibilityResult(BaseModel):
    member_id: str
    status: Literal["active", "inactive", "not_found"]
    plan_name: str | None = None
    coverage_start_date: str | None = None
    coverage_end_date: str | None = None
    source: Literal["synthetic_member_repository"]
    checked_at: str


class ToolExecutionRecord(BaseModel):
    tool_name: Literal[
        "check_member_eligibility",
        "get_claim_history",
        "get_provider_information",
        ]
    call_id: str
    status: Literal["succeeded", "failed"]
    duration_ms: int


class ClaimRecord(BaseModel):
    claim_id: str
    service_date: str
    service_type: str
    diagnosis_code: str
    procedure_code: str
    status: Literal["paid", "denied", "pending"]


class ClaimHistoryResult(BaseModel):
    member_id: str
    claims: list[ClaimRecord]
    total_claims: int
    source: Literal["synthetic_claims_repository"]
    checked_at: str


class ProviderInformationResult(BaseModel):
    provider_id: str
    provider_name: str | None = None
    specialty: str | None = None
    network_status: Literal[
        "in_network",
        "out_of_network",
        "not_found",
    ]
    active: bool | None = None
    source: Literal["synthetic_provider_directory"]
    checked_at: str

    

class CaseAnalysisResponse(BaseModel):
    request_id: str
    model: str
    analysis: StructuredCaseAnalysis
    eligibility_verification: EligibilityResult
    claim_history: ClaimHistoryResult
    provider_information: ProviderInformationResult
    tool_executions: list[ToolExecutionRecord]
    latency_ms: int
    token_usage: TokenUsage | None = None
