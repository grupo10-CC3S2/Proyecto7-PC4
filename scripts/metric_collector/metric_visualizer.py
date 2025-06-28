import os
from pathlib import Path
import sys
import subprocess
import pandas as pd
from tabulate import tabulate
import plotly.express as px

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


root_dir = find_root_dir("test-repo-pc4")

metrics_dir = root_dir / "metrics"
metrics_dir.mkdir(exist_ok=True)


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


def main():
    visualize_metrics_console()


if __name__ == "__main__":
    main()
