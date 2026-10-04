from datetime import datetime, timezone

from app.schemas import ProviderInformationResult


SYNTHETIC_PROVIDERS = {
    "P-2001": {
        "provider_name": "Northwest Orthopedic Clinic",
        "specialty": "Orthopedic Surgery",
        "network_status": "in_network",
        "active": True,
    },
    "P-2002": {
        "provider_name": "Regional Imaging Associates",
        "specialty": "Diagnostic Radiology",
        "network_status": "out_of_network",
        "active": True,
    },
}


def get_provider_information(
    provider_id: str,
) -> ProviderInformationResult:
    normalized_id = provider_id.strip().upper()
    record = SYNTHETIC_PROVIDERS.get(normalized_id)

    checked_at = datetime.now(timezone.utc).isoformat()

    if record is None:
        return ProviderInformationResult(
            provider_id=normalized_id,
            provider_name=None,
            specialty=None,
            network_status="not_found",
            active=None,
            source="synthetic_provider_directory",
            checked_at=checked_at,
        )

    return ProviderInformationResult(
        provider_id=normalized_id,
        provider_name=record["provider_name"],
        specialty=record["specialty"],
        network_status=record["network_status"],
        active=record["active"],
        source="synthetic_provider_directory",
        checked_at=checked_at,
    )