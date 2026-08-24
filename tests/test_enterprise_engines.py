from dbxguard_core.cost import estimate_scaled_compute_cost
from dbxguard_core.drift import detect_drift
from dbxguard_core.security import score_access_exposure


def test_cost_scaling():
    result = estimate_scaled_compute_cost(1000, 4, 8)
    assert result.proposed_monthly == 2000
    assert result.increase_percent == 100


def test_drift():
    findings = detect_drift({"auto_stop_mins": 10}, {"auto_stop_mins": 0, "manual": True})
    assert {f.kind for f in findings} == {"MODIFIED", "UNMANAGED"}


def test_security_exposure():
    exposure = score_access_exposure(8000, 12, "SELECT", broad_group=True)
    assert exposure.score >= 60
