# Proyecto7-PC4
# Observabilidad de clúster Kubernetes local (mini-monitoring)

## Integrantes:

- Christian Luna
- Diego Osorio
- Alex Vega

## Setup

1. Construir la imagen Docker local:
   ```sh
   docker build -t timeserver:v1 app
   docker build -t timeserver:v2 app
   ```
2. Verificar que Kubernetes esta activado:
   ```sh
   kubectl cluster-info
   ```
    Debe decir:
    ```sh
    Kubernetes control plane is running at https://kubernetes.docker.internal:6443
    CoreDNS is running at https://kubernetes.docker.internal:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

    To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
    ```

3. Desplegar pods:
   ```sh
   kubectl apply -f k8s/
   ```
4. Comprobar que Pods estan corriendo:
   ```sh
   kubectl get pods
   ```
5. Ir a un navegador y abrir:
    ```sh
    http://localhost:80
   ```
Se obtendra el tiempo actual en timezone UTC y Lima.


## Limpieza

Para borrar todo lo creado y liberar recursos:

1. Eliminar recursos en Kubernetes:
   ```sh
   kubectl delete -f k8s/
   ```

2. Eliminar la imagen (esperar unos segundos):
   ```sh
   docker image rm timeserver
   ```