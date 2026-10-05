import json
from pathlib import Path

from app.policy_schemas import PolicyDocument


DATASET_DIRECTORY = Path("data/policies/v1.0.0")


def load_policies() -> list[PolicyDocument]:
    policies = []

    for path in sorted(DATASET_DIRECTORY.glob("POL-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        policies.append(PolicyDocument.model_validate(data))

    return policies


def test_dataset_contains_ten_policies():
    assert len(load_policies()) == 10


def test_policy_ids_are_unique():
    policies = load_policies()
    policy_ids = [policy.policy_id for policy in policies]

    assert len(policy_ids) == len(set(policy_ids))


def test_all_policies_are_synthetic():
    for policy in load_policies():
        assert policy.policy_type == "synthetic"


def test_all_policies_require_human_review():
    for policy in load_policies():
        assert policy.human_review_required is True
        assert policy.authorization_decision_supported is False


def test_every_policy_has_retrievable_sections():
    for policy in load_policies():
        assert len(policy.sections) >= 5

        for section in policy.sections:
            assert section.section_id
            assert section.heading
            assert section.text