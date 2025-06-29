import requests
import pytest
import time


def test_health_ok(app_service_url: str):
    health_check_url = f"{app_service_url}/health"
    try:
        response = requests.get(health_check_url, timeout=5)
        response.raise_for_status()

        assert response.json() == {"status": "ok"}, \
            "El cuerpo de la respuesta de /health no es el esperado."

    except requests.exceptions.RequestException as e:
        pytest.fail(f"No se pudo conectar con el endpoint /health. Error: {e}")


def test_content_endpoint(app_service_url: str):
    try:
        response = requests.get(app_service_url, timeout=5)
        response.raise_for_status()

        response_text = response.text
        assert "UTC" in response_text, "La respuesta no contiene la hora en UTC."
        assert "Lima" in response_text, "La respuesta no contiene la hora de Lima."

    except requests.exceptions.RequestException as e:
        pytest.fail(f"No se pudo conectar con el endpoint principal ('/'). Error: {e}")


def test_health_performance(app_service_url: str):
    health_check_url = f"{app_service_url}/health"

    try:
        start_time = time.time()
        response = requests.get(health_check_url, timeout=5)
        end_time = time.time()

        response.raise_for_status()

        response_time = end_time - start_time

        assert response_time < 1.0, \
            f"El tiempo de respuesta del health check es demasiado alto: {response_time:.2f}s"

    except requests.exceptions.RequestException as e:
        pytest.fail(f"No se pudo conectar con el endpoint /health. Error: {e}")
