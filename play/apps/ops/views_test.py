def test_ready(client):
    response = client.get("/healthz/ready")
    assert response.status_code == 200


def test_alive(client):
    response = client.get("/healthz/alive")
    assert response.status_code == 200
