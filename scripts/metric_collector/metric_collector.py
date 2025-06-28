import os
from pathlib import Path
import sys
import subprocess
import pandas as pd
from tabulate import tabulate
import plotly.express as px
import json

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


def get_namespaces():
    namespaces = subprocess.run(["kubectl", "get", "namespaces", "-o", "name"], capture_output=True, text=True, check=True)
    all_namespaces = [line.replace("namespace/", "") for line in namespaces.stdout.strip().splitlines()]
    return all_namespaces


def get_nodes():
    nodes = subprocess.run(["kubectl", "get", "nodes", "-o", "name"], capture_output=True, text=True, check=True)
    all_nodes = [line.replace("node/", "") for line in nodes.stdout.strip().splitlines()]
    return all_nodes


def collect_metrics__pods(namespaces):
    pods_dir = metrics_dir / "pods"
    pods_dir.mkdir(exist_ok=True)
    print("Recolectando métricas de todos los pods...")
    for names in namespaces:
        with open(pods_dir / f"{names}_metrics.csv", "a", encoding="utf-8") as pod_metrics_file:
            try:
                metrics_result = subprocess.run(
                    ["kubectl", "top", "pods", "-n", names],
                    capture_output=True, text=True, check=True
                )
                pod_metrics_file.write(metrics_result.stdout)
                lines = metrics_result.stdout.strip().split("\n")
                if len(lines) > 1:
                    headers = lines[0].split()
                    metrics = []

                    for line in lines[1:]:
                        values = line.split()
                        metrics.append(dict(zip(headers, values)))

                    json_path = pods_dir / f"{names}_metrics.json"
                    with open(json_path, "w", encoding="utf-8") as jf:
                        json.dump(metrics, jf, indent=2)
            except subprocess.CalledProcessError as e:
                print(f"Error al obtener métricas de los pods en el namespace {names}: {e.stderr}")
    path = metrics_dir / "pods"
    archivos = os.listdir(path)
    print(f"Recolección de métricas de pods completada y guardados en: {archivos}")
    print("=========================================================")


def collect_metrics__nodes(nodes):
    nodes_dir = metrics_dir / "nodes"
    nodes_dir.mkdir(exist_ok=True)
    print("Recolectando métricas de todos los nodos...")
    for node in nodes:
        with open(nodes_dir / f"{node}_metrics.csv", "a", encoding="utf-8") as node_metrics_file:
            try:
                metrics_result = subprocess.run(
                    ["kubectl", "top", "nodes"],
                    capture_output=True, text=True, check=True
                )
                node_metrics_file.write(metrics_result.stdout)
                lines = metrics_result.stdout.strip().split("\n")
                if len(lines) > 1:
                    headers = lines[0].split()
                    metrics = []

                    for line in lines[1:]:
                        values = line.split()
                        metrics.append(dict(zip(headers, values)))

                    json_path = nodes_dir / f"{node}_metrics.json"
                    with open(json_path, "w", encoding="utf-8") as jf:
                        json.dump(metrics, jf, indent=2)
            except subprocess.CalledProcessError as e:
                print(f"Error al obtener métricas del nodo {node}: {e.stderr}")
    path = metrics_dir / "nodes"
    archivos = os.listdir(path)
    print(f"Recolección de métricas de pods completada y guardados en: {archivos}")
    print("=========================================================")


def main():
    nodes = get_nodes()
    if not nodes:
        print("No se encontraron nodos.")
    else:
        print(f"Nodos encontrados: {', '.join(nodes)}")
        print("=========================================================")
        name = get_namespaces()
        if not name:
            print("No se encontraron namespaces.")
        else:
            print(f"Namespaces encontrados: {', '.join(name)}")
            print("=========================================================")
            collect_metrics__pods(name)
            collect_metrics__nodes(nodes)


if __name__ == "__main__":
    main()
