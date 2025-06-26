# Documentación de funciones de los hooks 

## commit-msg

Este hook lo que hace va a ser que al momento de escribir el commit respectivo y ejecutar, en la línea 3 se guarda la ruta temporal del mensaje del commit en la variable commit_msg_file
```bash
commit_msg_file=$1
```
Luego en la siguiente línea solo se guarda la ejecución del comando cat para la ruta que se guardó anteriormente
```bash
commit_msg=$(cat "$commit_msg_file")
```

En la variable **validation** se guarda mediante expresiones regulares, los requisitos que debe de tener el mensaje de commit:
```bash
validation="^(feat|fix|docs|test)(\([a-z0-9\-]+\))?: .{1,}"
```
Explicación de la expresión regular\
- **(feat|fix|docs|test)**: Verifica que el comienzo del mensaje sea "feat, fix, docs o test" según como lo indica la rúbrica la cuál pertenece a la convención de commits
- **(\([a-z0-9\-]+\))?:**: Esto indicará que luego de la primera verificación, el mensaje puede incluir mensaje entre paréntesis y terminando por el símbolo `:` y además un espacio adicional luego de los dos puntos ` ` como por ejemplo `feat(tf): <msg_commit>`
- **.{1,}**: La última restricción, verifica que al menos haya un carácter en la descripción, es decir, el mensaje del commit no puede estar vacío

La última parte es solo una condicional de bash, que verificará si **commit_msg** el cuál es el mensaje del commit, siga las verificaciones dadas en la variable **validation**, en caso no cumpla, nos dará como respouesta que nuestro mensaje de commit no cumple con la convención de commits
```bash
if echo "$commit_msg" | grep -qE "$validation"; then
  exit 0
else
  echo "El mensaje de commit no sigue la Convención de Commits." 
  echo "Ejemplo de mensaje: 'feat(tf-module):', 'fix(hooks)', 'docs(readme)' o 'test(py)'"
  exit 1
fi
```
### Ejemplo de ejecución
> Agregamos de manera normal los cambios hechos para que estén listos para el commit.
> Haremos el primer commit que tenga el mensaje `Add README.md for documentation` y como no cumple la convención, nos avisará ello.
```bash
git commit -m "Add README.md for documentation"
El mensaje de commit no sigue la Convención de Commits.
Ejemplo de mensaje: 'feat(tf-module):', 'fix(hooks)', 'docs(readme)' o 'test(py)'
```
> Notamos que como se esperaba, nos avisa que el mensaje de commit no cumple con la convención de commits
> Comiteamos nuevamente pero ahora con el mensaje `docs(readme): Add README.md for documentation` el cuál ya respeta la convención y nos tendría que aceptar el commit sin problemas:
```bash
git commit -m "docs(readme): Add README.md for documentation"
[master 4e9b678] docs(readme): Add README.md for documentation
 1 file changed, 25 insertions(+)
 create mode 100644 hooks/README.md
```

Y de esta manera notamos que nuestro hook commit-msg nos permitirá realizar commits que cumplan la convención de commits

## pre-commit

Al iniciar el hook se buscan los archivos que estan siendo commiteados con `git diff` y se filtran los archivos `.py` (y un patron regex) con grep.

```bash
PY_FILES=$(git diff --cached --name-only | grep '\.py$')

echo "$PY_FILES"
```

Si no hay archivos python, no se realizan mas acciones se termina con un output de OK (0).

```bash
if [ -z "$PY_FILES" ]; then
    echo "Sin archivos python para formateo o linting."
    exit 0
fi
```

En cambio si hay archivos `.py`, se realiza un bucle con los archivos python y se realiza un formateo con black y chequeo de lint con flake8, si hay un error en flake8 este genera un codigo y mensaje error y con un OR ( || ) se genera un output de error (1) en bash

```bash
for file in $PY_FILES; do
    black "$file"
    flake8 "$file" || exit 1    # al ultimo para ver si hay errores que no son solucionados por black
done

exit 0
```

