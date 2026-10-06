import json
import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import ValidationError

from app.prompts import (
    ENTERPRISE_TOOL_INSTRUCTIONS,
    PRIOR_AUTHORIZATION_INSTRUCTIONS,
    GROUNDED_CASE_ANALYSIS_INSTRUCTIONS,
)
from app.schemas import (
    CaseAnalysisRequest,
    CaseAnalysisResponse,
    HealthResponse,
    StructuredCaseAnalysis,
    TokenUsage,
    ToolExecutionRecord,
)
from app.tools import ENTERPRISE_TOOLS, execute_tool
from app.retrieval import get_policy_retrieval_service
from app.retrieval_schemas import (
    PolicyRetrievalRequest,
    PolicyRetrievalResponse,
)
from app.case_workflow import (
    CitationValidationError,
    build_grounded_policy_context,
    build_policy_retrieval_query,
    validate_policy_citations,
)


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
Provider ID: {case.provider_id}
Requested service: {case.requested_service}
Clinical information:
{case.clinical_information}
""".strip()


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="healthcare-prior-authorization-copilot",
    )


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
            instructions=ENTERPRISE_TOOL_INSTRUCTIONS,
            input=input_items,
            tools=ENTERPRISE_TOOLS,
            tool_choice="required",
            parallel_tool_calls=True,
            store=False,
        )

        tool_calls = [
            
            item
            for item in tool_response.output
            if item.type == "function_call"
            
        ]

        if not tool_calls:
            raise HTTPException(
                status_code=502,
                detail="The model did not request enterprise tools.",
            )

        input_items.extend(tool_response.output)

        tool_results = {}
        tool_executions = []

        for tool_call in tool_calls:
            raw_arguments = json.loads(tool_call.arguments)

            tool_started = time.perf_counter()

            result = execute_tool(
                tool_name=tool_call.name,
                raw_arguments=raw_arguments,
            )

            duration_ms = round(
                (time.perf_counter() - tool_started) * 1000
            )

            tool_results[tool_call.name] = result

            tool_executions.append(
                ToolExecutionRecord(
                    tool_name=tool_call.name,
                    call_id=tool_call.call_id,
                    status="succeeded",
                    duration_ms=duration_ms,
                )
            )

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(
                        result.model_dump(mode="json")
                    ),
                }
            )

        required_tools = {
            "check_member_eligibility",
            "get_claim_history",
            "get_provider_information",
        }

        executed_tools = set(tool_results)

        missing_tools = required_tools - executed_tools
        unexpected_tools = executed_tools - required_tools

        if missing_tools:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Required enterprise tools were not executed.",
                    "missing_tools": sorted(missing_tools),
                },
            )

        if unexpected_tools:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": (
                        "Unexpected enterprise tools were executed."
                    ),
                    "unexpected_tools": sorted(
                        unexpected_tools
                    ),
                },
            )


        if len(tool_calls) != len(executed_tools):
            raise HTTPException(
                status_code=502,
                detail="One or more enterprise tools were requested more than once.",
            )

        # Retrieve applicable policy evidence
        retrieval_service = get_policy_retrieval_service()

        retrieval_query = build_policy_retrieval_query(case)

        policy_retrieval = retrieval_service.retrieve(
            PolicyRetrievalRequest(
                query=retrieval_query,
                top_k=5,
            )
        )

        if not policy_retrieval.results:
            policy_context = (
                "RETRIEVED POLICY EVIDENCE\n\n"
                "No policy evidence was retrieved."
            )
        else:
            policy_context = build_grounded_policy_context(
                retrieval_service=retrieval_service,
                retrieval=policy_retrieval,
            )


        input_items.append(
            {
                "role": "user",
                "content": "\n".join(
                    [
                        (
                            "Prepare the final structured case "
                            "analysis using the enterprise results "
                            "and retrieved evidence."
                        ),
                        "",
                        policy_context,
                    ]
                ),
            }
        )

        # Call 2: convert case data + tool result into structured output.
        # final_response = client.responses.parse(
        #     model=MODEL,
        #     instructions=PRIOR_AUTHORIZATION_INSTRUCTIONS,
        #     input=input_items,
        #     text_format=StructuredCaseAnalysis,
        #     max_output_tokens=900,
        #     store=False,
        # )

        # Generate the grounded structured analysis - case data + tool result + policy retrieval into structured output.
        final_response = client.responses.parse(
            model=MODEL,
            instructions=(
                GROUNDED_CASE_ANALYSIS_INSTRUCTIONS
            ),
            input=input_items,
            text_format=StructuredCaseAnalysis,
            max_output_tokens=1200,
            store=False,
        )

        analysis = final_response.output_parsed

        if analysis is None:
            raise HTTPException(
                status_code=502,
                detail="The model did not return structured analysis.",
            )

        # analysis = enforce_safety_invariants(analysis)

        validate_policy_citations(
            analysis=analysis,
            retrieval=policy_retrieval,
        )

        total_latency_ms = round(
            (time.perf_counter() - request_started) * 1000
        )

        return CaseAnalysisResponse(
            request_id=final_response.id,
            model=MODEL,
            latency_ms=total_latency_ms,
            token_usage=combine_usage(tool_response, final_response),
            eligibility_verification=tool_results[
                "check_member_eligibility"
            ],
            claim_history=tool_results[
                "get_claim_history"
            ],
            provider_information=tool_results[
                "get_provider_information"
            ],
            tool_executions=tool_executions,
            policy_retrieval=policy_retrieval,
            analysis=analysis,
        )

    except HTTPException:
        raise
    except (ValidationError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Tool execution failed: {exc}",
        ) from exc
    except CitationValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Citation validation failed: {exc}",
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

@app.post(
    "/retrieve-policies",
    response_model=PolicyRetrievalResponse,
)
def retrieve_policies(
    request: PolicyRetrievalRequest,
) -> PolicyRetrievalResponse:
    try:
        retrieval_service = (
            get_policy_retrieval_service()
        )

        return retrieval_service.retrieve(request)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Policy vector index is not available. "
                "Build the index before retrieving policies."
            ),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Policy retrieval failed.",
        ) from exc