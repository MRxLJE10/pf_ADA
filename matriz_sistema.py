# =============================================================================
# Clase: MatrizConIndices
#
# Coordina MatrizDispersa e IndicesAuxiliares.
# Todas las operaciones de escritura (set, delete) actualizan ambas
# estructuras de forma sincronizada.
# =============================================================================

from hash_table import MatrizDispersa
from indices    import IndicesAuxiliares


class MatrizConIndices:
    """
    Une MatrizDispersa (almacenamiento) con IndicesAuxiliares (consultas).
    Es el unico objeto que circula entre modulos, garantiza que indices
    y matriz siempre esten sincronizados.
    """

    def __init__(self, filas, cols):
        self.matriz  = MatrizDispersa(filas, cols)
        self.indices = None

    def inicializar_indices(self):
        """Construye los indices auxiliares sobre los datos ya cargados."""
        self.indices = IndicesAuxiliares(self.matriz)

    # ------------------------------------------------------------------
    # Escritura sincronizada
    # ------------------------------------------------------------------
    def set(self, fila, col, valor):
        """Inserta o actualiza (fila, col) y sincroniza los indices."""
        valor_anterior = self.matriz.get(fila, col)
        self.matriz.set(fila, col, valor)
        if self.indices is not None:
            if valor == 0:
                self.indices.on_delete(fila, col)
            else:
                self.indices.on_set(fila, col, valor, valor_anterior)
        return "OK"

    def delete(self, fila, col):
        """Elimina (fila, col) y sincroniza los indices."""
        resultado = self.matriz.delete(fila, col)
        if self.indices is not None and resultado == "OK":
            self.indices.on_delete(fila, col)
        return resultado

    # ------------------------------------------------------------------
    # Lectura (se lo deja a MatrizDispersa)
    # ------------------------------------------------------------------
    def get(self, fila, col):
        return self.matriz.get(fila, col)

    def cantidad(self):
        return self.matriz.cantidad()

    def iterar(self):
        return self.matriz.iterar()