# Calculadora-de-Procesos-de-Redes

# CPM Studio

Aplicación de escritorio para planificar proyectos mediante el método de la ruta crítica (**CPM**, por sus siglas en inglés). Permite definir actividades, establecer sus dependencias, calcular la red del proceso, identificar la ruta crítica y visualizar el cronograma en un diagrama de Gantt.

## Funciones principales

- Crear, editar y eliminar actividades.
- Definir la duración de cada actividad.
- Indicar las predecesoras directas de cada actividad.
- Calcular automáticamente:
  - Red de precedencias.
  - Ruta crítica.
  - Duración total del proyecto.
  - Inicio temprano y terminación temprana.
  - Inicio tardío y terminación tardía.
  - Flotante total y flotante libre.
- Detectar actividades con `señal roja`, es decir, actividades cuya demora puede afectar a sus sucesoras antes de consumir toda su holgura total.
- Visualizar la red del proyecto.
- Visualizar el cronograma tipo Gantt.
- Cargar un proyecto de ejemplo de construcción de una casa.
- Importar y exportar proyectos en formato JSON.
- Exportar la red y el cronograma como imágenes PNG.
- Recalcular automáticamente al agregar, editar o eliminar una actividad.
- Consultar la ficha completa de cualquier actividad seleccionada en Resultados.

## Requisitos

- Windows, macOS o Linux.
- Python 3.10 o superior.
- Las bibliotecas indicadas en `requirements.txt`:
  - `matplotlib`
  - `networkx`

`tkinter` se utiliza para la interfaz gráfica. Normalmente viene incluido con Python en Windows.

## Instalación

Abre PowerShell o una terminal en la carpeta del proyecto:

```powershell
cd "c:\Users\munoz\Documents\Aplicaciones\Calculadora de procesos"
```

Instala las dependencias:

```powershell
python -m pip install -r requirements.txt
```

Si `python` no apunta al intérprete correcto, utiliza el ejecutable configurado en VS Code:

```powershell
& "C:/Users/munoz/AppData/Local/Microsoft/WindowsApps/python3.12.exe" -m pip install -r requirements.txt
```

## Ejecutar la aplicación

Desde la carpeta del proyecto:

```powershell
python app.py
```

También puedes abrir `app.py` en VS Code y utilizar **Run Python File**.

Al iniciar, CPM Studio carga automáticamente un ejemplo de construcción con 20 actividades y calcula sus resultados. El programa genera las imágenes en la carpeta `salidas`.

## Cómo definir una actividad

En el panel izquierdo encontrarás cuatro campos:

| Campo | Qué significa | Ejemplo |
|---|---|---|
| `ID` | Identificador único y corto de la actividad | `A` |
| `Actividad` | Nombre o descripción de la tarea | `Excavar cimientos` |
| `Duración` | Tiempo necesario para realizar la tarea | `3` |
| `Predecesoras` | IDs de actividades que deben terminar antes | `A, B` |

### Reglas para el ID

- Debe ser único dentro del proyecto.
- Se convierte automáticamente a mayúsculas.
- Se recomienda usar letras o códigos cortos: `A`, `B`, `C`, `EXC-01`.
- No debe repetirse.

### Reglas para la duración

- Debe ser un número positivo.
- Puede ser entero o decimal, _ejemplo_ (`3`, `2.5`, `0.5`).
- La unidad es definida por el usuario: días, semanas, horas, meses, etc.
- Todas las actividades deben utilizar la misma unidad.

### Reglas para las predecesoras

- Escribe los IDs separados por comas: `A, B`.
- Una actividad sin predecesoras comienza desde el inicio del proyecto.
- Para indicar que no tiene predecesoras puedes dejar `-`.
- Las predecesoras deben existir en la tabla.
- No puede haber ciclos. Por ejemplo, `A -> B -> A` no es válido.

## Flujo de trabajo recomendado

1. Pulsa **Cargar ejemplo** para estudiar un proyecto completo, o crea tus propias actividades.
2. Escribe el `ID`, nombre, duración y predecesoras.
3. Pulsa **+ Agregar**.
4. Repite el proceso hasta completar la red.
5. El análisis se recalcula automáticamente después de agregar, editar o eliminar una actividad. También puedes pulsar **CALCULAR PROYECTO** en cualquier momento.
6. Revisa la pestaña **Resultados** y selecciona una fila para ver la ficha completa: datos de entrada, tiempos tempranos y tardíos, holguras, dependencias, estado y señal roja. Pulsa **Editar esta actividad en el formulario** para cambiar su ID, nombre, duración o predecesoras.
7. Revisa la pestaña **Red del proceso** para ver las relaciones entre actividades.
8. Revisa la pestaña **Cronograma** para analizar el calendario y las holguras.

## Editar una actividad

1. Selecciona una fila de la tabla izquierda.
2. Sus datos aparecerán en el formulario.
3. Modifica uno o varios campos.
4. Pulsa **Actualizar**.
5. El programa recalcula automáticamente todos los resultados, la red y el cronograma.

También puedes seleccionar cualquier actividad desde **Resultados**. Sus valores se cargarán en el formulario izquierdo; pulsa **Actualizar** para aplicar los cambios a esa actividad y a las actividades que dependan de ella.

