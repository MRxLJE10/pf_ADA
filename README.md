# Motor Algorítmico para Procesamiento Eficiente de Matrices Dispersas

**Proyecto Final — Análisis y Diseño de Algoritmos I**  
ing. Mateo Echeverry Correa  
Universidad del Valle — 2026-I

---

## Integrantes

| Nombre | Código |
|--------|--------|
| Mariana Rios Coronado | 2459759 |
| Juan Sebastian Perez Cruz | 2459371 |
| Victor Murillo Goyes | 2459569 |
| Juan Felipe Aristizabal Davalos | 2459364 |

---

## Descripción general del problema

El sistema resuelve el problema de procesar una matriz dispersa de dimensiones hasta 10⁹ × 10⁹ sin construirla en memoria. Dado que la mayoría de celdas están vacías, solo se almacenan los valores no nulos, permitiendo operar con grandes volúmenes de datos de forma eficiente tanto en tiempo como en memoria.

El programa lee un conjunto inicial de valores y una secuencia de operaciones desde `entrada.txt`, las ejecuta en orden y escribe los resultados en `salida.txt`.

---

## Estructura del proyecto

```
hash_table.py       # Clase MatrizDispersa — GET, SET, DELETE
indices.py          # Clase IndicesAuxiliares — ROW_SUM, COL_SUM, DENSITY
matriz_sistema.py   # Clase MatrizConIndices — coordina los dos anteriores
operaciones.py      # Clase OperacionesAvanzadas — REGION_SUM, TRANSPOSE, TOP_K
main.py             # Punto de entrada: lectura, ejecución, escritura
entrada.txt         # Datos de entrada
salida.txt          # Resultados (se genera automáticamente)
test_indices.py     # Tests exhaustivos para IndicesAuxiliares
genera_casos.py     # Generador de casos de prueba de distintos tamaños
```

---

## Ejecución

1. Asegúrate de que todos los archivos `.py` estén en la misma carpeta junto con `entrada.txt`.
2. Corre el programa desde la terminal:

```bash
python main.py
```

3. El programa lee `entrada.txt` y genera `salida.txt` automáticamente.

Para correr los tests:

```bash
python test_indices.py
```

Para generar casos de prueba de distintos tamaños:

```bash
python genera_casos.py
```

---

## Formato de entrada

```
F C N
fila columna valor   (N veces)
Q
OPERACION parametros (Q veces)
```

Donde `F` es el número de filas, `C` el número de columnas, `N` la cantidad de valores no nulos iniciales y `Q` la cantidad de operaciones.

## Formato de salida

Cada operación que produce resultado genera una línea con el formato:

```
OPERACION parametros = resultado
```

---

## Diseño general de la solución

La solución se divide en cuatro módulos independientes que se integran en `main.py`:

- **`hash_table.py`**: implementa `MatrizDispersa`, la estructura principal que almacena los valores no nulos usando una tabla hash propia con sondeo lineal.
- **`indices.py`**: implementa `IndicesAuxiliares`, que mantiene índices por fila y por columna para acelerar `ROW_SUM` y `COL_SUM`.
- **`matriz_sistema.py`**: implementa `MatrizConIndices`, que coordina `MatrizDispersa` e `IndicesAuxiliares` garantizando que ambas estructuras estén siempre sincronizadas.
- **`operaciones.py`**: implementa `OperacionesAvanzadas`, que resuelve `REGION_SUM`, `TRANSPOSE` y `TOP_K`.
- **`main.py`**: integra todos los módulos. Se encarga únicamente de leer `entrada.txt`, despachar cada operación al módulo correspondiente y escribir `salida.txt`.

---

## Estructuras de datos implementadas

### MatrizDispersa — tabla hash con sondeo lineal

Implementada en `hash_table.py`. Representa la matriz usando únicamente los valores no nulos. Internamente es una tabla hash de direccionamiento abierto con sondeo lineal.

**Función hash:**