Con este git hook se realiza formateo con black y chequeo de errors de lint con flake8 solo en archivos python, de esta manera los commits subidos al repositorio remoto seran limpios y los errores de lint disminuiran.

### Ejemplo de ejecución

> Se agrega un archivo python al staging area de git, luego se escribe el mensaje de commit

```bash
git add src/main.py
git commit -m "feat(py): 'Agrega archivo python inicial'"
```

> Cuando se realize el comando de commit se mostraran mensajes con los archivos python encontrados, y si se realizan formateos asi como los mensajes de errores de lint.

```bash
src/main.py
All done! 
1 file left unchanged.
src/main.py:17:80: E501 line too long (96 > 79 characters)
```

En este caso se realizo un formateo con black y flake8 muestra que la linea es muy larga (> 79 caracteres), por lo que el hook formateara el archivo y saldra del area de staging evitando el commit incorrecto. Cuando se solucione el error se mostrara el siguiente mensaje.

```bash
src/main.py
All done!
1 file left unchanged.
[master fdf666e] "feat(py): 'Agrega archivo python inicial'"
 1 file changed, 2 insertions(+), 1 deletion(-)
 ```

 Confirmando que se realizo el commit sin errores de lint y formateo.

## pre-push

Este hook va validar 3 acciones antes de realizar un push. 

- El primero será que no permitirá un `git push origin main`.
Inicialmente el script obtendrá el nombre de la rama actual y mostrará el nombre de la rama.
  ```bash
  current_branch=$(git symbolic-ref --short HEAD)
  echo "Rama actual: $current_branch"
  ```

  Entonces, si la rama actual es `main` nuestra mensajes de error y retorna con código 1.
  ```bash
  if [ "$current_branch" = "main" ]; then
      echo "Push directo a rama principal no permitido."
      echo "Protección local, complementa reglas de GitHub."
      exit 1
  fi
  ```

- El segunddo es para ejecutar los tests que tengamos. Verifica si existe el directorio `tests` y si contiene archivos `Python`. Si hay tests, los ejecuta usando pytest con modo verbose (-v), si los tests fallan muestra mensaje de error y sale con código 1 y si los tests pasan muestra mensaje de éxito
  ```bash
  if [ -d "tests" ] && [ -n "$(find tests -name '*.py' -print -quit)" ]; then
      echo "Ejecutando tests"
      python -m pytest tests/ -v
      if [ $? -ne 0 ]; then
          echo "Tests fallaron. Fix antes de push."
          exit 1
      fi
      echo "Tests pasaron."
  fi
  ```

- Y por último valida si hay cambios pendientes o no. Verifica si hay diferencias entre el último commit y el anterior y si no hay cambios, muestra un mensaje informativo. 
  ```bash
  if git diff --quiet HEAD~1 HEAD 2>/dev/null; then
    echo "No hay cambios para pushear."
  fi
  ```

### Ejemplo de ejecución
Si hacemos push desde la rama `main`
```bash
git add .
git commit -m "feat(hooks): Se añade hooks pre-commit, pre-push, commit-msg"
git push origin main
```

Cuando se haga el push nos botará mensajes de error.
```bash
Ejecutando validaciones pre-push...
Rama actual: main
Push directo a la rama principal no permitido.
Protección local, complementa reglas de GitHub.
error: failed to push some refs to 'https://github.com/grupo10-CC3S2/Proyecto7-PC4.git'
```

Si estamos en otra rama distinta a main, tenemos la carpeta tests y no tenemos cambios pendientes entre commits.
```bash
Ejecutando validaciones pre-push...
Rama actual: feature/...
Ejecutando tests
.
.
.
Test pasaron.
Validaciones pre-push completadas. Push puede continuar.
``` 

 ## Pasos para instalar los hooks
 
 1. Creamos el directorio hooks, el cual contendrá los archivos `pre-commit`, `commit-msg` y `pre-push`.

 2. En el directorio raiz implementamos un script `install_hooks.sh` que optimizará el uso de nuestros hooks.

 3. Ejecutar el comando `chmod +x install_hooks.sh` para convertir el archivo en ejecutable y por último lo ejecutamos `./install_hooks.sh`.