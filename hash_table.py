# -----------------------------------------------------------------------------
# Constantes
# -----------------------------------------------------------------------------
_VACIO   = 0   # celda nunca usada
_ACTIVO  = 1   # celda con dato valido
_BORRADO = 2   # celda marcada como eliminada (tombstone)


class _Celda:
    """Nodo interno de la tabla hash."""
    def __init__(self, fila, col, valor):
        self.fila  = fila
        self.col   = col
        self.valor = valor
        self.estado = _ACTIVO


class MatrizDispersa:
    """
    Tabla hash de direccionamiento abierto (sondeo lineal) que representa
    una matriz dispersa de dimensiones F x C con N valores no nulos.

    Complejidad promedio:
        insertar / buscar / eliminar -> O(1)
        peor caso (tabla muy llena)  -> O(N)
        Memoria: O(N), solo se almacenan los valores no nulos.
    """

    # Factor de carga maximo antes de hacer rehash
    _FACTOR_CARGA = 0.7 #70% de la capacidad

    def __init__(self, filas, cols):
        self.filas = filas          # dimension total de filas
        self.cols  = cols           # dimension total de columnas
        self._capacidad = 16        # tamano inicial de la tabla (potencia de 2)
        self._tabla = [None] * self._capacidad # tabla hash con slots vacios
        self._cantidad = 0          # elementos activos
        self._total_insertados = 0  # activos + tombstones (para el factor de carga)

    # ------------------------------------------------------------------
    # Funcion hash
    # ------------------------------------------------------------------
    def _hash(self, fila, col):
        """
        Convierte el par (fila, col) en un indice de la tabla.
        Se combina fila y columna en una clave unica mediante fila * p + col,
        donde p = 1_000_000_007 es un primo mayor que el maximo valor de
        columna posible (10^9), garantizando que pares distintos produzcan
        claves distintas. Luego se aplica modulo para obtener el indice.
        """
        clave = fila * 1_000_000_007 + col
        return clave % self._capacidad

    # ------------------------------------------------------------------
    # Sondeo lineal
    # ------------------------------------------------------------------
    def _buscar_indice(self, fila, col):
        """
        Retorna el indice donde esta (fila, col) si existe,
        o None si no se encuentra.
        """
        idx = self._hash(fila, col)
        for _ in range(self._capacidad):
            celda = self._tabla[idx]
            if celda is None:
                # Celda vacia => la clave no existe en la tabla
                return None
            if celda.estado == _ACTIVO and celda.fila == fila and celda.col == col:
                return idx
            # Si es BORRADO o es otra clave, seguir sondeando
            idx = (idx + 1) % self._capacidad
        return None

    def _buscar_indice_insercion(self, fila, col):
        """
        Retorna el indice donde se debe insertar (fila, col).
        Si la clave ya existe, retorna su indice actual.
        Aprovecha los slots BORRADO para reutilizarlos.
        """
        idx = self._hash(fila, col)
        primer_borrado = None
        for _ in range(self._capacidad):
            celda = self._tabla[idx]
            if celda is None:
                # Slot completamente vacio
                return primer_borrado if primer_borrado is not None else idx
            if celda.estado == _BORRADO:
                if primer_borrado is None:
                    primer_borrado = idx
            elif celda.fila == fila and celda.col == col:
                # La clave ya existe => actualizacion
                return idx
            idx = (idx + 1) % self._capacidad
        return primer_borrado

    # ------------------------------------------------------------------
    # Rehash
    # ------------------------------------------------------------------
    def _rehash(self):
        """Duplica la capacidad y reinserta todos los elementos activos."""
        tabla_vieja = self._tabla
        self._capacidad *= 2
        self._tabla = [None] * self._capacidad
        self._cantidad = 0
        self._total_insertados = 0
        for celda in tabla_vieja:
            if celda is not None and celda.estado == _ACTIVO:
                self._insertar_interno(celda.fila, celda.col, celda.valor)

    def _insertar_interno(self, fila, col, valor):
        """Insercion sin verificar factor de carga (usada en rehash)."""
        idx = self._buscar_indice_insercion(fila, col)
        if self._tabla[idx] is not None and self._tabla[idx].estado == _ACTIVO:
            # Actualizacion de clave existente
            self._tabla[idx].valor = valor
        else:
            era_borrado = (self._tabla[idx] is not None and
                           self._tabla[idx].estado == _BORRADO)
            self._tabla[idx] = _Celda(fila, col, valor)
            self._cantidad += 1
            if not era_borrado:
                self._total_insertados += 1

    # ------------------------------------------------------------------
    # Funciones publicas: set, get, delete, cantidad, iterar
    # ------------------------------------------------------------------

    def set(self, fila, col, valor):
        """
        Inserta o actualiza el valor en (fila, col).
        Si valor == 0, equivale a eliminar la celda.

        Retorna:
            "OK"
        """
        if valor == 0:
            self.delete(fila, col)
            return "OK"
        # Verificar factor de carga antes de insertar
        if self._total_insertados / self._capacidad >= self._FACTOR_CARGA:
            self._rehash()
        self._insertar_interno(fila, col, valor)
        return "OK"

    def get(self, fila, col):
        """
        Retorna el valor en (fila, col), o 0 si la celda esta vacia.
        """
        idx = self._buscar_indice(fila, col)
        if idx is None:
            return 0
        return self._tabla[idx].valor

    def delete(self, fila, col):
        """
        Elimina (fila, col) usando tombstone (marcado como BORRADO).
        Si la celda no existe, no hace nada.

        Retorna:
            "OK"  si existia y se elimino
            "NOT_FOUND"  si no existia
        """
        idx = self._buscar_indice(fila, col)
        if idx is None:
            return "NOT_FOUND"
        self._tabla[idx].estado = _BORRADO
        self._cantidad -= 1
        return "OK"

    def cantidad(self):
        """Retorna cuantos valores no nulos hay actualmente."""
        return self._cantidad

    def iterar(self):
        """
        Generador que produce (fila, col, valor) de cada celda activa.
        Usado por los modulos de indices, REGION_SUM y TOP_K.
        """
        for celda in self._tabla:
            if celda is not None and celda.estado == _ACTIVO:
                yield celda.fila, celda.col, celda.valor


