# =============================================================================
# Estructuras propias implementadas:
#   - _ArregloDinamico : arreglo dinamico propio (sin usar list.sort ni sorted)
#
# Algoritmo de dividir y vencer:
#   - _merge_sort      : ordena por valor descendente en O(N log N)
#                        usado en TOP_K
#
# Operaciones soportadas:
#   REGION_SUM f1 c1 f2 c2
#   TOP_K k
#   TRANSPOSE
#
# Complejidad:
#   REGION_SUM -> O(k) donde k = elementos activos en la region
#   TOP_K      -> O(N log N) donde N = elementos no nulos
#   TRANSPOSE  -> O(N)
# =============================================================================


# -----------------------------------------------------------------------------
# Arreglo dinamico propio
# -----------------------------------------------------------------------------

class _ArregloDinamico:
    """
    Arreglo dinamico simple que duplica capacidad al llenarse.
    Almacena tuplas (valor, fila, col).
    """
    def __init__(self):
        self._capacidad = 16
        self._datos     = [None] * self._capacidad
        self._tamanio   = 0

    def agregar(self, item):
        if self._tamanio == self._capacidad:
            self._capacidad *= 2
            nuevo = [None] * self._capacidad
            for i in range(self._tamanio):
                nuevo[i] = self._datos[i]
            self._datos = nuevo
        self._datos[self._tamanio] = item
        self._tamanio += 1

    def obtener(self, i):
        return self._datos[i]

    def asignar(self, i, val):
        self._datos[i] = val

    def tamanio(self):
        return self._tamanio


# -----------------------------------------------------------------------------
# Merge Sort — Dividir y Vencer
# Ordena _ArregloDinamico por valor DESCENDENTE
# Complejidad: O(N log N) tiempo, O(N) espacio auxiliar
# -----------------------------------------------------------------------------

def _merge_sort(arr, inicio, fin):
    """
    Ordena arr[inicio..fin] usando merge sort.
    Caso base: subarray de tamanio 1.
    Division: mitad izquierda y mitad derecha.
    Combinacion: merge con comparacion por valor descendente.
    """
    if fin - inicio <= 0:
        return
    medio = (inicio + fin) // 2
    _merge_sort(arr, inicio, medio)
    _merge_sort(arr, medio + 1, fin)
    _merge(arr, inicio, medio, fin)


def _merge(arr, inicio, medio, fin):
    """Combina dos mitades ordenadas en orden descendente por valor."""
    izq = [arr.obtener(i) for i in range(inicio, medio + 1)]
    der = [arr.obtener(i) for i in range(medio + 1, fin + 1)]

    i, j, k = 0, 0, inicio
    while i < len(izq) and j < len(der):
        if izq[i][0] >= der[j][0]:
            arr.asignar(k, izq[i]); i += 1
        else:
            arr.asignar(k, der[j]); j += 1
        k += 1
    while i < len(izq):
        arr.asignar(k, izq[i]); i += 1; k += 1
    while j < len(der):
        arr.asignar(k, der[j]); j += 1; k += 1


# -----------------------------------------------------------------------------
# Modulo principal de operaciones avanzadas
# -----------------------------------------------------------------------------

class OperacionesAvanzadas:
    """
    Implementa REGION_SUM, TOP_K y TRANSPOSE sobre MatrizConIndices.

    Se inicializa una sola vez y se mantiene como atributo de MatrizConIndices,
    igual que IndicesAuxiliares.
    """

    def __init__(self, matriz):
        self._matriz = matriz

    # ------------------------------------------------------------------
    # REGION_SUM f1 c1 f2 c2
    # Suma todos los valores cuya fila este en [f1,f2] y col en [c1,c2]
    # Complejidad: O(k) donde k = elementos activos en la region
    # ------------------------------------------------------------------

    def region_sum(self, f1, c1, f2, c2):
        """
        Recorre solo los elementos no nulos de la matriz.
        No construye ninguna estructura proporcional al dominio.
        """
        rf1, rf2 = min(f1, f2), max(f1, f2)
        rc1, rc2 = min(c1, c2), max(c1, c2)
        total = 0
        for fila, col, valor in self._matriz.iterar():
            if rf1 <= fila <= rf2 and rc1 <= col <= rc2:
                total += valor
        return total

    # ------------------------------------------------------------------
    # TOP_K k
    # Retorna los k elementos con mayor valor usando merge sort propio
    # Complejidad: O(N log N) donde N = elementos no nulos
    # ------------------------------------------------------------------

    def top_k(self, k):
        """
        1. Carga todos los elementos en un _ArregloDinamico propio.
        2. Aplica merge sort (dividir y vencer) para ordenar descendentemente.
        3. Retorna los primeros k elementos.
        """
        arr = _ArregloDinamico()
        for fila, col, valor in self._matriz.iterar():
            arr.agregar((valor, fila, col))

        n = arr.tamanio()
        if n == 0:
            return []

        _merge_sort(arr, 0, n - 1)

        resultado = []
        for i in range(min(k, n)):
            valor, fila, col = arr.obtener(i)
            resultado.append((fila, col, valor))
        return resultado

    # ------------------------------------------------------------------
    # TRANSPOSE
    # Intercambia filas y columnas de todos los elementos activos.
    # Complejidad: O(N)
    # ------------------------------------------------------------------

    def transpose(self):
        """
        1. Recoge todos los elementos actuales.
        2. Elimina cada uno de la matriz.
        3. Re-inserta con fila y columna intercambiadas.
        Tambien intercambia las dimensiones de la matriz.
        """
        elementos = []
        for fila, col, valor in self._matriz.iterar():
            elementos.append((fila, col, valor))

        for fila, col, _ in elementos:
            self._matriz.delete(fila, col)

        self._matriz.matriz.filas, self._matriz.matriz.cols = (
            self._matriz.matriz.cols, self._matriz.matriz.filas
        )

        for fila, col, valor in elementos:
            self._matriz.set(col, fila, valor)

        return "OK"

    # ------------------------------------------------------------------
    # Punto de entrada — llamado desde ejecutar_operaciones en main.py
    # ------------------------------------------------------------------

    def ejecutar(self, nombre, params):
        """
        Recibe el nombre de la operacion y sus parametros como lista de strings.
        Mismo patron que IndicesAuxiliares.ejecutar().
        """
        if nombre == "REGION_SUM":
            f1, c1, f2, c2 = int(params[0]), int(params[1]), int(params[2]), int(params[3])
            res = self.region_sum(f1, c1, f2, c2)
            return f"REGION_SUM {f1} {c1} {f2} {c2} = {res}"

        elif nombre == "TOP_K":
            k = int(params[0])
            elementos = self.top_k(k)
            if not elementos:
                return f"TOP_K {k} = (vacio)"
            partes_str = " ".join(f"({f},{c},{v})" for f, c, v in elementos)
            return f"TOP_K {k} = {partes_str}"

        elif nombre == "TRANSPOSE":
            self.transpose()
            return "TRANSPOSE = OK"

        else:
            return f"{nombre} = NO_IMPLEMENTADO_EN_AVANZADAS"