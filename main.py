# =============================================================================
# main.py
# =============================================================================

from matriz_sistema import MatrizConIndices
from operaciones    import OperacionesAvanzadas


# -----------------------------------------------------------------------------
# Lectura
# -----------------------------------------------------------------------------
def leer_entrada(ruta="entrada.txt"):
    """
    Lee entrada.txt y retorna (mc, ops):
        mc  -> MatrizConIndices ya cargado con los N valores iniciales
        ops -> lista de strings con las Q operaciones
    """
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
    """Procesa cada operacion y retorna lista de strings con los resultados."""
    ops_avanzadas = OperacionesAvanzadas(mc)
    resultados    = []

    for op in ops:
        partes = op.split()
        nombre = partes[0].upper()
        resultado = _despachar(nombre, partes, mc, ops_avanzadas)
        resultados.append(resultado)

    return resultados


def _despachar(nombre, partes, mc, ops_avanzadas):
    """Dirige cada operacion al metodo correspondiente."""
    if nombre == "GET":
        fila, col = int(partes[1]), int(partes[2])
        return f"GET {fila} {col} = {mc.get(fila, col)}"

    elif nombre == "SET":
        fila, col, valor = int(partes[1]), int(partes[2]), int(partes[3])
        mc.set(fila, col, valor)
        return f"SET {fila} {col} = OK"

    elif nombre == "DELETE":
        fila, col = int(partes[1]), int(partes[2])
        return f"DELETE {fila} {col} = {mc.delete(fila, col)}"

    elif nombre == "ROW_SUM":
        fila = int(partes[1])
        return f"ROW_SUM {fila} = {mc.indices.row_sum(fila)}"

    elif nombre == "COL_SUM":
        col = int(partes[1])
        return f"COL_SUM {col} = {mc.indices.col_sum(col)}"

    elif nombre == "DENSITY":
        return _formatear_density(mc.indices.density())

    elif nombre == "REGION_SUM":
        f1, c1, f2, c2 = int(partes[1]), int(partes[2]), int(partes[3]), int(partes[4])
        return f"REGION_SUM {f1} {c1} {f2} {c2} = {ops_avanzadas.region_sum(f1, c1, f2, c2)}"

    elif nombre == "TRANSPOSE":
        ops_avanzadas.transpose()
        return "TRANSPOSE = OK"

    elif nombre == "TOP_K":
        k = int(partes[1])
        return f"TOP_K {k} = {ops_avanzadas.top_k(k)}"

    else:
        return f"{nombre} = NO_IMPLEMENTADO"


def _formatear_density(d):
    """Formatea el valor de densidad como string."""
    if d == 0.0:
        return "DENSITY = 0.0"
    return f"DENSITY = {d:.10e}"


# -----------------------------------------------------------------------------
# Escritura
# -----------------------------------------------------------------------------
def escribir_salida(resultados, ruta="salida.txt"):
    """Escribe los resultados en salida.txt, uno por linea."""
    with open(ruta, "w") as f:
        f.write("\n".join(resultados) + "\n")


# -----------------------------------------------------------------------------
# Punto de entrada
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    mc, ops       = leer_entrada("entrada.txt")
    resultados    = ejecutar_operaciones(mc, ops)
    escribir_salida(resultados, "salida.txt")
    print(f"Listo: {len(resultados)} operaciones procesadas.")