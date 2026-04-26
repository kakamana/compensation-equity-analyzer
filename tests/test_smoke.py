from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_equity_audit_endpoint():
    r = client.post("/equity_audit", json={})
    assert r.status_code == 200
    body = r.json()
    assert "raw_gap" in body
    assert "explained" in body
    assert "unexplained" in body
    assert "by_role" in body
    assert "recommendations" in body
    assert "decision_aid_disclaimer" in body


def test_synthetic_data_shape():
    from comp_equity.data import make_org_frame

    df = make_org_frame()
    assert len(df) == 5_000
    expected = {
        "emp_id", "age", "tenure_yrs", "education_level", "role", "level",
        "dept", "gender", "nationality_group", "monthly_comp_aed",
        "performance_rating",
    }
    assert expected.issubset(set(df.columns))
    assert df["monthly_comp_aed"].min() > 0
    assert set(df["gender"].unique()) <= {"M", "F"}


def test_decomposition_recovers_signed_gap():
    from comp_equity.data import make_org_frame
    from comp_equity.models import threefold_decomposition

    df = make_org_frame()
    d = threefold_decomposition(df)
    # F is paid less by construction, so M − F gap is positive in log-comp
    assert d["raw_gap"] > 0
    # E + C + I must reconstruct the raw gap exactly
    assert abs(d["sum_EC_I"] - d["raw_gap"]) < 1e-6
