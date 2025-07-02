import subprocess
import json
import os


class NetworkPolicyChecker:
    def __init__(self, namespace="default"):
        self.namespace = namespace
        self.alerts = []

        os.makedirs("scripts/security/reports", exist_ok=True)

    def generate_alert(self, message, severity="INFO"):
        alert = {
            "message": message,
            "severity": severity,
            "type": "network_policy_check",
        }
        self.alerts.append(alert)
        print(f"{severity}: {message}")
        return alert

    def check_network_policies(self):
        print("Verificando NetworkPolicies existentes")

        try:
            cmd = [
                "kubectl",
                "get",
                "networkpolicies",
                "-n",
                self.namespace,
                "-o",
                "json",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            policies = json.loads(result.stdout)
            policy_count = len(policies["items"])

            if policy_count == 0:
                self.generate_alert("No se encontraron NetworkPolicies", "WARNING")
                return False
            else:
                self.generate_alert(
                    f"Se encontraron {policy_count} NetworkPolicies", "SUCCESS"
                )

                # Verificar política específica de timeserver
                for policy in policies["items"]:
                    if "timeserver" in policy["metadata"]["name"]:
                        self.generate_alert(
                            f"NetworkPolicy para timeserver encontrada: {policy['metadata']['name']}",
                            "SUCCESS",
                        )
                        return True

                self.generate_alert(
                    "No se encontró NetworkPolicy específica para timeserver", "WARNING"
                )
                return False

        except subprocess.CalledProcessError as e:
            self.generate_alert(
                f"Error al verificar NetworkPolicies: {e.stderr}", "ERROR"
            )
            return False

    def check_affected_pods(self):
        print("Verificando pods afectados por las politicas de red")

        try:
            cmd = [
                "kubectl",
                "get",
                "pods",
                "-n",
                self.namespace,
                "-l",
                "pod=timeserver-pod",
                "--no-headers",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            pod_lines = result.stdout.strip().splitlines()
            pod_count = len(pod_lines)

            if pod_count > 0:
                self.generate_alert(
                    f"{pod_count} pods timeserver protegidos por NetworkPolicy",
                    "SUCCESS",
                )
                return True
            else:
                self.generate_alert(
                    "No se encontraron pods timeserver para proteger", "WARNING"
                )
                return False

        except subprocess.CalledProcessError as e:
            self.generate_alert(f"Error al verificar pods: {e.stderr}", "ERROR")
            return False

    def generate_report(self):
        report_file = "scripts/security/reports/network_policy_report.json"

        report = {
            "network_policy_check": {
                "namespace": self.namespace,
                "total_alerts": len(self.alerts),
                "check_completed": True,
            },
            "alerts": self.alerts,
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"Reporte generado: {report_file}")
        return report_file


def main():
    print("=" * 50)
    print(" VERIFICACIÓN DE NETWORKPOLICIES")
    print("=" * 50 + "\n")

    checker = NetworkPolicyChecker(namespace="default")

    # Verificar NetworkPolicies
    policies_ok = checker.check_network_policies()

    # Verificar pods afectados
    pods_ok = checker.check_affected_pods()

    checker.generate_report()

    print("\n" + "=" * 50)
    print(" VERIFICACIÓN COMPLETADA")
    print("=" * 50 + "\n")
    print(f"Total alertas: {len(checker.alerts)}")

    success_count = len([a for a in checker.alerts if a["severity"] == "SUCCESS"])
    warning_count = len([a for a in checker.alerts if a["severity"] == "WARNING"])
    error_count = len([a for a in checker.alerts if a["severity"] == "ERROR"])

    print(f"Éxitos: {success_count}")
    print(f" Advertencias: {warning_count}")
    print(f"Errores: {error_count}")


if __name__ == "__main__":
    main()
