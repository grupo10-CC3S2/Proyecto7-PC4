import os
import subprocess
import sys

namespace = sys.argv[1] if len(sys.argv) > 1 else "default"

os.makedirs("logs", exist_ok=True)


def get_pods(namespace="default"):
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", namespace, "-o", "name"],
            capture_output=True, text=True, check=True
        )
        pods = [line.replace("pod/", "") for line in result.stdout.strip().splitlines()]
        return pods
    except subprocess.CalledProcessError as e:
        print(f"Error al obtener los pods: {e.stderr}")
        sys.exit(1)


def collect_logs(pods, namespace="default"):
    for pod in pods:
        print(f"Recolectando logds del pod: {pod}")
        with open("logs/all_pods.log", "a", encoding="utf-8") as all_log_file:
            all_log_file.write(f"=================== Logs del pod: {pod} ===================\n")

            try:
                log_result = subprocess.run(
                    ["kubectl", "logs", pod, "-n", namespace],
                    capture_output=True, text=True, check=True
                )

                name_pod = pod.replace("timeserver-7c9445b569-", "")
                pod_log_path = f"logs/{name_pod}.log"

                with open(pod_log_path, "a", encoding="utf-8") as pod_log_file:
                    pod_log_file.write(log_result.stdout)
                all_log_file.write(log_result.stdout)
                all_log_file.write(f"====== Recolección de logs del pod {pod} completada ======\n")
                all_log_file.write("----------------------------------------------------------\n")

                print(f"Logs del pod {pod} guardados en {pod_log_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error al obtener los logs del pod {pod}: {e.stderr}")


def get_events(namespace="default"):
    print("Recolección de eventos del cluster:")
    with open("logs/all_events.log", "a", encoding="utf-8") as all_log_file:
        all_log_file.write("=============== Eventos del cluster ===============\n")
        try:
            events_result = subprocess.run(
                ["kubectl", "get", "events", "-n", namespace],
                capture_output=True, text=True, check=True
            )
            all_log_file.write(events_result.stdout)
            print("Eventos del clúster guardados en log/all_events.log")
        except subprocess.CalledProcessError as e:
            print(f"Error al obtener los eventos: {e.stderr}")


if __name__ == "__main__":
    pods = get_pods(namespace)
    if not pods:
        print(f"No se encontraron pods en el namespace '{namespace}'.")
        sys.exit(0)

    collect_logs(pods, namespace)
    get_events(namespace)

    print("Recolección de logs y eventos completada.")
    print("Los logs se han guardado en el directorio 'logs'.")
