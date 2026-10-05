import hashlib
import json
import sys
from pathlib import Path

from app.policy_schemas import PolicyDocument


DATASET_DIRECTORY = Path("data/policies/v1.0.0")
MANIFEST_PATH = DATASET_DIRECTORY / "manifest.json"

REQUIRED_SECTIONS = {
    "purpose",
    "coverage-criteria",
    "required-documentation",
    "limitations",
    "decision-boundary",
}


def calculate_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    errors = []

    manifest = json.loads(
        MANIFEST_PATH.read_text(encoding="utf-8")
    )

    policy_files = sorted(
        DATASET_DIRECTORY.glob("POL-*.json")
    )

    if len(policy_files) != 10:
        errors.append(
            f"Expected 10 policies, found {len(policy_files)}"
        )

    policy_ids = set()

    for policy_path in policy_files:
        try:
            raw_policy = json.loads(
                policy_path.read_text(encoding="utf-8")
            )
            policy = PolicyDocument.model_validate(raw_policy)
        except Exception as exc:
            errors.append(f"{policy_path.name}: {exc}")
            continue

        if policy.policy_id in policy_ids:
            errors.append(
                f"Duplicate policy ID: {policy.policy_id}"
            )

        policy_ids.add(policy.policy_id)

        if policy.dataset_version != manifest["dataset_version"]:
            errors.append(
                f"{policy.policy_id}: dataset version mismatch"
            )

        section_ids = {
            section.section_id
            for section in policy.sections
        }

        missing_sections = REQUIRED_SECTIONS - section_ids

        if missing_sections:
            errors.append(
                f"{policy.policy_id}: missing sections "
                f"{sorted(missing_sections)}"
            )

        if policy.policy_type != "synthetic":
            errors.append(
                f"{policy.policy_id}: policy is not synthetic"
            )

        if policy.human_review_required is not True:
            errors.append(
                f"{policy.policy_id}: human review must be required"
            )

        if policy.authorization_decision_supported is not False:
            errors.append(
                f"{policy.policy_id}: autonomous decisions cannot be supported"
            )

    manifest_entries = {
        entry["policy_id"]: entry
        for entry in manifest["policies"]
    }

    for policy_path in policy_files:
        policy_id = policy_path.stem
        entry = manifest_entries.get(policy_id)

        if entry is None:
            errors.append(
                f"{policy_id}: missing manifest entry"
            )
            continue

        actual_hash = calculate_sha256(policy_path)

        if actual_hash != entry["sha256"]:
            errors.append(
                f"{policy_id}: SHA-256 checksum mismatch"
            )

    if errors:
        print("Dataset validation failed:")

        for error in errors:
            print(f"- {error}")

        sys.exit(1)

    print("Dataset validation passed")
    print(f"Policies validated: {len(policy_files)}")
    print(f"Dataset version: {manifest['dataset_version']}")
    print("Real PHI: false")
    print("Autonomous authorization: false")


if __name__ == "__main__":
    main()