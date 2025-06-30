import subprocess
import time
import random
import json
import os


class MinimalChaosTest:
    def __init__(self, namespace="default", pod_selector="timeserver-pod"):
        self.namespace = namespace
        self.pod_selector = (
            pod_selector  # Cambio: usar pod_selector en lugar de app_label
        )
        self.alerts = []

        os.makedirs("scripts/chaos_test/reports", exist_ok=True)

    def get_pods(self, verbose=True):
        if verbose:
            print(f"\nObteniendo pods con namespace {self.namespace}")
        try:
            cmd = [
                "kubectl",
                "get",
                "pods",
                "-n",
                self.namespace,
                "-l",
                f"pod={self.pod_selector}",
                "--no-headers",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            pods = []
            for line in result.stdout.strip().splitlines():
                parts = line.split()
                pod_name = parts[0]
                status = parts[2]
                pods.append({"name": pod_name, "status": status})
                if verbose:
                    print(f"   Pod: {pod_name} - Status: {status}")

            return pods
        except subprocess.CalledProcessError as e:
            self.generate_alert(f"ERROR: No se pudieron obtener pods: {e.stderr}")
            return []

    def generate_alert(self, message):
        alert = {"message": message, "type": "chaos_testing_alert"}
        self.alerts.append(alert)
        print(f" ALERTA:\n {message}")
        return alert

    def simulate_pod_deletion(self):
        print("\n" + "=" * 50)
        print(" INICIANDO CHAOS TESTING MINIMAL")
        print("=" * 50)

        pods = self.get_pods()
        running_pods = [p for p in pods if p["status"] == "Running"]

        print(f" Pods encontrados: {len(pods)}")
        print(f" Pods Running: {len(running_pods)}")

        if len(running_pods) < 2:
            self.generate_alert(
                "ERROR: Se necesitan al menos 2 pods Running para chaos testing seguro"
            )
            return None

        victim = random.choice(running_pods)
        victim_name = victim["name"]

        print(f"\n Pod seleccionado para eliminación: {victim_name}")
        self.generate_alert(
            f"CHAOS INICIADO: Pod {victim_name} seleccionado para eliminación"
        )

        try:
            print(f" Eliminando pod {victim_name}...")
            cmd = ["kubectl", "delete", "pod", victim_name, "-n", self.namespace]
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            self.generate_alert(
                f"POD ELIMINADO: {victim_name} ha sido eliminado exitosamente"
            )
            print(f" Pod {victim_name} eliminado")
            return victim_name

        except subprocess.CalledProcessError as e:
            self.generate_alert(
                f"ERROR: Falló eliminación de pod {victim_name}: {e.stderr}"
            )
            return None

    def detect_problem(self, eliminated_pod, monitoring_duration=30):
        print(
            f"\n DETECTANDO PROBLEMA - Monitoreando por {monitoring_duration} segundos"
        )
        print("-" * 50)

        start_time = time.time()
        problem_detected = False
        recovery_started = False
        recovery_complete = False

        initial_pod_count = len(self.get_pods(verbose=False))

        while time.time() - start_time < monitoring_duration:
            current_pods = self.get_pods(verbose=False)
            elapsed_time = int(time.time() - start_time)

            if elapsed_time % 10 == 0 and elapsed_time > 0:
                print(f" Progreso: {elapsed_time}s - {len(current_pods)} pods activos")

            eliminated_found = any(
                pod["name"] == eliminated_pod for pod in current_pods
            )

            if not eliminated_found and not problem_detected:
                self.generate_alert(
                    f"PROBLEMA DETECTADO: Pod {eliminated_pod} ya no existe en el cluster"
                )
                problem_detected = True

            creating_pods = [
                p for p in current_pods if p["status"] == "ContainerCreating"
            ]
            if creating_pods and not recovery_started:
                for pod in creating_pods:
                    self.generate_alert(
                        f"RECUPERACIÓN DETECTADA: Nuevo pod {pod['name']} siendo creado"
                    )
                recovery_started = True

            running_count = len([p for p in current_pods if p["status"] == "Running"])
            if (
                running_count >= initial_pod_count
                and recovery_started
                and not recovery_complete
            ):
                self.generate_alert(
                    f"RECUPERACIÓN COMPLETA: Sistema restaurado con {running_count}/{initial_pod_count} pods Running"
                )
                recovery_complete = True

            time.sleep(1)

        elapsed_time = int(time.time() - start_time)
        print(f" Monitoreo completado: {elapsed_time}s transcurridos")

        if not recovery_started:
            final_pods = self.get_pods(verbose=False)
            final_running = len([p for p in final_pods if p["status"] == "Running"])
            if final_running >= initial_pod_count:
                self.generate_alert(
                    f"RECUPERACIÓN DETECTADA: Sistema con {final_running} pods Running"
                )

        return problem_detected

    def generate_report(self):
        report_file = "scripts/chaos_test/reports/chaos_testing_report.json"

        report = {
            "chaos_test_summary": {
                "namespace": self.namespace,
                "target_selector": f"pod={self.pod_selector}",
                "total_alerts": len(self.alerts),
                "test_completed": True,
            },
            "alerts_generated": self.alerts,
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f" REPORTE GENERADO: {report_file}")
        return report_file


def main():
    print(" CHAOS TESTING MINIMAL")

    chaos = MinimalChaosTest(namespace="default", pod_selector="timeserver-pod")

    eliminated_pod = chaos.simulate_pod_deletion()

    if eliminated_pod:
        chaos.detect_problem(eliminated_pod, monitoring_duration=30)

        report_file = chaos.generate_report()

        print("\n" + "=" * 50)
        print("CHAOS TESTING COMPLETADO")
        print("=" * 50)
        print(f" Total de alertas generadas: {len(chaos.alerts)}")
        print(f" Reporte guardado en: {report_file}")

        print("\n ALERTAS GENERADAS:")
        for i, alert in enumerate(chaos.alerts, 1):
            print(f"{i}. {alert['message']}")

    else:
        print(" Chaos testing falló en la eliminación del pod")


if __name__ == "__main__":
    main()