```
h(fila, col) = (fila × 1_000_000_007 + col) mod capacidad
```

El primo `p = 1_000_000_007` es mayor que el máximo valor de columna posible (10⁹), garantizando que pares distintos produzcan claves distintas.

**Eliminación con tombstone:** en lugar de desplazar elementos al eliminar, la celda se marca como `BORRADO`. Esto preserva las cadenas de sondeo sin costo adicional.

**Rehash:** cuando el factor de carga supera 0.7, la capacidad se duplica y todos los elementos activos se reinsertan. La capacidad inicial es 16.

---

### IndicesAuxiliares — tablas hash con encadenamiento

Implementada en `indices.py`. Mantiene dos índices auxiliares:

- `_idx_fila`: fila → lista de (col, valor)
- `_idx_col`: columna → lista de (fila, valor)

Cada índice es una instancia de `_HashMapLista`, que usa **encadenamiento** para manejar colisiones — a diferencia de `MatrizDispersa` que usa sondeo lineal. Esto demuestra que el equipo evaluó dos estrategias distintas para manejar colisiones.

**Función hash de Knuth:**

```
h(clave) = (clave × 2_654_435_769) mod capacidad
```

La constante `2_654_435_769 = ⌊2³² / φ⌋` (constante de Knuth) produce una distribución uniforme para claves enteras grandes.

Cada bucket de `_HashMapLista` contiene una `_ListaEntradas`: lista enlazada simple que agrupa todas las entradas secundarias de esa clave.

Los índices se sincronizan automáticamente con cada `SET` y `DELETE` a través de los métodos `on_set()` y `on_delete()`, manteniéndose siempre consistentes con la matriz.

---

### MatrizConIndices — fachada de coordinación

Implementada en `matriz_sistema.py`. Coordina `MatrizDispersa` e `IndicesAuxiliares`. Es el único punto de modificación de la matriz: garantiza que toda operación de escritura actualiza ambas estructuras juntas. El resto del programa solo interactúa con `MatrizConIndices`.

---

### OperacionesAvanzadas — operaciones sobre la matriz completa

Implementada en `operaciones.py`. Agrupa las operaciones que requieren recorrer o transformar la matriz: `REGION_SUM`, `TRANSPOSE` y `TOP_K`. Para `TOP_K`, los elementos se recolectan en una lista y se seleccionan con `_quickselect`, un algoritmo propio basado en dividir y vencer.

---

## Justificación de cada estructura

| Estructura | Tipo | Colisiones | Complejidad insertar | Complejidad suma por clave |
|------------|------|------------|----------------------|---------------------------|
| `MatrizDispersa` | Hash table | Sondeo lineal | O(1) promedio | O(N) (iterar todo) |
| `_HashMapLista` | Hash table | Encadenamiento | O(1) promedio | O(k) |
| `_ListaEntradas` | Lista enlazada | — | O(k) | O(k) |

La elección de una tabla hash para `MatrizDispersa` es fundamental: con coordenadas hasta 10⁹, un arreglo directo requeriría 10¹⁸ celdas, lo que es imposible. La tabla hash almacena solo los N valores no nulos en O(N) memoria.

Los índices auxiliares en `_HashMapLista` permiten que `ROW_SUM` y `COL_SUM` sean O(k) en lugar de O(N), donde k es el número de elementos en esa fila o columna.

---

## Operaciones soportadas

| Operación | Parámetros | Descripción |
|-----------|------------|-------------|
| `GET` | fila col | Retorna el valor en (fila, col), 0 si vacía |
| `SET` | fila col valor | Inserta o actualiza el valor |
| `DELETE` | fila col | Elimina el valor (tombstone) |
| `ROW_SUM` | fila | Suma de todos los valores en esa fila |
| `COL_SUM` | col | Suma de todos los valores en esa columna |
| `DENSITY` | — | Proporción de celdas no nulas sobre el total |
| `REGION_SUM` | f1 c1 f2 c2 | Suma dentro del rectángulo |
| `TOP_K` | k | Los k elementos con mayor valor |
| `TRANSPOSE` | — | Intercambia filas y columnas |

