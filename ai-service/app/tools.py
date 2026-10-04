from pydantic import BaseModel, Field

from app.claims import get_claim_history
from app.eligibility import check_member_eligibility
from app.providers import get_provider_information


class MemberLookupArguments(BaseModel):
    member_id: str = Field(min_length=1)


class ProviderLookupArguments(BaseModel):
    provider_id: str = Field(min_length=1)


ENTERPRISE_TOOLS = [
    {
        "type": "function",
        "name": "check_member_eligibility",
        "description": (
            "Checks the member's eligibility using the trusted "
            "synthetic membership repository."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "member_id": {"type": "string"}
            },
            "required": ["member_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_claim_history",
        "description": (
            "Retrieves the member's recent synthetic claim history. "
            "Claims provide historical context but do not independently "
            "prove medical necessity."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "member_id": {"type": "string"}
            },
            "required": ["member_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_provider_information",
        "description": (
            "Retrieves provider identity, specialty, active status, "
            "and network status from the synthetic provider directory."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "provider_id": {"type": "string"}
            },
            "required": ["provider_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def execute_tool(
    tool_name: str,
    raw_arguments: dict,
):
    if tool_name == "check_member_eligibility":
        arguments = MemberLookupArguments.model_validate(
            raw_arguments
        )
        return check_member_eligibility(arguments.member_id)

    if tool_name == "get_claim_history":
        arguments = MemberLookupArguments.model_validate(
            raw_arguments
        )
        return get_claim_history(arguments.member_id)

    if tool_name == "get_provider_information":
        arguments = ProviderLookupArguments.model_validate(
            raw_arguments
        )
        return get_provider_information(arguments.provider_id)

    raise ValueError(f"Unsupported tool: {tool_name}")