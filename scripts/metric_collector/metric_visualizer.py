import os
from pathlib import Path
import sys
import subprocess
import pandas as pd
from tabulate import tabulate
import plotly.express as px
import json
from datetime import datetime, UTC
import smtplib
from email.mime.text import MIMEText


# Comandos para obtener métricas de pods y nodes
# 1.- kubectl top pods -n <namespace>
# 2.- kubectl top pods
# 3.- kubectl top nodes


def find_root_dir(target_folder_name):
    '''
    Busca el directorio raíz del proyecto para el nombre de carpeta especificado.
    '''
    current = Path(__file__).resolve()
    while current.name != target_folder_name:
        if current.parent == current:
            raise FileNotFoundError(f"No se encontró el directorio '{target_folder_name}' hacia arriba desde {__file__}")
        current = current.parent
    return current


root_dir = find_root_dir("Proyecto7-PC4")

metrics_dir = root_dir / "metrics"
metrics_dir.mkdir(exist_ok=True)

msg_umbral = []
msg_ready = []


def get_namespaces():
    namespaces = subprocess.run(
        ["kubectl", "get", "namespaces", "-o", "name"],
        capture_output=True,
        text=True,
        check=True,
    )
    all_namespaces = [
        line.replace("namespace/", "")
        for line in namespaces.stdout.strip().splitlines()
    ]
    return all_namespaces


# Visualización de métricas
def clean_raw_metrics_pods(pod_path):
    df = pd.read_csv(pod_path, sep=r'\s+')
    df.columns = ["POD", "CPU_cores(m)", "MEM_bytes(Mi)"]
    df["CPU_cores(m)"] = df["CPU_cores(m)"].str.replace("m", "", regex=False).astype(int)
    df["MEM_bytes(Mi)"] = df["MEM_bytes(Mi)"].str.replace("Mi", "", regex=False).astype(int)

    return df


def clean_raw_metrics_nodes(node_path):
    df = pd.read_csv(node_path, sep=r'\s+')

    df.columns = ["NODE", "CPU_cores(m)", "CPU_%", "MEM_bytes(Mi)", "MEM_%"]

    df["CPU_cores(m)"] = df["CPU_cores(m)"].str.replace("m", "", regex=False).astype(str)
    df["CPU_%"] = df["CPU_%"].str.replace("%", "", regex=False).astype(str)
    df["MEM_bytes(Mi)"] = df["MEM_bytes(Mi)"].str.replace("Mi", "", regex=False).astype(str)
    df["MEM_%"] = df["MEM_%"].str.replace("%", "", regex=False).astype(str)

    return df


def show_console_table(df, name):
    print(f"\n=== Tabla resumida de métricas de {name} ===")
    print(tabulate(df, headers='keys', tablefmt='fancy_grid'))


# Ingresar pods or nodes
def visualize_metrics_console():
    path = metrics_dir
    folders = os.listdir(path)
    for folder in folders:
        files_path = path / folder
        archivos = os.listdir(files_path)
        for file in archivos:
            if not file.endswith(".csv"):
                continue
            else:
                if folder == "pods":
                    with open(files_path / file, "r", encoding="utf-8") as f:
                        read = f.read()
                    if not read:
                        print(f"Las métricas de {file} no están disponibles.")
                    else:
                        df = clean_raw_metrics_pods(files_path / file)
                        show_console_table(df, file)
                        generate_html_graph_pods(df, files_path / f"{file.split('.')[0]}.html", f"{file.split('.')[0]}.html")
                elif folder == "nodes":
                    with open(files_path / file, "r", encoding="utf-8") as f:
                        read = f.read()
                    if not read:
                        print(f"Las métricas de {file} no están disponibles.")
                    else:
                        df = clean_raw_metrics_nodes(files_path / file)
                        show_console_table(df, file)
                        generate_html_graph_nodes(df, files_path / f"{file.split('.')[0]}.html", f"{file.split('.')[0]}.html")


def generate_html_graph_pods(df, output_path, name):
    df_long = df.melt(id_vars="POD", value_vars=["CPU_cores(m)", "MEM_bytes(Mi)"], var_name="Recurso", value_name="Valor")

    df_long["Recurso"] = df_long["Recurso"].replace({
        "CPU_cores(m)": "CPU (m)",
        "MEM_bytes(Mi)": "Memoria (Mi)"
    })

    fig = px.bar(df_long, y="POD", x="Valor", color="Recurso", barmode="group", orientation="h", title="Uso de CPU y Memoria por Pod")
    fig.update_traces(texttemplate='%{x}', textposition='outside')
    fig.write_html(output_path)
    print(f"\nGráfico HTML guardado en: {name}")


def generate_html_graph_nodes(df, output_path, name):
    df["CPU_cores(m)"] = df["CPU_cores(m)"].astype(float)
    df["CPU_%"] = df["CPU_%"].astype(float)
    df["MEM_bytes(Mi)"] = df["MEM_bytes(Mi)"].astype(float)
    df["MEM_%"] = df["MEM_%"].astype(float)

    df_long = df.melt(
        id_vars="NODE",
        value_vars=["CPU_cores(m)", "CPU_%", "MEM_bytes(Mi)", "MEM_%"],
        var_name="Recurso",
        value_name="Valor"
    )

    df_long["Recurso"] = df_long["Recurso"].replace({
        "CPU_cores(m)": "CPU (m)",
        "CPU_%": "CPU (%)",
        "MEM_bytes(Mi)": "Memoria (Mi)",
        "MEM_%": "Memoria (%)"
    })

    fig = px.bar(df_long, y="NODE", x="Valor", color="Recurso", barmode="group", orientation="h", title="Uso de Recursos por Nodo (CPU y Memoria)")

    fig.update_traces(texttemplate='%{x}', textposition='outside')
    fig.write_html(output_path)
    print(f"\nGráfico HTML guardado en: {name}")


