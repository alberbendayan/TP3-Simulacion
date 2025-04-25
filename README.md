<h1 align="center">Simulación de Sistemas</h1>
<h3 align="center">TP3: Dinámica molecular dirigida por eventos</h3>
<h4 align="center">Primer cuatrimestre 2025</h4>

# Requisitos

* Java versión 21: Para correr el simulador
* Maven: Para compilar el proyecto de Java
* Python: Para los gráficos
* [UV](https://github.com/astral-sh/uv): Administrador de dependencias para
Python

# Instalando las dependencias

```sh
# Para crear y activar el entorno virtual
uv venv
source .venv/bin/activate  # En Unix
.venv\Scripts\activate     # En Windows

# Para instalar las dependencias
uv sync
```

# Compilando el proyecto

Desde la consola, para compilar el proyecto de **Java**, desde la raíz del
proyecto, correr:

```bash
mvn clean package
```

# Ejecución de la simulación

Para correr la simulación, en Java, se le pueden pasar varios parámetros
opcionales los cuales son:

- `BIG_RADIUS`: el radio de la pared
- `SMALL_RADIUS`: el radio del obstáculo
- `PARTICLE_RADIUS`: el radio de las partículas
- `MASS`: la masa de las partículas
- `SPEED`: la velocidad de las partículas
- `TIME_LIMIT`: el tiempo máximo de simulación (en segundos)
- `OBSTACLE_MASS`: la masa del obstáculo (si se pone `0` se lo toma como un obstáculo fijo)
- `PARTICLE_COUNT`: la cantidad de partículas

```bash
java -classpath target/classes ar.edu.itba.ss.Main BIG_RADIUS=x SMALL_RADIUS=y ...
```

Estos parámetros son opcionales, si no se ingresan, el simulador tomará valores
por defecto.

Los resultados de la simulación, estarán guardados en la carpeta `results/`, con
los estados de cada evento guardados en una subcarpeta `snapshots/` que contiene
la posición, velocidad y radio de cada partícula.

# Ejecución de la animación y los gráficos

Hay cuatro archivos que generan los videos y las imágenes de los gráficos en la
carpeta de resultados de la simulación que se seleccione:

1. Uno genera una animación con los estados de cada fotograma.
2. Los otros muestran gráficos de análisis.

## Animación

Para visualizar la animación se puede correr:

```bash
uv run animacion.py <results_path>
```

## Gráficos

### Evolución de la presión

Para visualizar el gráfico de evolución se puede correr:

```bash
uv run graphic_a.py <results_path> --time-limit x
```

La variable opcional `--time-limit` permite, especificar el tiempo máximo hasta
donde se tomarán los datos de la simulación.

### Verificación de P~T

Para visualizar el gráfico se puede correr:

```bash
uv run graphic_b.py <dir1> <dir2> ... <dirn> --time-limit x
```

### Cantidad de colisiones totales y únicas

Para visualizar esta comparativa se puede correr:

```bash
uv run graphic_c.py <dir1> <dir2> ... <dirn> --time-limit x
```

### DCM

Para visualizar este gráfico de DCM primero hay que correr la simulación
especificando la variable opcional `OBSTACLE_MASS` con un valor diferente de
`0`.

```bash
java -classpath target/classes ar.edu.itba.ss.Main OBSTACLE_MASS=3
```

Luego, correr el gráfico de DCM para cada una de las simulaciones. La idea es
realizar varias simulaciones con los mismos parámetros para obtener valores de
media.

```bash
uv run graphic_d.py <dir1> <dir2> ... <dirn> --time-limit x
```
