from app.routing import select_model_version


def test_explicit_version_override_wins_over_experiment_key():
    decision = select_model_version("v2", "customer-1")

    assert decision.model_version == "v2"
    assert decision.experiment_group == "test"


def test_same_experiment_key_routes_to_same_group():
    first = select_model_version(None, "customer-1")
    second = select_model_version(None, "customer-1")

    assert first == second


def test_ab_split_is_roughly_balanced_for_1000_keys():
    decisions = [select_model_version(None, f"customer-{index}") for index in range(1000)]
    v2_share = sum(decision.model_version == "v2" for decision in decisions) / len(decisions)

    assert 0.45 <= v2_share <= 0.55


def test_default_route_uses_v1():
    decision = select_model_version(None, None)

    assert decision.model_version == "v1"
    assert decision.experiment_group == "default_control"