def check_umbral(path, kind):
    df = pd.read_csv(path, sep=r'\s+')

    umbral_cpu = 10

    def convertir_cpu(cpu_str):
        if isinstance(cpu_str, str) and cpu_str.endswith("m"):
            return int(cpu_str[:-1])
        return 0

    df['CPU_m'] = df['CPU(cores)'].apply(convertir_cpu)

    for index, row in df.iterrows():
        if row['CPU_m'] > umbral_cpu:
            # print(f"Alerta: El {kind} {row['NAME']} está usando {row['CPU_m']}m de CPU (>{umbral_cpu}m)")
            msg_umbral = f"Alerta: El {kind} {row['NAME']} está usando {row['CPU_m']}m de CPU (>{umbral_cpu}m)"
            print(msg_umbral)
            return msg_umbral


def alert_umbral():
    path = metrics_dir
    folders = os.listdir(path)
    for folder in folders:
        files_path = path / folder
        files = os.listdir(files_path)
        for file in files:
            if file.endswith(".csv"):
                with open(files_path / file, "r", encoding="utf-8") as f:
                    read = f.read()
                if read:
                    msg_umbral.append(check_umbral(files_path / file, kind=folder))
    # print(msg)


def send_email():
    port = 587
    smtp_server = "smtp.gmail.com"
    login = "christiangiovannixd2@gmail.com"
    password = "wvns xury dfrj fwnz"

    sender_email = login
    receiver_email = ["christiangiovannixd@gmail.com", "christian.luna.j@uni.pe", "azvegab@gmail.com", "jesus.osorio.t@uni.pe"]
    # "christiangiovannixd@gmail.com", "christian.luna.j@uni.pe", "azvegab@gmail.com", "jesus.osorio.t@uni.pe"
    # receiver_email = "christiangiovannixd@gmail.com"
    # Plain text content
    # text = """\
    # Text de prueba
    # """
    text = "Alertas reportadas en el Proyecto 7 - PC4:\n\n"
    if not msg_umbral:
        text = text + "Ningun pod supera el umbral de CPU.\n"
    else:
        text1 = "Alertas de pods que superan el umbral de CPU:\n"
        text2 = "\n".join(m for m in msg_umbral if m is not None) if msg_umbral else "No se generaron alertas."
        text3 = "\n=======================================================\n"
        text = text + text1 + text2 + text3
    if not msg_ready:
        text = text + "Ningun pod no está listo.\n"
    else:
        text4 = "Alertas de pods no listos:\n\n"
        text5 = "\n".join(m for m in msg_ready if m is not None) if msg_ready else "Todos los pods están listos."
        text = text + text4 + text5

    # text = text1 + "\n" + text2 + text3 + "\n" + text4 + "\n" + text5
    if not receiver_email:
        print("No se especificó un correo electrónico de destino.")
        return
    else:
        for email in receiver_email:
            if not email:
                print("No se especificó un correo electrónico de destino.")
                return
            else:
                message = MIMEText(text, "plain")
                message["Subject"] = "Notificacion de alertas Proyecto 7 - PC4"
                message["From"] = sender_email
                message["To"] = email

                # Send the email
                with smtplib.SMTP(smtp_server, port) as server:
                    server.starttls()  # Secure the connection
                    server.login(login, password)
                    server.sendmail(sender_email, email, message.as_string())

                print(f'Se envió el correo a {email} con éxito.')


def alert_pods_not_ready(namespaces):
    for ns in namespaces:
        try:
            result = subprocess.run(
                ["kubectl", "get", "pods", "-n", ns, "-o", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            pods_json = json.loads(result.stdout)

            for pod in pods_json["items"]:
                pod_name = pod["metadata"]["name"]
                conditions = pod.get("status", {}).get("conditions", [])
                ready_condition = next((c for c in conditions if c["type"] == "Ready"), None)

                if ready_condition and ready_condition["status"] != "True":
                    # Modificar el status a False para verificar que funciona
                    last_transition = ready_condition.get("lastTransitionTime")
                    if last_transition:
                        dt = datetime.strptime(last_transition, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
                        # print(dt)
                        now = datetime.now(UTC)
                        # print(now)
                        duration = now - dt
                        if duration.total_seconds() > 300:  # > 5 minutos
                            # print(f"Alerta: El pod '{pod_name}' en el namespace '{ns}' no está Ready desde hace más de {round(duration.total_seconds()/60)} minutos.")
                            msg = f"Alerta: El pod '{pod_name}' en el namespace '{ns}' no está Ready desde hace más de {round(duration.total_seconds() / 60)} minutos."
                            msg_ready.append(msg)
                            print(msg)
                        else:
                            print(f"El pod '{pod_name}' en el namespace '{ns}' no está Ready (desde {last_transition})")
                    else:
                        print(f"El pod '{pod_name}' en el namespace '{ns}' no está Ready (sin timestamp)")
        except subprocess.CalledProcessError as e:
            print(f"Error al obtener estado de pods en el namespace {ns}: {e.stderr}")
    # print(msg_ready)


def main():
    visualize_metrics_console()
    alert_umbral()
    alert_pods_not_ready(get_namespaces())
    send_email()


if __name__ == "__main__":
    main()
