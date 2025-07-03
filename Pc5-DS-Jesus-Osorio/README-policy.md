# Network Policy

Esta NetworkPolicy implementa controles de red básicos para proteger los pods del timeserver en Kubernetes, que establece reglas de firewall a cada pod.

## Funcionalidad

- Se aplica a pods con etiqueta `pod = timeserver-pod`.
- Activo en namespace `default`.
- En el tráfico de entrada permite conexiones desde cualquier origen, solo en puerto 80, protocolo TCP.
- En el tráfico de salida permite todas las conexiones salientes y no tiene restricciones de destino o puerto.

## Como usar

1. Para aplicar la política
    ```sh
    kubectl apply -f k8s/network-policy.yaml
    ```

2. Verificar aplicación
    ```sh
    kubectl get networkpolicies -n default
    kubectl describe networkpolicy timeserver-network-policy
    ```

3. Probamos conectividad, para esto debemos estar dentro del clúster.
    ```sh
    # Creamos el pod temporal con shell
    kubectl run curl-test --image=curlimages/curl -it --rm -- sh

    # Probamos la conexión
    curl http://timeserver:80

    exit
    ```
