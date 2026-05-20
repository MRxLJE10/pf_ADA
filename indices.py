# =============================================================================
# Estructuras propias implementadas:
#   - HashMapLista : tabla hash clave -> NodoLista (lista enlazada de entradas)
#   - NodoLista    : nodo de lista enlazada para manejar colisiones y entradas
#
# Operaciones soportadas:
#   ROW_SUM fila
#   COL_SUM columna
#   DENSITY
#
# Complejidad:
#   ROW_SUM / COL_SUM  -> O(k) donde k = elementos en esa fila/columna
#   DENSITY            -> O(1)
#   set / delete       -> O(1) promedio
# =============================================================================
class _NodoEntrada:
    """
    Nodo de lista enlazada.
    Almacena una entrada (clave_secundaria, valor) dentro de un bucket.

    clave_secundaria: en el indice de filas es la columna; en el de columnas es la fila.
    """
    def __init__(self, clave_sec, valor):
        self.clave_sec = clave_sec
        self.valor     = valor
        self.siguiente = None


class _ListaEntradas:
    """
    Lista enlazada simple que agrupa todas las entradas de un mismo bucket.
    Permite insertar, actualizar, eliminar y recorrer en O(k).
    """
    def __init__(self):
        self.cabeza = None
        self.tamanio = 0

    def insertar_o_actualizar(self, clave_sec, valor):
        """
        Si clave_sec ya existe, actualiza su valor.
        Si no existe, inserta al frente.
        Retorna True si fue insercion nueva, False si fue actualizacion.
        """
        nodo = self.cabeza
        while nodo is not None:
            if nodo.clave_sec == clave_sec:
                nodo.valor = valor
                return False  # actualizacion
            nodo = nodo.siguiente
        # Insertar al frente
        nuevo = _NodoEntrada(clave_sec, valor)
        nuevo.siguiente = self.cabeza
        self.cabeza = nuevo
        self.tamanio += 1
        return True  # insercion nueva

    def eliminar(self, clave_sec):
        """
        Elimina la entrada con clave_sec.
        Retorna True si existia, False si no.
        """
        anterior = None
        nodo = self.cabeza
        while nodo is not None:
            if nodo.clave_sec == clave_sec:
                if anterior is None:
                    self.cabeza = nodo.siguiente
                else:
                    anterior.siguiente = nodo.siguiente
                self.tamanio -= 1
                return True
            anterior = nodo
            nodo = nodo.siguiente
        return False

    def buscar(self, clave_sec):
        """Retorna el valor de clave_sec o None si no existe."""
        nodo = self.cabeza
        while nodo is not None:
            if nodo.clave_sec == clave_sec:
                return nodo.valor
            nodo = nodo.siguiente
        return None

    def suma(self):
        """Suma todos los valores de la lista. O(k)."""
        total = 0
        nodo = self.cabeza
        while nodo is not None:
            total += nodo.valor
            nodo = nodo.siguiente
        return total

    def iterar(self):
        """Generador que produce (clave_sec, valor)."""
        nodo = self.cabeza
        while nodo is not None:
            yield nodo.clave_sec, nodo.valor
            nodo = nodo.siguiente


# -----------------------------------------------------------------------------
# Tabla hash propia: clave_primaria (int) -> _ListaEntradas
# Usa encadenamiento (chaining) para manejar colisiones.
# -----------------------------------------------------------------------------

class _HashMapLista:
    """
    Tabla hash con encadenamiento.
    Mapea una clave entera (fila o columna) a una _ListaEntradas
    que contiene todas las entradas secundarias de esa clave.

    Complejidad promedio:
        insertar / buscar / eliminar -> O(1) sobre la tabla
        recorrer entradas de una clave -> O(k)
    """

    _FACTOR_CARGA = 0.7

    def __init__(self):
        self._capacidad   = 16
        self._buckets     = [None] * self._capacidad
        self._claves_usadas = 0  # cuantas claves primarias distintas hay

    # ------------------------------------------------------------------
    # Funcion hash para claves enteras grandes (hasta 10^9)
    # Usa multiplicacion de Fibonacci para distribucion uniforme.
    # ------------------------------------------------------------------
    def _hash(self, clave):
        # Constante de Knuth: floor(2^32 / phi) = 2654435769
        return (clave * 2654435769) % self._capacidad

    def _rehash(self):
        """Duplica capacidad y redistribuye todos los buckets."""
        buckets_viejos = self._buckets
        self._capacidad *= 2
        self._buckets = [None] * self._capacidad
        self._claves_usadas = 0

        for lista in buckets_viejos:
            if lista is not None:
                # Cada elemento de la lista es (clave_primaria, _ListaEntradas)
                clave_prim, entradas = lista
                idx = self._hash(clave_prim)
                # Reencadenar — en rehash no hay colisiones de clave_primaria
                # porque cada bucket tiene una sola clave primaria
                while idx < self._capacidad:
                    if self._buckets[idx] is None:
                        self._buckets[idx] = (clave_prim, entradas)
                        self._claves_usadas += 1
                        break
                    idx = (idx + 1) % self._capacidad

    def _buscar_bucket(self, clave_prim):
        """
        Retorna (indice, _ListaEntradas) si clave_prim existe,
        o (None, None) si no.
        """
        idx = self._hash(clave_prim)
        for _ in range(self._capacidad):
            bucket = self._buckets[idx]
            if bucket is None:
                return None, None
            clave_bucket, lista = bucket
            if clave_bucket == clave_prim:
                return idx, lista
            idx = (idx + 1) % self._capacidad
        return None, None

    def _obtener_o_crear(self, clave_prim):
        """
        Retorna la _ListaEntradas asociada a clave_prim.
        Si no existe, la crea e inserta en la tabla.
        """
        idx, lista = self._buscar_bucket(clave_prim)
        if lista is not None:
            return lista

        # Crear nueva lista para esta clave primaria
        if self._claves_usadas / self._capacidad >= self._FACTOR_CARGA:
            self._rehash()

        nueva_lista = _ListaEntradas()
        idx = self._hash(clave_prim)
        for _ in range(self._capacidad):
            if self._buckets[idx] is None:
                self._buckets[idx] = (clave_prim, nueva_lista)
                self._claves_usadas += 1
                return nueva_lista
            idx = (idx + 1) % self._capacidad

        # No deberia llegar aqui si el rehash funciona bien
        return nueva_lista

    def insertar(self, clave_prim, clave_sec, valor):
        """
        Inserta o actualiza (clave_prim, clave_sec) -> valor.
        Retorna True si fue insercion nueva, False si fue actualizacion.
        """
        lista = self._obtener_o_crear(clave_prim)
        return lista.insertar_o_actualizar(clave_sec, valor)

    def eliminar(self, clave_prim, clave_sec):
        """
        Elimina la entrada (clave_prim, clave_sec).
        Retorna True si existia, False si no.
        """
        _, lista = self._buscar_bucket(clave_prim)
        if lista is None:
            return False
        return lista.eliminar(clave_sec)

    def suma_por_clave(self, clave_prim):
        """
        Retorna la suma de todos los valores asociados a clave_prim.
        O(k) donde k = elementos en esa clave.
        """
        _, lista = self._buscar_bucket(clave_prim)
        if lista is None:
            return 0
        return lista.suma()

    def iterar_clave(self, clave_prim):
        """Generador: produce (clave_sec, valor) para una clave_prim."""
        _, lista = self._buscar_bucket(clave_prim)
        if lista is None:
            return
        yield from lista.iterar()
