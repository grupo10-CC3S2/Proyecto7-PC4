from unittest.mock import patch, MagicMock
from scripts.metric_collector import metric_visualizer

def test_metric_dirs(run_metric_collector):
    metrics_dir = run_metric_collector
    assert metrics_dir.exists(), "El directorio principal de métricas no fue creado."
    pods_dir = metrics_dir / "pods"
    nodes_dir = metrics_dir / "nodes"
    assert pods_dir.exists(), "El directorio de métricas de pods no fue creado."
    assert nodes_dir.exists(), "El directorio de métricas de nodos no fue creado."


def test_metric_files(run_metric_collector):
    metrics_dir = run_metric_collector

    csv_files = list(metrics_dir.rglob("*.csv"))
    json_files = list(metrics_dir.rglob("*.json"))

    assert len(csv_files) > 0, "No se generaron archivos CSV de métricas."
    assert len(json_files) > 0, "No se generaron archivos JSON de métricas."


def test_log_files(run_log_collector):
    logs_dir = run_log_collector
    assert logs_dir.exists(), "El directorio de logs no fue creado."

    main_log_file = logs_dir / "all_pods.log"
    individual_logs = [f for f in logs_dir.glob("*.log") if f.name != "all_pods.log"]

    assert main_log_file.exists(), "El archivo de log principal no fue creado."
    assert len(individual_logs) > 0, "No se crearon logs individuales para los pods."


def test_log_not_empty(run_log_collector):
    main_log_file = run_log_collector / "all_pods.log"

    with open(main_log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"contenido {content}")

    assert len(content) > 0, "El archivo de logs principal está vacío."
    assert "Logs del pod:" in content, "El formato esperado no se encontró en el log."


def test_html_graphs_generated(run_metric_visualizer):
    metrics_dir = run_metric_visualizer
    html_files = list(metrics_dir.rglob("*.html"))
    assert len(html_files) > 0, "No se genero HTML archivo"


def test_html_graphs_not_empty(run_metric_visualizer):
    metrics_dir = run_metric_visualizer
    html_files = list(metrics_dir.rglob("*.html"))

    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) > 0, f"El archivo HTML {html_file} esta vacío."
        assert "<html>" in content, f"El archivo {html_file} no es un HTML valido."

def test_alert_umbral(monkeypatch, capsys, mock_metrics_dir):
    monkeypatch.setattr(metric_visualizer, 'metrics_dir', mock_metrics_dir)
    metric_visualizer.alert_umbral()
    captured = capsys.readouterr()
    assert "15m de CPU" in captured.out
    assert "pod-1" not in captured.out


@patch('subprocess.run')
def test_alert_pods_not_ready(mock_subprocess_run, capsys):
    not_ready_pod_json = '''
    {
        "items": [
            {
                "metadata": {
                    "name": "test-pod-not-ready"
                },
                "status": {
                    "conditions": [
                        {
                            "type": "Ready",
                            "status": "False",
                            "lastTransitionTime": "2025-01-01T12:00:00Z"
                        }
                    ]
                }
            }
        ]
    }
    '''

    ready_pod_json = '''
    {
        "items": [
            {
                "metadata": {
                    "name": "test-pod-ready"
                },
                "status": {
                    "conditions": [
                        {
                            "type": "Ready",
                            "status": "True"
                        }
                    ]
                }
            }
        ]
    }
    '''

    mock_subprocess_run.side_effect = [
        MagicMock(stdout=not_ready_pod_json, check_return_value=None),
        MagicMock(stdout=ready_pod_json, check_return_value=None)
    ]

    namespaces = ["ns1", "ns2"]
    metric_visualizer.alert_pods_not_ready(namespaces)

    captured = capsys.readouterr()
    assert "no está Ready" in captured.out
    assert "test-pod-ready" not in captured.out