# =============================================================================
# Lectura de entrada.txt y escritura de salida.txt
# =============================================================================

def leer_entrada(ruta="entrada.txt"):
    """
    Parsea entrada.txt con el formato:
        F C N
        fila col valor   (N veces)
        Q
        OPERACION params (Q veces)

    Retorna:
        matriz   -> instancia de MatrizDispersa ya cargada
        ops      -> lista de strings con las operaciones
    """
    with open(ruta, "r") as f:
        lineas = f.read().split("\n")

    idx = 0

    # Primera linea: dimensiones y cantidad de valores iniciales
    partes = lineas[idx].split(); idx += 1
    F, C, N = int(partes[0]), int(partes[1]), int(partes[2])

    matriz = MatrizDispersa(F, C)

    # N lineas de valores no nulos
    for _ in range(N):
        p = lineas[idx].split(); idx += 1
        fila, col, valor = int(p[0]), int(p[1]), int(p[2])
        matriz.set(fila, col, valor)

    # Cantidad de operaciones
    Q = int(lineas[idx]); idx += 1

    # Q operaciones
    ops = []
    for _ in range(Q):
        if idx < len(lineas) and lineas[idx].strip():
            ops.append(lineas[idx].strip())
        idx += 1

    return matriz, ops


def ejecutar_operaciones(matriz, ops, modulo_indices=None):
    """
    Ejecuta cada operacion y retorna una lista de strings con los resultados.

    Parametros:
        matriz         -> instancia de MatrizDispersa
        ops            -> lista de strings de operaciones
        modulo_indices -> objeto con metodos row_sum, col_sum, etc.
    """
    resultados = []

    for op in ops:
        partes = op.split()
        nombre = partes[0].upper()

        if nombre == "GET":
            fila, col = int(partes[1]), int(partes[2])
            val = matriz.get(fila, col)
            resultados.append(f"GET {fila} {col} = {val}")

        elif nombre == "SET":
            fila, col, valor = int(partes[1]), int(partes[2]), int(partes[3])
            matriz.set(fila, col, valor)
            resultados.append(f"SET {fila} {col} = OK")

        elif nombre == "DELETE":
            fila, col = int(partes[1]), int(partes[2])
            res = matriz.delete(fila, col)
            resultados.append(f"DELETE {fila} {col} = {res}")

        elif modulo_indices is not None:
            # PENDIENTE: integrar el modulo de indices para estas operaciones
            resultado = modulo_indices.ejecutar(nombre, partes[1:], matriz)
            resultados.append(resultado)

        else:
            # PENDIENTE: operaciones de REGION_SUM, TOP_K, etc. sin modulo de indices
            resultados.append(f"{nombre} = PENDIENTE")

    return resultados


def escribir_salida(resultados, ruta="salida.txt"):
    """Escribe los resultados en salida.txt, uno por linea."""
    with open(ruta, "w") as f:
        f.write("\n".join(resultados) + "\n")


# =============================================================================
# Entrada Principal
# =============================================================================

if __name__ == "__main__":
    matriz, ops = leer_entrada("entrada.txt")
    resultados = ejecutar_operaciones(matriz, ops)
    escribir_salida(resultados, "salida.txt")
    print(f"Melo {len(resultados)} operaciones hechas.")