---

## Análisis de complejidad temporal

| Operación | Complejidad | Justificación |
|-----------|-------------|---------------|
| `GET` | O(1) promedio | Búsqueda directa en tabla hash |
| `SET` | O(1) promedio | Inserción en tabla hash; O(N) en rehash amortizado |
| `DELETE` | O(1) promedio | Marcado tombstone, sin desplazamiento |
| `ROW_SUM` | O(k_f) | k_f = elementos en esa fila; usa índice auxiliar |
| `COL_SUM` | O(k_c) | k_c = elementos en esa columna; usa índice auxiliar |
| `DENSITY` | O(1) | `cantidad / (F × C)`, ambos disponibles en O(1) |
| `REGION_SUM` | O(N) | Recorre todos los elementos no nulos |
| `TOP_K` | O(N) promedio | Quickselect propio; O(N²) peor caso |
| `TRANSPOSE` | O(N) | Un recorrido para recolectar, uno para reinsertar |

**Variables:**
- N: cantidad de valores no nulos activos
- Q: cantidad de operaciones
- k_f: elementos en la fila consultada
- k_c: elementos en la columna consultada
- k: cantidad de elementos solicitados en TOP_K

---

## Análisis de uso de memoria

La solución usa **O(N)** memoria en total, donde N es la cantidad de valores no nulos:

- `MatrizDispersa`: O(N) — una celda por valor no nulo.
- `_idx_fila` y `_idx_col`: O(N) cada uno — almacenan exactamente los mismos N pares en índices distintos.
- **Total: O(N)**

Nunca se construye una estructura proporcional al dominio (F × C), que podría llegar a 10¹⁸ celdas.

---

## Estrategia de dividir y vencer — TOP_K

La operación `TOP_K` utiliza **Quickselect**, un algoritmo propio basado en la estrategia de dividir y vencer.

### Problema que resuelve

Encontrar los k elementos con mayor valor entre N elementos no nulos, sin necesidad de ordenar todos.

### Descripción del algoritmo

```python
def _quickselect(self, lista, k):
    if k <= 0 or len(lista) == 0:
        return []
    if k >= len(lista):
        return lista[:]

    pivote_val = lista[len(lista) // 2][2]
    mayores, iguales, menores = [], [], []

    for item in lista:
        v = item[2]
        if v > pivote_val:
            mayores.append(item)
        elif v == pivote_val:
            iguales.append(item)
        else:
            menores.append(item)

    if len(mayores) >= k:
        return self._quickselect(mayores, k)
    elif len(mayores) + len(iguales) >= k:
        return mayores + iguales[:k - len(mayores)]
    else:
        resto = self._quickselect(menores, k - len(mayores) - len(iguales))
        return mayores + iguales + resto
```

### Caso base

Cuando `k ≤ 0` o `k ≥ len(lista)` (se piden más elementos de los que hay), se retorna directamente sin recursión.

### División

Se elige el elemento central como pivote y se divide la lista en tres particiones: mayores, iguales y menores al valor del pivote.

### Combinación

- Si `mayores` tiene ≥ k elementos → buscar recursivamente solo en `mayores`.
- Si `mayores + iguales` ≥ k → tomar todos los mayores y completar con `iguales`.
- Si no → tomar todos los mayores e iguales y buscar el resto en `menores`.

### Complejidad

- **Promedio: O(N)** — cada nivel de recursión procesa una fracción del problema.
- **Peor caso: O(N²)** — si el pivote siempre cae en el extremo (lista ya ordenada).

### Comparación con solución ingenua

| Solución | Complejidad | Descripción |
|----------|-------------|-------------|
| Ingenua | O(N × k) | Buscar el máximo k veces, eliminándolo cada vez |
| Ordenar todo | O(N log N) | Ordenar y tomar los primeros k |
| **Quickselect** | **O(N) promedio** | Dividir y vencer sin ordenar todo |

