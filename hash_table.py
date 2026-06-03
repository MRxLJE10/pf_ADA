# =============================================================================
# hash_table.py
# Clase: MatrizDispersa
#
# Tabla hash de direccionamiento abierto con sondeo lineal.
# Almacena solo los valores no nulos de una matriz de hasta 10^9 x 10^9.
# =============================================================================

_ACTIVO  = 1
_BORRADO = 2


class _Celda:
    """Nodo interno de la tabla hash."""
    def __init__(self, fila, col, valor):
        self.fila   = fila
        self.col    = col
        self.valor  = valor
        self.estado = _ACTIVO


class MatrizDispersa:
    """
    Tabla hash de direccionamiento abierto (sondeo lineal).
    Representa una matriz dispersa de dimensiones F x C.

    Complejidad promedio:
        insertar / buscar / eliminar -> O(1)
        peor caso (tabla muy llena)  -> O(N)
    Memoria: O(N), solo se almacenan los valores no nulos.
    """

    _FACTOR_CARGA = 0.7

    def __init__(self, filas, cols):
        self.filas             = filas
        self.cols              = cols
        self._capacidad        = 16
        self._tabla            = [None] * self._capacidad
        self._cantidad         = 0
        self._total_insertados = 0

    # ------------------------------------------------------------------
    # Funcion hash
    # ------------------------------------------------------------------
    def _hash(self, fila, col):
        """
        Combina (fila, col) en una clave unica mediante fila * p + col,
        donde p = 1_000_000_007 es primo y mayor que el maximo valor de
        columna posible (10^9). Luego aplica modulo sobre la capacidad.
        """
        clave = fila * 1_000_000_007 + col
        return clave % self._capacidad

    # ------------------------------------------------------------------
    # Sondeo lineal
    # ------------------------------------------------------------------
    def _buscar_indice(self, fila, col):
        """Retorna el indice de (fila, col) si existe, o None si no."""
        idx = self._hash(fila, col)
        for _ in range(self._capacidad):
            celda = self._tabla[idx]
            if celda is None:
                return None
            if celda.estado == _ACTIVO and celda.fila == fila and celda.col == col:
                return idx
            idx = (idx + 1) % self._capacidad
        return None

    def _buscar_indice_insercion(self, fila, col):
        """
        Retorna el indice donde insertar (fila, col).
        Reutiliza slots BORRADO. Si la clave ya existe, retorna su indice.
        """
        idx          = self._hash(fila, col)
        primer_borrado = None
        for _ in range(self._capacidad):
            celda = self._tabla[idx]
            if celda is None:
                return primer_borrado if primer_borrado is not None else idx
            if celda.estado == _BORRADO:
                if primer_borrado is None:
                    primer_borrado = idx
            elif celda.fila == fila and celda.col == col:
                return idx
            idx = (idx + 1) % self._capacidad
        return primer_borrado

    # ------------------------------------------------------------------
    # Rehash
    # ------------------------------------------------------------------
    def _rehash(self):
        """Duplica la capacidad y reinserta todos los elementos activos."""
        tabla_vieja        = self._tabla
        self._capacidad   *= 2
        self._tabla        = [None] * self._capacidad
        self._cantidad     = 0
        self._total_insertados = 0
        for celda in tabla_vieja:
            if celda is not None and celda.estado == _ACTIVO:
                self._insertar_interno(celda.fila, celda.col, celda.valor)

    def _insertar_interno(self, fila, col, valor):
        """Insercion directa sin verificar factor de carga (usada en rehash)."""
        idx = self._buscar_indice_insercion(fila, col)
        if self._tabla[idx] is not None and self._tabla[idx].estado == _ACTIVO:
            self._tabla[idx].valor = valor
        else:
            era_borrado = (self._tabla[idx] is not None and
                           self._tabla[idx].estado == _BORRADO)
            self._tabla[idx] = _Celda(fila, col, valor)
            self._cantidad += 1
            if not era_borrado:
                self._total_insertados += 1

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------
    def set(self, fila, col, valor):
        """Inserta o actualiza (fila, col). Si valor==0 elimina la celda."""
        if valor == 0:
            self.delete(fila, col)
            return "OK"
        if self._total_insertados / self._capacidad >= self._FACTOR_CARGA:
            self._rehash()
        self._insertar_interno(fila, col, valor)
        return "OK"

    def get(self, fila, col):
        """Retorna el valor en (fila, col), o 0 si la celda esta vacia."""
        idx = self._buscar_indice(fila, col)
        if idx is None:
            return 0
        return self._tabla[idx].valor

    def delete(self, fila, col):
        """
        Elimina (fila, col) con tombstone.
        Retorna 'OK' si existia, 'NOT_FOUND' si no.
        """
        idx = self._buscar_indice(fila, col)
        if idx is None:
            return "NOT_FOUND"
        self._tabla[idx].estado = _BORRADO
        self._cantidad -= 1
        return "OK"

    def cantidad(self):
        """Cantidad de valores no nulos actualmente almacenados."""
        return self._cantidad

    def iterar(self):
        """Generador: produce (fila, col, valor) de cada celda activa."""
        for celda in self._tabla:
            if celda is not None and celda.estado == _ACTIVO:
                yield celda.fila, celda.col, celda.valor