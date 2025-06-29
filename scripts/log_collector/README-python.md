# Script python que recolecta todos los logs de los Pods en un namespace específico

Teniendo ya definido lo que es un namespace, y previamente implementado el `log_collector.sh`, lo que ahora hacemos es que con el objetivo de poder realizar pruebas unitarias a nuestro script, nos vemos en la necesidad de crear un archivo python que tenga la misma funcionalidad que `log_collector.sh` pero este archivo estará escrito en python, por lo que empezaremos con la explicación del código, cabe recalcar que seré más breve porque algunos conceptos como los comando a aplicar, ya se explicaron en [README-bash.md](README-bash.md)

## Explicación del código
Empezamos con manera de ejecutar el script python, ya que al igual que en el de bash, podiamos hacer `bash log_collector.sh` o `bash log_collector.sh default` y con ambos comandos, ejecutabamos el script bash con el namespace default por defecto, así que para poner esta forma de ejecutar el script, hacemos uso del siguiente comando:
```python
namespace = sys.argv[1] if len(sys.argv) > 1 else "default"
``` 
Con esto, tomamos el argumento que se indica al momento de ejecutar el script, y en caso no haya argumento, se tomará por defecto, el namespace `default`
#### Forma de ejecución
```bash
# Sin argumento
python log_collector.py

# Con argumento
python log_collector.py default
```

Y como sabemos que todo se iba a guardar en la carpeta logs, con el siguiente comando hacemos que se cree en caso no exista y nos aseguramos de que se presente algún error
```bash
mkdir -p logs

```
```python
os.makedirs("logs", exist_ok=True)
```
En ambos casos, es la manera que se indica para crear la carpeta `logs`

## Adapando la estructura del código para usarlo con pytest
A diferencia del script `log_collector.sh` para el archivo `log_collector.py` lo que haremos será crear funciones, las cuales serán las siguientes `get_pods` (Encargada de obtener todos los pods según el namespace y retornar estos pods como una lista para poder guardarlos en una variable al momento de su llamado), `collect_logs` (Encargada de obtener los logs de cada pod y en primera guardarlas en su respectivo archivo `.log` y en segunda, guardar todos los logs, en un archivo general que se llama `all_pods.log`) y por último la función `get_events` (Encargada de obtener todos los eventos ocurridos en un namespace específico y guardarlas en el archivo `all_events.log`) y con estas funciones, se facilita el uso de pytest ya que al crear el archivo [test_collector_log.py](..\tests\test_collector_log.py) donde importamos las funciones y de acuerdo a eso se crearán las pruebas.


## Funciones

### Get_pods(namespace="default")
Esta función tiene la opción de recibir un argumento llamado `namespace` pero en caso al momento de llamarla, no se le asigne argumento alguno, por defecto tomará a `namespace` como `default`
En un primer momento, lo que se hará será verificar que hayan pods existentes en el namespace dado al momento de ejecutar el comando `kubectl get pods -n namespace -o name`, y en caso no hayan pods en ese namespace, nos botará un error el cual nos dará como respuesta el siguiente mensaje `Error al obtener los pods`
Tomando el caso donde no hay error al ejecutar el comando, lo que haremos será eliminar la palabra `pod/` que aparece en el resultado del comando, para que solo nos aparezca el nombre en si del pod (la palabra correcta no sería eliminar tecnicamente, lo que hacemos es que con el comando `replace("pod/", "")` lo que hacemos es reemplazar el string `pods/` con un string vacío, así que formalmente es reemplazar el string por uno vacío pero creo que también sería válido decir eliminar ese string), luego de eso, lo que se hace es guardar el nombre de **todos** los pods obtenidos luego del ajuste de su nombre en una variable `pods`, para luego esa variable, retornarla como resultado de invocar la función **get_pods** y hacemos esto para luego invocar la función **collect_logs** el cuál necesita como argumento, un namespace (opcional) y el nombre de los pods sobre los cuales buscar el log

### Collect_logs(pods, namespace="default")
Esta función es basicamente tomar cada elemento de la lista **pods** (como se explicó antes, la lista guarda el nombre de los pods del namespace elegido), guardar el elemento en una variable **pod** y según esta variable ejecutar el comando `kubectl logs pod -n namespace` para de esa manera, obtener el log de cada pod, y este resultado, primero se guardará en el archivo `all_pods.log` y luego, se guardará en un archivo `pod.log` donde pod será el nombre del elemento que se está tomando por el momento, eso se hace para que hasta este punto, tener **n+1** archivos `.log`, donde este **1** será el archivo `all_pods.log` que guardará los resultados de todos los logs que se tienen de cada pod, y el **n** son los **n** pods que se tienen o matematicamente **n=len(pods)** y como ya se sabe, **pods** es una lista con todos los nombres de los pods existentes en el namespace elegido.

### Get_events(namespace="default")
Por último, esta función, se encarga de obtener todos los eventos ocurridos en el namespace elegido, ejecutando el comando `kubectl get events -n namespace` y guardando la respuesta en el archivo `all_events.log`

# Instrucción de ejecución
La forma de ejecutar este archivo, es similar al del archivo bash, podemos ejecutarlo señalando el namespace, o no y se tomará por defecto a default, así que suponiendo estamos dentro de la carpeta scripts que es donde se encuentra el script, ejecutamos el comando
```bash
python log_collector.py
```
Y en caso estemos en la carpeta raíz, modificamos el comando
```bash
python scripts/log_collector.py
```
