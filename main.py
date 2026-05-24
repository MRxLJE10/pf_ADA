from hash_table import MatrizDispersa
from indices import IndicesAuxiliares


class MatrizConIndices:
    def __init__(self, filas, cols):
        self.matriz  = MatrizDispersa(filas, cols)
        self.indices = None

    def inicializar_indices(self):
        self.indices = IndicesAuxiliares(self.matriz)

    def set(self, fila, col, valor):
        valor_anterior = self.matriz.get(fila, col)
        resultado = self.matriz.set(fila, col, valor)
        if self.indices is not None:
            if valor == 0:
                self.indices.on_delete(fila, col)
            else:
                self.indices.on_set(fila, col, valor, valor_anterior)
        return resultado

    def get(self, fila, col):
        return self.matriz.get(fila, col)

    def delete(self, fila, col):
        resultado = self.matriz.delete(fila, col)
        if self.indices is not None and resultado == "OK":
            self.indices.on_delete(fila, col)
        return resultado

    def cantidad(self):
        return self.matriz.cantidad()

    def iterar(self):
        return self.matriz.iterar()


# -----------------------------------------------------------------------------
# REGION_SUM: suma valores no nulos dentro del rectangulo [f1..f2][c1..c2]
# Usa iterar_fila por cada fila del indice; solo recorre filas que existan.
# Complejidad: O(k) donde k = elementos no nulos en la region.
# -----------------------------------------------------------------------------
def region_sum(mc, f1, c1, f2, c2):
    total = 0
    filas_vistas = set()
    for fila, col, valor in mc.matriz.iterar():
        if f1 <= fila <= f2 and c1 <= col <= c2:
            if fila not in filas_vistas:
                filas_vistas.add(fila)
    del filas_vistas
    for fila, col, valor in mc.matriz.iterar():
        if f1 <= fila <= f2 and c1 <= col <= c2:
            total += valor
    return total


# -----------------------------------------------------------------------------
# TRANSPOSE: voltea (fila,col,valor) -> (col,fila,valor)
# Reconstruye los indices desde cero al final. O(N).
# -----------------------------------------------------------------------------
def transpose(mc):
    elementos = []
    for fila, col, valor in mc.matriz.iterar():
        elementos.append((col, fila, valor))

    nueva = MatrizDispersa(mc.matriz.cols, mc.matriz.filas)
    for fila, col, valor in elementos:
        nueva.set(fila, col, valor)

    mc.matriz = nueva
    mc.indices = IndicesAuxiliares(mc.matriz)


# -----------------------------------------------------------------------------
# Quickselect propio para TOP_K — divide y venceras
#
# Problema: encontrar los k elementos de mayor valor en la lista.
# Caso base: lista de 1 elemento o k >= len(lista) -> retornar todo.
# Division: elegir pivote, partir en mayores / iguales / menores.
# Combinacion: si la particion izquierda tiene >= k elementos, buscar alli;
#              si no, tomar todos los mayores y buscar en los iguales/menores.
# Complejidad promedio: O(N), peor caso O(N^2) con pivote malo.
# Mejor que ordenar: O(N log N) no es necesario cuando solo queremos los top k.
# -----------------------------------------------------------------------------
def _quickselect_topk(lista, k):
    if k <= 0:
        return []
    if k >= len(lista):
        return lista[:]

    pivote_val = lista[len(lista) // 2][2]
    mayores  = []
    iguales  = []
    menores  = []
    for item in lista:
        v = item[2]
        if v > pivote_val:
            mayores.append(item)
        elif v == pivote_val:
            iguales.append(item)
        else:
            menores.append(item)

    if len(mayores) >= k:
        return _quickselect_topk(mayores, k)
    elif len(mayores) + len(iguales) >= k:
        return mayores + iguales[:k - len(mayores)]
    else:
        resto = _quickselect_topk(menores, k - len(mayores) - len(iguales))
        return mayores + iguales + resto


def top_k(mc, k):
    elementos = []
    for fila, col, valor in mc.matriz.iterar():
        elementos.append((fila, col, valor))

    seleccionados = _quickselect_topk(elementos, k)

    seleccionados.sort(key=lambda x: -x[2])

    resultado = ""
    for fila, col, valor in seleccionados:
        resultado += f"({fila},{col},{valor}) "
    return resultado.strip()


# -----------------------------------------------------------------------------
# Lectura
# -----------------------------------------------------------------------------
def leer_entrada(ruta="entrada.txt"):
    with open(ruta, "r") as f:
        lineas = f.read().split("\n")

    idx = 0
    partes = lineas[idx].split(); idx += 1
    F, C, N = int(partes[0]), int(partes[1]), int(partes[2])

    mc = MatrizConIndices(F, C)

    for _ in range(N):
        p = lineas[idx].split(); idx += 1
        mc.matriz.set(int(p[0]), int(p[1]), int(p[2]))

    mc.inicializar_indices()

    Q = int(lineas[idx]); idx += 1
    ops = []
    for _ in range(Q):
        if idx < len(lineas) and lineas[idx].strip():
            ops.append(lineas[idx].strip())
        idx += 1

    return mc, ops


# -----------------------------------------------------------------------------
# Ejecucion
# -----------------------------------------------------------------------------
def ejecutar_operaciones(mc, ops):
    resultados = []

    for op in ops:
        partes = op.split()
        nombre = partes[0].upper()

        if nombre == "GET":
            fila, col = int(partes[1]), int(partes[2])
            resultados.append(f"GET {fila} {col} = {mc.get(fila, col)}")

        elif nombre == "SET":
            fila, col, valor = int(partes[1]), int(partes[2]), int(partes[3])
            mc.set(fila, col, valor)
            resultados.append(f"SET {fila} {col} = OK")

        elif nombre == "DELETE":
            fila, col = int(partes[1]), int(partes[2])
            res = mc.delete(fila, col)
            resultados.append(f"DELETE {fila} {col} = {res}")

        elif nombre == "ROW_SUM":
            fila = int(partes[1])
            resultados.append(f"ROW_SUM {fila} = {mc.indices.row_sum(fila)}")

        elif nombre == "COL_SUM":
            col = int(partes[1])
            resultados.append(f"COL_SUM {col} = {mc.indices.col_sum(col)}")

        elif nombre == "DENSITY":
            d = mc.indices.density()
            if d == 0.0:
                resultados.append("DENSITY = 0.0")
            else:
                resultados.append(f"DENSITY = {d:.10e}")

        elif nombre == "REGION_SUM":
            f1, c1, f2, c2 = int(partes[1]), int(partes[2]), int(partes[3]), int(partes[4])
            resultados.append(f"REGION_SUM {f1} {c1} {f2} {c2} = {region_sum(mc, f1, c1, f2, c2)}")

        elif nombre == "TRANSPOSE":
            transpose(mc)
            resultados.append("TRANSPOSE = OK")

        elif nombre == "TOP_K":
            k = int(partes[1])
            resultados.append(f"TOP_K {k} = {top_k(mc, k)}")

        else:
            resultados.append(f"{nombre} = NO_IMPLEMENTADO")

    return resultados


# -----------------------------------------------------------------------------
# Salida
# -----------------------------------------------------------------------------
def escribir_salida(resultados, ruta="salida.txt"):
    with open(ruta, "w") as f:
        f.write("\n".join(resultados) + "\n")


if __name__ == "__main__":
    mc, ops = leer_entrada("entrada.txt")
    resultados = ejecutar_operaciones(mc, ops)
    escribir_salida(resultados, "salida.txt")
    print(f"Listo: {len(resultados)} operaciones procesadas.")