# =============================================================================
# Punto de entrada del proyecto — integra MatrizDispersa + IndicesAuxiliares + OperacionesAvanzadas
# =============================================================================

from hash_table import MatrizDispersa
from indices import IndicesAuxiliares
from ops_avanzadas import OperacionesAvanzadas


# -----------------------------------------------------------------------------
# Wrapper que sincroniza matriz + indices en cada mutacion
# -----------------------------------------------------------------------------

class MatrizConIndices:
    """
    Envuelve MatrizDispersa e IndicesAuxiliares juntos.
    Garantiza que cada SET y DELETE actualice ambas estructuras atomicamente.
    """

    def __init__(self, filas, cols):
        self.matriz  = MatrizDispersa(filas, cols)
        self.indices = None  # se inicializa despues de cargar los datos
        self.ops_avanzadas = None

    def inicializar_indices(self):
        """
        Construye los indices auxiliares a partir del estado actual de la matriz.
        Llamar una sola vez despues de cargar todos los valores iniciales.
        """
        self.indices = IndicesAuxiliares(self.matriz)
        self.ops_avanzadas = OperacionesAvanzadas(self)

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
# Lectura de entrada.txt
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
        mc.matriz.set(int(p[0]), int(p[1]), int(p[2]))  # carga directa sin indices todavia

    # Construir indices una sola vez con todos los datos iniciales
    mc.inicializar_indices()

    Q = int(lineas[idx]); idx += 1
    ops = []
    for _ in range(Q):
        if idx < len(lineas) and lineas[idx].strip():
            ops.append(lineas[idx].strip())
        idx += 1

    return mc, ops


# -----------------------------------------------------------------------------
# Ejecucion de operaciones
# -----------------------------------------------------------------------------

def ejecutar_operaciones(mc, ops):
    resultados = []

    for op in ops:
        partes = op.split()
        nombre = partes[0].upper()

        if nombre == "GET":
            fila, col = int(partes[1]), int(partes[2])
            val = mc.get(fila, col)
            resultados.append(f"GET {fila} {col} = {val}")

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
            resultado = mc.indices.row_sum(fila)
            resultados.append(f"ROW_SUM {fila} = {resultado}")

        elif nombre == "COL_SUM":
            col = int(partes[1])
            resultado = mc.indices.col_sum(col)
            resultados.append(f"COL_SUM {col} = {resultado}")

        elif nombre == "DENSITY":
            d = mc.indices.density()
            if d == 0.0:
                resultados.append("DENSITY = 0.0")
            else:
                resultados.append(f"DENSITY = {d:.10e}")

        elif nombre in ("REGION_SUM", "TOP_K", "TRANSPOSE"):
            resultado = mc.ops_avanzadas.ejecutar(nombre, partes[1:])
            resultados.append(resultado)

        else:
            resultados.append(f"{nombre} = OPERACION_DESCONOCIDA")

    return resultados


# -----------------------------------------------------------------------------
# Escritura de salida.txt
# -----------------------------------------------------------------------------

def escribir_salida(resultados, ruta="salida.txt"):
    with open(ruta, "w") as f:
        f.write("\n".join(resultados) + "\n")


# -----------------------------------------------------------------------------
# Entrada principal
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    mc, ops = leer_entrada("entrada.txt")
    resultados = ejecutar_operaciones(mc, ops)
    escribir_salida(resultados, "salida.txt")
    print(f"Listo: {len(resultados)} operaciones procesadas.")