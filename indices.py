# =============================================================================
# indices.py
# Persona 2 — Indices auxiliares por fila y columna
#
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


# -----------------------------------------------------------------------------
# Lista enlazada simple para almacenar entradas en cada bucket
# -----------------------------------------------------------------------------

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

