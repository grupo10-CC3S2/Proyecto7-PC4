# Visualización de métricas

## Instalar metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml


En caso ejecutemos la línea "kubectl top pods -n default" que indique algo como `API no disponible` lo que haremos será

### 1.- kubectl get pods -n kube-system

Y verificar que existe un pods llamado metric-server-<numero>-<codigo>

Si verificamos eso, guardamos el nombre del pods, y editaremos su archivo

```bash
kubectl edit deployment metrics-server -n kube-system
```
Esto nos abrirá un editor, y cuando haga esto, buscamos lo siguiente:
```bash
containers:
    - args:
        - --cert-dir=/tmp
        - --secure-port=10250
        - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
        - --kubelet-use-node-status-port
        - --metric-resolution=15s
```
Cuando encontremos eso, lo que haremos será agregar la siguiente línea
```bash
        - --kubelet-insecure-tls
```
**Ojo** Tener cuidado con los espacios

Luego guardamos el editor, cerramos el archivo
### Mal
En caso hayamos editado mal nos aparecerá algo así cuando guardemos el archivo
```bash
error: deployments.apps "metrics-server" is invalid
```
Y nos abrirá otro editor

### Bien
En caso haberlo hecho bien, nos aparecerá este mensaje
```bash
deployment.apps/metrics-server edited
```

Ahora con esto, ya podemos ejecutar el comando

```bash
kubectl top pods -d default
```

Y nos mostrará el uso de Memory y CPU de los pods que existen en el namespace `default`

Así que para la realización de obtención de métricas con `kubectl top` existen 3 formas:
```bash
##Comandos para obtener métricas de pods y nodes
# Métricas de los pods en un namespace en específico
kubectl top pods -n <namespace>

# Métricas de los pods en el namespace por defecto
kubectl top pods

# Métricas de los nodes
kubectl top nodes
```

# metric_visualizer.py
## Vista general
El script de `metric_visualizar.py` se encarga de generar archivos `.csv` donde guardará las métricas obtenidas mediante alguno de los comando anterior según el tipo de elemento que usemos, y de acuerdo a este archivo se encargará de:
- Realizar una visualización simple y ordenada de los datos en la consola mediante el uso de tablas
- Crear archivos `html` para la visualización mediante gráficos de barras

## Función collect_metrics
En el archivo `metric_visualizer.py` existen dos funciones de este tipo, uno para los pods `collect_metrics_pods` y otra para los nodos `collect_metric_nodes` esto lo realicé debido a que no se usa el mismo comando para ambos y preferí mantener un orden con la creación de archivos `csv` en vez de crear un `collect_metric_general` que ejecute ambos, así que estas funciones harán lo siguiente:
> collect_metrics_pods(namespaces)
- Esta función se encargará de revisar todos los `namespace` disponibles en el lista que solicita como argumento, de acuerdo a ello ejecutará el comando `kubectl top pods -d <namespace>` y guardará el resultado en el archivo `<namespace>.csv`, el csv lo creé para que luego sea posible leerlo con la libreria pandas, y de acuerdo a esto, realizar su gráfico de barras

> collect_metrics_pods(nodes)
- La función necesitará como argumento, una lista de los nodos disponibles, siendo esta verificación la principal ya que si no hay nodos, no existirá algún pod en el sistema, por lo que al asignarle el nombre del nodo, este ejecutará el comando `kubectl top nodes` y el resultado lo guardará en `<node>.csv`

## Función clean_raw_metrics 
Esta función se encargará de leer el archivo `csv` creado y de acuerdo a esto, con la libreria pandas, lo separará en columnas con el nombre que posee cada columna en el resultado del comando , para así manejar los datos como un DataFrame facilitando su limpieza y visualización posterior

## Función show_console_table
El objetivo de esta función es para cumplir con el primer requisito de la rúbrica para esta tarea, la cuál es de mostrar los datos en la consola pero de manera ordenada y simple, así que con la libreria tabulate, lo que realicé fue mostrar todos los datos de manera tabulada en la pantalla, haciendo que sea más entendible y fácil de leer al momento de ejecutar el script

## Funcion generate_html_graph
Esta función termina de cumplir el último objetivo de la tarea, la cuál es generar un archivo `html` donde sea posible su visualización, en un primer momento lo quise realizar de manera vertical, pero luego como hay una gran diferencia entre los datos de las columnas, había perdida de datos o mejor dicho, no se podía ver correctamente algunas barras, así que para esta función lo que hice fue que los gráficos de barras se muestren de manera horizontal, ya que así tendrá más tamaño y podrá verse el gráfico correctamente con todas las columnas que presentan los archivos `csv`

# Ejecución

La forma de ejecutar es primero correr el programa `metric_collector.py` y luego `metric_visualizer.py` ya que el último script lee los archvos que se crearon con  `metric_collector.py`