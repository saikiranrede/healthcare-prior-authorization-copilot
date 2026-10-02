from datetime import datetime, timezone

from app.schemas import EligibilityResult


SYNTHETIC_MEMBERS = {
    "M-1001": {
        "status": "active",
        "plan_name": "ClearHealth Gold",
        "coverage_start_date": "2026-01-01",
        "coverage_end_date": None,
    },
    "M-1002": {
        "status": "inactive",
        "plan_name": "ClearHealth Silver",
        "coverage_start_date": "2025-01-01",
        "coverage_end_date": "2025-12-31",
    },
}


def check_member_eligibility(member_id: str) -> EligibilityResult:
    normalized_member_id = member_id.strip().upper()
    record = SYNTHETIC_MEMBERS.get(normalized_member_id)

    checked_at = datetime.now(timezone.utc).isoformat()

    if record is None:
        return EligibilityResult(
            member_id=normalized_member_id,
            status="not_found",
            plan_name=None,
            coverage_start_date=None,
            coverage_end_date=None,
            source="synthetic_member_repository",
            checked_at=checked_at,
        )

    return EligibilityResult(
        member_id=normalized_member_id,
        status=record["status"],
        plan_name=record["plan_name"],
        coverage_start_date=record["coverage_start_date"],
        coverage_end_date=record["coverage_end_date"],
        source="synthetic_member_repository",
        checked_at=checked_at,
    )