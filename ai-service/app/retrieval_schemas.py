from pydantic import BaseModel, Field, field_validator


class PolicyRetrievalRequest(BaseModel):
    query: str = Field(
        min_length=3,
        max_length=1000,
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )
    service_category: str | None = None
    minimum_score: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        normalized = value.strip()

        if len(normalized) < 3:
            raise ValueError(
                "Query must contain at least three characters."
            )

        return normalized

    @field_validator("service_category")
    @classmethod
    def normalize_category(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip().lower()

        if not normalized:
            return None

        return normalized


class PolicyCitation(BaseModel):
    citation_id: str
    citation_uri: str

    policy_id: str
    policy_title: str

    document_version: str
    dataset_version: str

    section_id: str
    section_heading: str

    service_category: str
    source_filename: str
    source_sha256: str


class PolicyRetrievalResult(BaseModel):
    rank: int
    similarity_score: float
    content: str
    citation: PolicyCitation


class RetrievalUsage(BaseModel):
    embedding_model: str
    query_tokens: int | None = None


class PolicyRetrievalResponse(BaseModel):
    query: str
    requested_top_k: int
    returned_results: int

    index_version: str
    dataset_version: str
    retrieval_method: str = "cosine_similarity"

    service_category_filter: str | None = None
    minimum_score_filter: float | None = None

    results: list[PolicyRetrievalResult]
    usage: RetrievalUsage