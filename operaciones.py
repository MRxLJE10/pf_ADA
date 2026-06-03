# =============================================================================
# Clase: OperacionesAvanzadas
#
# Se implementa REGION_SUM, TRANSPOSE y TOP_K sobre un MatrizConIndices.
# TOP_K usa divide y venceras: O(N) promedio vs O(N log N)
# de un ordenamiento completo.
# =============================================================================

from hash_table     import MatrizDispersa
from indices        import IndicesAuxiliares


class OperacionesAvanzadas:
    """
    Agrupa las operaciones que requieren recorrer o transformar
    la matriz completa: REGION_SUM, TRANSPOSE y TOP_K.
    """

    def __init__(self, mc):
        """mc: instancia de MatrizConIndices."""
        self._mc = mc

    # ------------------------------------------------------------------
    # REGION_SUM
    # Complejidad: O(k) donde k = elementos no nulos en la region.
    # ------------------------------------------------------------------
    def region_sum(self, f1, c1, f2, c2):
        """Suma todos los valores no nulos dentro del rectangulo [f1..f2][c1..c2]."""
        total = 0
        for fila, col, valor in self._mc.matriz.iterar():
            if f1 <= fila <= f2 and c1 <= col <= c2:
                total += valor
        return total

    # ------------------------------------------------------------------
    # TRANSPOSE
    # Complejidad: O(N) — recorre todos los elementos una vez.
    # ------------------------------------------------------------------
    def transpose(self):
        """
        Intercambia filas y columnas de toda la matriz.
        Reconstruye MatrizDispersa e IndicesAuxiliares desde cero.
        """
        elementos = []
        for fila, col, valor in self._mc.matriz.iterar():
            elementos.append((col, fila, valor))

        nueva = MatrizDispersa(self._mc.matriz.cols, self._mc.matriz.filas)
        for fila, col, valor in elementos:
            nueva.set(fila, col, valor)

        self._mc.matriz  = nueva
        self._mc.indices = IndicesAuxiliares(self._mc.matriz)

    # ------------------------------------------------------------------
    # TOP_K  divide y venceras (quickselect)
    #
    # Problema : encontrar los k elementos de mayor valor.
    # Caso base: lista vacia, k=0, o k >= len(lista) -> devolver todo.
    # Division : elegir pivote central, partir en mayores/iguales/menores.
    # Conquista : recurrir solo sobre la particion necesaria.
    # Combinacion: concatenar particiones hasta completar k elementos.
    # Complejidad: O(N) promedio, O(N^2) peor caso (pivote desfavorable).
    # Ventaja vs solucion ingenua (ordenar todo): O(N log N) innecesario
    # cuando solo se necesitan los k mayores.
    # ------------------------------------------------------------------
    def _quickselect(self, lista, k):
        """Retorna los k elementos de mayor valor usando divide y venceras."""
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

    def _insertion_sort_desc(self, lista):
        """Ordena lista por valor descendente. Insertion sort propio O(k^2)."""
        for i in range(1, len(lista)):
            actual = lista[i]
            j = i - 1
            while j >= 0 and lista[j][2] < actual[2]:
                lista[j + 1] = lista[j]
                j -= 1
            lista[j + 1] = actual

    def top_k(self, k):
        """
        Retorna string con los k elementos de mayor valor en formato
        (fila,col,valor) ordenados de mayor a menor.
        """
        elementos = []
        for fila, col, valor in self._mc.matriz.iterar():
            elementos.append((fila, col, valor))

        seleccionados = self._quickselect(elementos, k)
        self._insertion_sort_desc(seleccionados)

        partes = []
        for fila, col, valor in seleccionados:
            partes.append(f"({fila},{col},{valor})")
        return " ".join(partes)