Si modificas el ID, CPM Studio actualiza también las referencias a ese ID en las actividades que lo utilizan como predecesora.

## Eliminar una actividad

1. Selecciona la actividad en la tabla.
2. Pulsa **Eliminar seleccionada**.
3. Las referencias a esa actividad se retiran de las predecesoras de las demás actividades.
4. Vuelve a calcular el proyecto.

## Interpretar los resultados

### Ruta crítica

La ruta crítica aparece en rojo y se muestra en la parte superior de **Resultados**. Es la secuencia de actividades con flotante total igual a cero. Una demora en cualquiera de ellas puede retrasar la fecha final del proyecto.

### Indicadores de tiempo

| Indicador | Significado |
|---|---|
| `ES` | Inicio temprano: momento más pronto en que puede comenzar la actividad. |
| `EF` | Terminación temprana: `ES + duración`. |
| `LS` | Inicio tardío: último momento en que puede comenzar sin retrasar el proyecto. |
| `LF` | Terminación tardía: último momento en que puede terminar sin retrasar el proyecto. |
| `Flot. total` | Tiempo que puede retrasarse una actividad sin retrasar el proyecto completo. |
| `Flot. libre` | Tiempo que puede retrasarse sin retrasar el inicio temprano de sus sucesoras. |

### Señales rojas

Una señal roja aparece cuando el flotante libre es menor que el flotante total. Esto significa que una actividad puede tener margen para no retrasar la fecha final, pero su demora puede desplazar el inicio de una actividad siguiente.

## Red del proceso

La pestaña **Red del proceso** muestra un grafo dirigido:

- Cada nodo representa una actividad.
- Una flecha indica una relación de precedencia.
- Los nodos críticos aparecen en rojo.
- Las actividades no críticas aparecen en azul.
- Los enlaces de la ruta crítica se resaltan.

## Cronograma de actividades

La pestaña **Cronograma** muestra un Gantt:

- Rojo: actividad crítica.
- Azul: actividad no crítica.
- Rayado: holgura total disponible.
- La línea vertical marca el final calculado del proyecto.

Puedes pulsar **Exportar PNG** para guardar la gráfica en otra ubicación.

## Guardar y abrir proyectos JSON

### Exportar

Pulsa **Exportar JSON** y elige dónde guardar el archivo. El formato generado es una lista de actividades:

```json
[
  {
    "id": "A",
    "nombre": "Excavar cimientos",
    "duracion": 3,
    "predecesoras": []
  },
  {
    "id": "B",
    "nombre": "Colar concreto",
    "duracion": 2,
    "predecesoras": ["A"]
  }
]
```

### Importar

Pulsa **Importar JSON**, selecciona un archivo con el formato anterior y el programa cargará y calculará el proyecto.

## Ejemplo rápido

Para un proyecto de cuatro actividades:

| ID | Actividad | Duración | Predecesoras |
|---|---|---:|---|
| A | Diseño | 2 | - |
| B | Compra de materiales | 3 | - |
| C | Construcción | 5 | A, B |
| D | Inspección final | 1 | C |

La red es:

```text
A ──┐
    ├──> C ──> D
B ──┘
```

La ruta crítica será la secuencia que determine la mayor duración acumulada hasta `D`.

## Archivos del proyecto

| Archivo | Función |
|---|---|
| `app.py` | Interfaz gráfica de CPM Studio. |
| `cpm_analyzer.py` | Motor de cálculo CPM y generación de gráficas. |
| `ejemplo_construccion_casa.py` | Ejemplo ejecutable desde la terminal. |
| `requirements.txt` | Dependencias Python. |
| `salidas/` | Imágenes generadas por la aplicación. |

## Ejecutar el ejemplo desde la terminal

Si quieres ejecutar el ejemplo sin abrir la interfaz:

```powershell
python ejemplo_construccion_casa.py
```

El programa imprimirá los cálculos en la terminal y guardará el Gantt y la red en `salidas`.

## Problemas frecuentes

### `ModuleNotFoundError: No module named 'matplotlib'` o `networkx`

Instala las dependencias con:

```powershell
python -m pip install -r requirements.txt
```

Comprueba que instalas los paquetes en el mismo Python con el que ejecutas `app.py`.

### La aplicación no abre

Ejecuta desde una terminal para ver el mensaje exacto:

```powershell
python app.py
```

En Windows, utiliza una instalación normal de Python desde python.org o el intérprete configurado en VS Code.

### Error de predecesora inexistente

Comprueba que cada ID escrito en `Predecesoras` coincide exactamente con una actividad existente. La aplicación convierte los IDs a mayúsculas, por lo que `a` se interpreta como `A`.

### Error de ciclo de precedencias

Revisa que ninguna cadena de dependencias regrese a una actividad anterior. Una red CPM válida debe ser acíclica.

## Notas técnicas

El programa utiliza el modelo **Actividad-en-el-Nodo (AON)**. Cada actividad es un nodo y sus predecesoras se representan mediante flechas. El algoritmo realiza un recorrido hacia adelante para calcular tiempos tempranos y un recorrido hacia atrás para calcular tiempos tardíos y holguras.

La instalación opcional de `pygraphviz` no es necesaria. Cuando no está disponible, el programa utiliza automáticamente un diseño alternativo por niveles para dibujar la red.