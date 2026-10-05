from typing import Literal

from pydantic import BaseModel, Field


class PolicySection(BaseModel):
    section_id: str = Field(min_length=1)
    heading: str = Field(min_length=1)
    text: str = Field(min_length=1)


class PolicyDocument(BaseModel):
    policy_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    document_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    dataset_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")

    effective_date: str
    last_reviewed_date: str

    status: Literal["active", "retired", "draft"]
    policy_type: Literal["synthetic"]
    service_category: str
    jurisdiction: Literal["synthetic-national"]

    keywords: list[str]
    sections: list[PolicySection]

    human_review_required: Literal[True]
    authorization_decision_supported: Literal[False]

    disclaimer: str = (
        "Synthetic policy created for software demonstration and "
        "evaluation. It is not medical or insurance guidance."
    )