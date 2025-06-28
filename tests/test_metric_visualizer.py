import pytest
from scripts.metric_collector import metric_collector
from scripts.metric_collector import metric_visualizer


root_dir = metric_visualizer.find_root_dir("Proyecto7-PC4")


def setup_module(module):
    # Se ejecuta una vez antes de cualquier test en este archivo
    print("\n[setup] Ejecutando dependencias...")
    metric_collector.main()  # si aplica
    metric_visualizer.main()  # o alguna función que prepare el entorno


@pytest.mark.xfail(reason="El directorio no existe")
def test_not_fing_root_dir():
    assert metric_visualizer.find_root_dir("non_existent_dir")


def test_find_root_dir():
    root = metric_visualizer.find_root_dir("Proyecto7-PC4")
    assert root.is_dir()


def test_clean_raw_metrics_pods():
    pod_path = root_dir / "metrics" / "pods" / "default_metrics.csv"
    df = metric_visualizer.clean_raw_metrics_pods(pod_path)
    assert not df.empty
    assert "POD" in df.columns
    assert "CPU_cores(m)" in df.columns
    assert "MEM_bytes(Mi)" in df.columns
