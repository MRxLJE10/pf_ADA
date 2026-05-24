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

        
# -----------------------------------------------------------------------------
# Modulo principal de indices auxiliares
# -----------------------------------------------------------------------------
 
class IndicesAuxiliares:
    """
    Mantiene dos indices auxiliares sobre la MatrizDispersa:
        _idx_fila : fila    -> { col  : valor }
        _idx_col  : columna -> { fila : valor }
 
    Ambos se construyen en O(N) al inicializar y se mantienen
    sincronizados con cada set/delete en O(1) promedio.
 
    Responsabilidades:
        - ROW_SUM fila       -> O(k_f) donde k_f = elementos en esa fila
        - COL_SUM columna    -> O(k_c) donde k_c = elementos en esa columna
        - DENSITY            -> O(1)
    """
 
    def __init__(self, matriz):
        """
        Construye los indices recorriendo todos los elementos actuales
        de la matriz con matriz.iterar().
        Complejidad: O(N)
        """
        self._idx_fila = _HashMapLista()
        self._idx_col  = _HashMapLista()
        self._matriz   = matriz
 
        for fila, col, valor in matriz.iterar():
            self._idx_fila.insertar(fila, col, valor)
            self._idx_col.insertar(col, fila, valor)
 
    # ------------------------------------------------------------------
    # Sincronizacion: deben llamarse cada vez que la matriz cambie
    # ------------------------------------------------------------------
 
    def on_set(self, fila, col, valor_nuevo, valor_anterior):
        """
        Actualiza los indices cuando se hace SET (fila, col, valor_nuevo).
 
        valor_anterior: valor que habia antes (0 si no existia).
        Se llama DESPUES de que la matriz ya actualizo su valor.
        """
        self._idx_fila.insertar(fila, col, valor_nuevo)
        self._idx_col.insertar(col, fila, valor_nuevo)
 
    def on_delete(self, fila, col):
        """
        Actualiza los indices cuando se hace DELETE (fila, col).
        Se llama DESPUES de que la matriz ya elimino el valor.
        """
        self._idx_fila.eliminar(fila, col)
        self._idx_col.eliminar(col, fila)
 
    # ------------------------------------------------------------------
    # Operaciones publicas
    # ------------------------------------------------------------------
 
    def row_sum(self, fila):
        """
        Suma de todos los valores en la fila dada.
        Complejidad: O(k_f)
        """
        return self._idx_fila.suma_por_clave(fila)
 
    def col_sum(self, col):
        """
        Suma de todos los valores en la columna dada.
        Complejidad: O(k_c)
        """
        return self._idx_col.suma_por_clave(col)
 
    def density(self):
        """
        Proporcion de celdas no nulas sobre el total de celdas posibles.
        density = N_activos / (F * C)
 
        Complejidad: O(1)
 
        Nota: F*C puede ser hasta 10^18, por eso se usa division flotante
        y se formatea con suficientes decimales para no perder precision.
        """
        total_celdas = self._matriz.filas * self._matriz.cols
        if total_celdas == 0:
            return 0.0
        return self._matriz.cantidad() / total_celdas
 
    def iterar_fila(self, fila):
        """Generador: produce (col, valor) para todos los elementos de una fila."""
        yield from self._idx_fila.iterar_clave(fila)
 
    def iterar_col(self, col):
        """Generador: produce (fila, valor) para todos los elementos de una columna."""
        yield from self._idx_col.iterar_clave(col)
 
    def ejecutar(self, nombre, params, matriz):
        """
        Punto de entrada para ejecutar_operaciones() del hash_table.py.
        Recibe el nombre de la operacion y sus parametros como lista de strings.
        """
        if nombre == "ROW_SUM":
            fila = int(params[0])
            resultado = self.row_sum(fila)
            return f"ROW_SUM {fila} = {resultado}"
 
        elif nombre == "COL_SUM":
            col = int(params[0])
            resultado = self.col_sum(col)
            return f"COL_SUM {col} = {resultado}"
 
        elif nombre == "DENSITY":
            d = self.density()
            # Mostrar en notacion cientifica si es muy pequenio
            if d == 0.0:
                return "DENSITY = 0.0"
            return f"DENSITY = {d:.10e}"
 
        else:
            return f"{nombre} = NO_IMPLEMENTADO_EN_INDICES"