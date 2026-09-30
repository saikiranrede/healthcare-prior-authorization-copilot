from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CaseAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    eligibility_status: Literal["active", "inactive", "unknown"]
    clinical_information: list[str] = Field(
        min_length=1,
        max_length=20,
        description="Synthetic clinical facts submitted with the request",
        examples=[
            [
                "Patient reports lower-back pain.",
                "Symptom duration was not supplied.",
                "Previous conservative treatment was not supplied.",
            ]
        ],
    )


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class CaseAnalysisResponse(BaseModel):
    case_id: str
    request_id: str
    model: str
    status: Literal["completed"]
    analysis: str
    latency_ms: int
    token_usage: TokenUsage | None = None


class HealthResponse(BaseModel):
    status: Literal["healthy"]
    service: str