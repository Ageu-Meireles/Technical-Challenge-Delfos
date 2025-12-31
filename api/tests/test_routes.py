from datetime import datetime

from fastapi.testclient import TestClient

from src.db.models import Data


class TestRoutes:
    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_start_after_end(self, client: TestClient):
        response = client.get(
            "/data",
            params={
                "start": "2025-01-02T10:00:00",
                "end": "2025-01-02T09:00:00",
            },
        )
        assert response.status_code == 400

    def test_invalid_variable(self, client: TestClient):
        response = client.get(
            "/data",
            params={
                "start": "2025-01-02T00:00:00",
                "end": "2025-01-02T01:00:00",
                "variables": ["invalid_var"],
            },
        )
        assert response.status_code == 422

    def test_response_structure(self, client: TestClient, mixer):
        mixer.blend(
            Data, timestamp=datetime(2025, 1, 2, 0, 0, 0), wind_speed=5.0
        )
        response = client.get(
            "/data",
            params={
                "start": "2025-01-02T00:00:00",
                "end": "2025-01-02T00:10:00",
                "variables": ["wind_speed"],
            },
        )

        data = response.json()
        assert isinstance(data, list)
        assert "timestamp" in data[0]
        assert "wind_speed" in data[0]
        assert data[0]["wind_speed"] == 5.0
        assert data[0]["timestamp"] == "2025-01-02T00:00:00"
        assert len(data) == 1
