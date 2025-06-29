def test_deployment_available(timeserver_deployment):
    status = timeserver_deployment.status
    spec = timeserver_deployment.spec

    assert status.available_replicas == spec.replicas, \
        f"El numero de replicas disponibles ({status.available_replicas}) no coincide con el deseado ({spec.replicas})."

    assert status.ready_replicas == spec.replicas, \
        f"El numero de replicas listas ({status.ready_replicas}) no coincide con el deseado ({spec.replicas})."


def test_service_exists(timeserver_service, resource_names):
    assert timeserver_service is not None
    assert timeserver_service.metadata.name == resource_names["service"]


def test_pods_running(timeserver_pods, resource_names):
    assert timeserver_pods is not None, "No se encontraron pods."

    assert len(timeserver_pods) == 3

    for pod in timeserver_pods:
        assert pod.status.phase == "Running", f"El pod {pod.metadata.name} no esta en estado 'Running'."
