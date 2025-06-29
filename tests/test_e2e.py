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
