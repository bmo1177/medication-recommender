def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json
    assert data["status"] == "ok"
    assert data["symptoms"] == 132
    assert data["diseases"] == 41
    assert data["model"] == "SVC"


def test_pages_render(client):
    for path in ["/", "/about", "/contact", "/developer", "/blog"]:
        r = client.get(path)
        assert r.status_code == 200, path
        assert "Health Center" in r.get_data(as_text=True)


def test_predict_form_ok(client):
    r = client.post(
        "/predict",
        data={"symptoms": "fatigue, weight_loss, restlessness, lethargy"},
    )
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "Predicted disease" in html or "predicted" in html.lower()
    assert "Severity score" in html


def test_predict_empty_returns_message(client):
    r = client.post("/predict", data={"symptoms": ""})
    assert r.status_code == 200
    assert "misspelled" in r.get_data(as_text=True).lower() or "enter" in r.get_data(as_text=True).lower()


def test_predict_unknown_only_no_crash(client):
    r = client.post("/predict", data={"symptoms": "unknown_xyz_123"})
    assert r.status_code == 200
    assert "recognized" in r.get_data(as_text=True).lower()


def test_predict_too_many_rejected(client):
    many = ", ".join(["itching"] * 40)
    r = client.post("/predict", data={"symptoms": many})
    assert r.status_code == 200
    assert "at most" in r.get_data(as_text=True).lower()


def test_index_preserves_user_input(client):
    r = client.post("/predict", data={"symptoms": "unknown_xyz"})
    assert "unknown_xyz" in r.get_data(as_text=True)


def test_api_symptoms(client):
    r = client.get("/api/symptoms")
    assert r.status_code == 200
    assert r.json["count"] == 132
    assert "itching" in r.json["symptoms"]


def test_api_predict_list(client):
    r = client.post(
        "/api/predict",
        json={"symptoms": ["fatigue", "weight_loss", "restlessness", "lethargy"]},
    )
    assert r.status_code == 200
    data = r.json
    assert data["predicted_disease"] == "Diabetes "
    assert 0 <= data["confidence"] <= 1
    assert isinstance(data["severity_score"], int)
    assert data["medications"] and data["precautions"]


def test_api_predict_string(client):
    r = client.post("/api/predict", json={"symptoms": "itching, skin_rash"})
    assert r.status_code == 200
    assert r.json["predicted_disease"]


def test_api_predict_bad_input(client):
    assert client.post("/api/predict", json={}).status_code == 400
    assert client.post("/api/predict", json={"symptoms": 123}).status_code == 400
    r = client.post("/api/predict", json={"symptoms": ["unknown_xyz"]})
    assert r.status_code == 422
    assert "unknown" in r.json
