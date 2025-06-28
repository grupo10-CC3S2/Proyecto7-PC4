import pytest
import subprocess
from scripts.log_collector.log_collector import get_pods, collect_logs, get_events

namespace = "default"

namespace2 = "inexsitent_pods"


def test_get_existent_logs():
    pods = get_pods(namespace)
    assert len(pods) > 0
    assert isinstance(pods, list)
    assert pods is not None


@pytest.mark.skip(reason="No hay pods disponibles en el namespace indicado")
def test_get_inexistent_pods():
    pods = get_pods(namespace)
    assert pods is not None
    assert isinstance(pods, list)
    assert len(pods) > 0, "No se encontraron pods en el namespace especificado"


@pytest.mark.xfail(reason="Algún pod no está disponible")
def test_collect_logs_xfail_and_fail():
    pods = get_pods(namespace2)
    if not pods:
        pytest.xfail("No hay pods disponibles en el namespace indicado")

    collect_logs(pods[0], namespace=namespace2)
    subprocess.run(
        ["rm", "-r", "logs"],
        capture_output=True, text=True, check=True
    )


@pytest.mark.xfail(reason="Algún pod no está disponible")
def test_collect_logs_xfail_not_fail():
    pods = get_pods(namespace)
    if not pods:
        pytest.xfail("No hay pods disponibles en el namespace indicado")

    collect_logs(pods[0], namespace=namespace2)
    subprocess.run(
        ["rm", "-r", "logs"],
        capture_output=True, text=True, check=True
    )
