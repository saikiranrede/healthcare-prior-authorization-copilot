from pydantic import BaseModel, Field

from app.eligibility import check_member_eligibility
from app.schemas import EligibilityResult


class EligibilityLookupArguments(BaseModel):
    member_id: str = Field(min_length=1)


ELIGIBILITY_TOOLS = [
    {
        "type": "function",
        "name": "check_member_eligibility",
        "description": (
            "Checks the member's current eligibility in the trusted "
            "synthetic membership repository."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "member_id": {
                    "type": "string",
                    "description": "The synthetic member identifier.",
                }
            },
            "required": ["member_id"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]


def execute_tool(
    tool_name: str,
    raw_arguments: dict,
) -> EligibilityResult:
    if tool_name != "check_member_eligibility":
        raise ValueError(f"Unsupported tool: {tool_name}")

    arguments = EligibilityLookupArguments.model_validate(raw_arguments)

    return check_member_eligibility(arguments.member_id)