from datetime import datetime, timezone

from app.schemas import ClaimHistoryResult, ClaimRecord


SYNTHETIC_CLAIMS = {
    "M-1001": [
        {
            "claim_id": "CLM-9001",
            "service_date": "2026-07-10",
            "service_type": "Primary care visit",
            "diagnosis_code": "M54.50",
            "procedure_code": "99213",
            "status": "paid",
        },
        {
            "claim_id": "CLM-9002",
            "service_date": "2026-08-02",
            "service_type": "Physical therapy",
            "diagnosis_code": "M54.50",
            "procedure_code": "97110",
            "status": "paid",
        },
    ],
    "M-1002": [],
}


def get_claim_history(member_id: str) -> ClaimHistoryResult:
    normalized_id = member_id.strip().upper()
    records = SYNTHETIC_CLAIMS.get(normalized_id, [])

    claims = [
        ClaimRecord(**record)
        for record in records
    ]

    return ClaimHistoryResult(
        member_id=normalized_id,
        claims=claims,
        total_claims=len(claims),
        source="synthetic_claims_repository",
        checked_at=datetime.now(timezone.utc).isoformat(),
    )