Quickselect es superior porque no necesita ordenar los N elementos completos — solo encuentra los k mayores, lo que es significativamente mejor cuando k ≪ N.

---

## Casos de prueba utilizados

### Caso del enunciado

Matriz de 10⁹ × 10⁹ con 6 valores no nulos:

```
1000000000 1000000000 6
1 1 5
1 100 7
500 300 9
1000 1000 2
200000 10 11
999999999 999999999 15
```

### Caso completo (entrada.txt entregada)

Incluye las 9 operaciones del sistema, verificando comportamiento antes y después de mutaciones:

```
GET 500 300      → 9
GET 999 999      → 0  (celda vacía)
ROW_SUM 1        → 12
COL_SUM 100      → 7
DENSITY          → 6.0000000000e-18
SET 1 100 20     → OK
GET 1 100        → 20
ROW_SUM 1        → 25 (actualizado)
COL_SUM 100      → 20 (actualizado)
REGION_SUM 1 1 1000 1000         → 36
REGION_SUM 1000000 1000000 ...   → 15
TOP_K 3          → (1,100,20) (999999999,999999999,15) (200000,10,11)
TOP_K 6          → todos los elementos ordenados
DELETE 500 300   → OK
GET 500 300      → 0
DELETE 500 300   → NOT_FOUND
ROW_SUM 500      → 0  (fila vacía tras delete)
TRANSPOSE        → OK
GET 100 1        → 20 (índices intercambiados)
GET 1 100        → 0
```

### Casos adicionales generados con genera_casos.py

- `entrada_pequeno.txt`: caso del enunciado (N=6, Q=7)
- `entrada_mediano.txt`: N=1000, Q=305
- `entrada_grande.txt`: N=50000, Q=1000
- `entrada_vacia.txt`: matriz sin valores no nulos
- `entrada_uno.txt`: un solo elemento
- `entrada_negativos.txt`: valores negativos y SET que sobreescribe

---

## Casos límite considerados

- **Matriz sin valores no nulos:** `GET`, `ROW_SUM`, `COL_SUM`, `REGION_SUM` y `TOP_K` retornan 0 o vacío sin errores.
- **GET sobre celda vacía:** retorna 0.
- **DELETE sobre celda inexistente:** retorna `NOT_FOUND`.
- **SET actualizando valor existente:** el índice auxiliar se actualiza correctamente.
- **ROW_SUM / COL_SUM de fila o columna vacía:** retorna 0.
- **REGION_SUM de región sin elementos:** retorna 0.
- **TOP_K con k > cantidad de elementos:** retorna todos los disponibles.
- **Coordenadas grandes (hasta 10⁹):** la función hash garantiza distribución uniforme sin colisiones por desbordamiento.
- **Valores negativos:** `ROW_SUM` y `COL_SUM` manejan correctamente sumas con negativos.
- **TRANSPOSE seguido de GET:** verifica que los índices se reconstruyen correctamente.

---

## Conclusiones

- El uso de una tabla hash propia permitió almacenar matrices de 10⁹ × 10⁹ usando solo O(N) memoria, donde N es el número de valores no nulos.
- Los índices auxiliares (`IndicesAuxiliares`) redujeron el costo de `ROW_SUM` y `COL_SUM` de O(N) a O(k), con sincronización automática en cada mutación.
- El grupo implementó dos estrategias distintas para manejar colisiones: sondeo lineal en `MatrizDispersa` y encadenamiento en `_HashMapLista`, evaluando los trade-offs de cada enfoque.
- El algoritmo Quickselect basado en dividir y vencer resuelve `TOP_K` en O(N) promedio, superando tanto la solución ingenua O(N × k) como la solución de ordenamiento completo O(N log N).
- La solución cumple las restricciones del enunciado: no usa estructuras nativas prohibidas (`dict`, `set`, `sorted`, `heapq`), no construye matrices completas y procesa correctamente coordenadas hasta 10⁹.
 
