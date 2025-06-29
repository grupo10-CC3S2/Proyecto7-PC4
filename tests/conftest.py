import pytest
from kubernetes import config, client

NAMESPACE = "default"
DEPLOYMENT_NAME = "timeserver"
SERVICE_NAME = "timeserver"
POD_LABEL_SELECTOR = "pod=timeserver-pod"


@pytest.fixture(scope="session")
def resource_names():
    return {
        "namespace": NAMESPACE,
        "deployment": DEPLOYMENT_NAME,
        "service": SERVICE_NAME,
        "pod_label_selector": POD_LABEL_SELECTOR
    }


@pytest.fixture(scope="session")
def app_service_url():
    return "http://localhost:80"


@pytest.fixture(scope="session")
def kube_api_client():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()
    return client.AppsV1Api()


@pytest.fixture(scope="session")
def kube_core_api_client():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()
    return client.CoreV1Api()


@pytest.fixture(scope="module")
def timeserver_deployment(kube_api_client: client.AppsV1Api):
    try:
        return kube_api_client.read_namespaced_deployment(
            name=DEPLOYMENT_NAME, namespace=NAMESPACE
        )
    except Exception as e:
        pytest.fail(f"Fallo al obtener el Deployment '{DEPLOYMENT_NAME}'. Error: {e}")


@pytest.fixture(scope="module")
def timeserver_service(kube_core_api_client: client.CoreV1Api):
    try:
        return kube_core_api_client.read_namespaced_service(
            name=SERVICE_NAME, namespace=NAMESPACE
        )
    except Exception as e:
        pytest.fail(f"Fallo al encontrar el Service '{SERVICE_NAME}'. Error: {e}")

@pytest.fixture(scope="module")
def timeserver_pods(kube_core_api_client: client.CoreV1Api):
    try:
        pods = kube_core_api_client.list_namespaced_pod(
            namespace=NAMESPACE, label_selector=POD_LABEL_SELECTOR
        )
        return pods.items
    except Exception as e:
        pytest.fail(f"Fallo al listar los pods. Error: {e}")
