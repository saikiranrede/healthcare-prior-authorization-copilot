import json
import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import ValidationError

from app.prompts import (
    ELIGIBILITY_TOOL_INSTRUCTIONS,
    PRIOR_AUTHORIZATION_INSTRUCTIONS,
)
from app.schemas import (
    CaseAnalysisRequest,
    CaseAnalysisResponse,
    StructuredCaseAnalysis,
    TokenUsage,
    ToolExecutionRecord,
)
from app.tools import ELIGIBILITY_TOOLS, execute_tool


load_dotenv()

MODEL = os.getenv("OPENAI_MODEL")
if not MODEL:
    raise RuntimeError("OPENAI_MODEL is not configured")

client = OpenAI()

app = FastAPI(
    title="Healthcare Prior Authorization Copilot",
    description=(
        "A portfolio API that analyzes synthetic prior-authorization cases. "
        "It does not approve, deny, or provide medical advice."
    ),
    version="0.2.0",
)


def build_case_input(case: CaseAnalysisRequest) -> str:
    return f"""
Analyze the following case data.

Case ID: {case.case_id}
Member ID: {case.member_id}
Requested service: {case.requested_service}
Clinical information:
{case.clinical_information}
""".strip()


# @app.get(
#     "/health",
#     response_model=HealthResponse,
#     tags=["System"],
# )
# def health_check() -> HealthResponse:
#     return HealthResponse(
#         status="healthy",
#         service="healthcare-prior-authorization-copilot",
#     )


@app.post("/analyze-case", response_model=CaseAnalysisResponse)
def analyze_case(case: CaseAnalysisRequest) -> CaseAnalysisResponse:
    request_started = time.perf_counter()

    input_items = [
        {
            "role": "user",
            "content": build_case_input(case),
        }
    ]

    try:
        # Call 1: require the model to request the eligibility tool.
        tool_response = client.responses.create(
            model=MODEL,
            instructions=ELIGIBILITY_TOOL_INSTRUCTIONS,
            input=input_items,
            tools=ELIGIBILITY_TOOLS,
            tool_choice={
                "type": "function",
                "name": "check_member_eligibility",
            },
            parallel_tool_calls=False,
            store=False,
        )

        tool_call = next(
            (
                item
                for item in tool_response.output
                if item.type == "function_call"
            ),
            None,
        )

        if tool_call is None:
            raise HTTPException(
                status_code=502,
                detail="The model did not request the required eligibility tool.",
            )

        try:
            raw_arguments = json.loads(tool_call.arguments)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=502,
                detail="The model returned invalid tool arguments.",
            ) from exc

        tool_started = time.perf_counter()

        eligibility_result = execute_tool(
            tool_name=tool_call.name,
            raw_arguments=raw_arguments,
        )

        tool_duration_ms = round(
            (time.perf_counter() - tool_started) * 1000
        )

        # Preserve the first response, including any reasoning items.
        input_items.extend(tool_response.output)

        # Return the deterministic application result to the model.
        input_items.append(
            {
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": json.dumps(
                    eligibility_result.model_dump(mode="json")
                ),
            }
        )

        # Call 2: convert case data + tool result into structured output.
        final_response = client.responses.parse(
            model=MODEL,
            instructions=PRIOR_AUTHORIZATION_INSTRUCTIONS,
            input=input_items,
            text_format=StructuredCaseAnalysis,
            max_output_tokens=700,
            store=False,
        )

        analysis = final_response.output_parsed

        if analysis is None:
            raise HTTPException(
                status_code=502,
                detail="The model did not return structured analysis.",
            )

        total_latency_ms = round(
            (time.perf_counter() - request_started) * 1000
        )

        return CaseAnalysisResponse(
            request_id=final_response.id,
            model=MODEL,
            latency_ms=total_latency_ms,
            token_usage=combine_usage(tool_response, final_response),
            eligibility_verification=eligibility_result,
            tool_executions=[
                ToolExecutionRecord(
                    tool_name="check_member_eligibility",
                    call_id=tool_call.call_id,
                    status="succeeded",
                    duration_ms=tool_duration_ms,
                )
            ],
            analysis=analysis,
        )

    except HTTPException:
        raise
    except (ValidationError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Tool execution failed: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Case analysis failed.",
        ) from exc



def combine_usage(*responses) -> TokenUsage | None:
    input_tokens = 0
    output_tokens = 0
    found_usage = False

    for response in responses:
        usage = getattr(response, "usage", None)

        if usage is not None:
            found_usage = True
            input_tokens += usage.input_tokens
            output_tokens += usage.output_tokens

    if not found_usage:
        return None

    return TokenUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
    )