# =============================================================================
# Tests exhaustivos para IndicesAuxiliares
# Cubre casos normales, casos limite y sincronizacion con la matriz
# =============================================================================
from hash_table import MatrizDispersa
from indices import IndicesAuxiliares


def matriz_con_indices(filas, cols, datos):
    """Helper: crea MatrizDispersa, carga datos y construye indices."""
    m = MatrizDispersa(filas, cols)
    for fila, col, valor in datos:
        m.set(fila, col, valor)
    return m, IndicesAuxiliares(m)


def ok(nombre):
    print(f"  ✓ {nombre}")

def falla(nombre, esperado, obtenido):
    print(f"  ✗ {nombre}")
    print(f"      esperado:  {esperado}")
    print(f"      obtenido:  {obtenido}")


# -----------------------------------------------------------------------------
# Test 1: ROW_SUM basico
# -----------------------------------------------------------------------------
def test_row_sum_basico():
    print("\n[1] ROW_SUM basico")
    m, idx = matriz_con_indices(100, 100, [
        (1, 1, 5),
        (1, 2, 7),
        (1, 3, 3),
        (2, 1, 10),
    ])

    r = idx.row_sum(1)
    if r == 15:
        ok("ROW_SUM fila 1 = 15")
    else:
        falla("ROW_SUM fila 1", 15, r)

    r = idx.row_sum(2)
    if r == 10:
        ok("ROW_SUM fila 2 = 10")
    else:
        falla("ROW_SUM fila 2", 10, r)


# -----------------------------------------------------------------------------
# Test 2: ROW_SUM fila vacia
# -----------------------------------------------------------------------------
def test_row_sum_vacia():
    print("\n[2] ROW_SUM fila vacia")
    m, idx = matriz_con_indices(100, 100, [
        (1, 1, 5),
    ])
    r = idx.row_sum(99)
    if r == 0:
        ok("ROW_SUM fila inexistente = 0")
    else:
        falla("ROW_SUM fila inexistente", 0, r)


# -----------------------------------------------------------------------------
# Test 3: COL_SUM basico
# -----------------------------------------------------------------------------
def test_col_sum_basico():
    print("\n[3] COL_SUM basico")
    m, idx = matriz_con_indices(100, 100, [
        (1,  100, 7),
        (5,  100, 3),
        (10, 100, 2),
        (1,  200, 99),
    ])

    r = idx.col_sum(100)
    if r == 12:
        ok("COL_SUM col 100 = 12")
    else:
        falla("COL_SUM col 100", 12, r)

    r = idx.col_sum(200)
    if r == 99:
        ok("COL_SUM col 200 = 99")
    else:
        falla("COL_SUM col 200", 99, r)


# -----------------------------------------------------------------------------
# Test 4: COL_SUM columna vacia
# -----------------------------------------------------------------------------
def test_col_sum_vacia():
    print("\n[4] COL_SUM columna vacia")
    m, idx = matriz_con_indices(100, 100, [(1, 1, 5)])
    r = idx.col_sum(500)
    if r == 0:
        ok("COL_SUM columna inexistente = 0")
    else:
        falla("COL_SUM columna inexistente", 0, r)


# -----------------------------------------------------------------------------
# Test 5: Sincronizacion con SET nuevo valor
# -----------------------------------------------------------------------------
def test_sincronizacion_set_nuevo():
    print("\n[5] Sincronizacion: SET nuevo elemento")
    m, idx = matriz_con_indices(100, 100, [
        (1, 1, 5),
        (1, 2, 3),
    ])

    # Antes del SET
    r_antes = idx.row_sum(1)

    # SET nuevo elemento en fila 1
    valor_anterior = m.get(1, 99)
    m.set(1, 99, 10)
    idx.on_set(1, 99, 10, valor_anterior)

    r_despues = idx.row_sum(1)
    if r_despues == r_antes + 10:
        ok(f"ROW_SUM fila 1 actualizado: {r_antes} -> {r_despues}")
    else:
        falla("ROW_SUM tras SET nuevo", r_antes + 10, r_despues)

    # COL_SUM de la nueva columna
    r_col = idx.col_sum(99)
    if r_col == 10:
        ok("COL_SUM col 99 = 10 tras SET")
    else:
        falla("COL_SUM col 99 tras SET", 10, r_col)


# -----------------------------------------------------------------------------
# Test 6: Sincronizacion con SET actualizacion
# -----------------------------------------------------------------------------
def test_sincronizacion_set_actualizar():
    print("\n[6] Sincronizacion: SET actualizar valor existente")
    m, idx = matriz_con_indices(100, 100, [
        (1, 1, 5),
        (1, 2, 3),
    ])

    # Actualizar (1,1) de 5 a 20
    valor_anterior = m.get(1, 1)
    m.set(1, 1, 20)
    idx.on_set(1, 1, 20, valor_anterior)

    r = idx.row_sum(1)
    if r == 23:  # 20 + 3
        ok("ROW_SUM fila 1 = 23 tras actualizar (1,1) a 20")
    else:
        falla("ROW_SUM tras actualizar", 23, r)

    r_col = idx.col_sum(1)
    if r_col == 20:
        ok("COL_SUM col 1 = 20 tras actualizar")
    else:
        falla("COL_SUM col 1 tras actualizar", 20, r_col)


# -----------------------------------------------------------------------------
# Test 7: Sincronizacion con DELETE
# -----------------------------------------------------------------------------
def test_sincronizacion_delete():
    print("\n[7] Sincronizacion: DELETE")
    m, idx = matriz_con_indices(100, 100, [
        (1, 1, 5),
        (1, 2, 3),
        (2, 1, 8),
    ])

    # Eliminar (1,1)
    m.delete(1, 1)
    idx.on_delete(1, 1)

    r_row = idx.row_sum(1)
    if r_row == 3:
        ok("ROW_SUM fila 1 = 3 tras DELETE (1,1)")
    else:
        falla("ROW_SUM tras DELETE", 3, r_row)

    r_col = idx.col_sum(1)
    if r_col == 8:
        ok("COL_SUM col 1 = 8 tras DELETE (1,1)")
    else:
        falla("COL_SUM col 1 tras DELETE", 8, r_col)


# -----------------------------------------------------------------------------
# Test 8: DELETE elemento inexistente (no debe romper indices)
# -----------------------------------------------------------------------------
def test_delete_inexistente():
    print("\n[8] DELETE elemento que no existe")
    m, idx = matriz_con_indices(100, 100, [
        (1, 1, 5),
    ])

    res = m.delete(99, 99)
    if res == "NOT_FOUND":
        idx.on_delete(99, 99)  # no debe lanzar excepcion
        ok("DELETE inexistente retorna NOT_FOUND sin romper indices")
    else:
        falla("DELETE inexistente", "NOT_FOUND", res)


# -----------------------------------------------------------------------------
# Test 9: DENSITY
# -----------------------------------------------------------------------------
def test_density():
    print("\n[9] DENSITY")
    m, idx = matriz_con_indices(1000000000, 1000000000, [
        (1, 1, 5),
        (1, 100, 7),
        (500, 300, 9),
        (1000, 1000, 2),
        (200000, 10, 11),
        (999999999, 999999999, 15),
    ])

    d = idx.density()
    esperado = 6 / (1_000_000_000 * 1_000_000_000)
    if abs(d - esperado) < 1e-30:
        ok(f"DENSITY = {d:.6e} (correcto)")
    else:
        falla("DENSITY", esperado, d)


# -----------------------------------------------------------------------------
# Test 10: Matriz vacia
# -----------------------------------------------------------------------------
def test_matriz_vacia():
    print("\n[10] Matriz sin valores no nulos")
    m, idx = matriz_con_indices(1000, 1000, [])

    r = idx.row_sum(1)
    if r == 0:
        ok("ROW_SUM en matriz vacia = 0")
    else:
        falla("ROW_SUM en matriz vacia", 0, r)

    r = idx.col_sum(1)
    if r == 0:
        ok("COL_SUM en matriz vacia = 0")
    else:
        falla("COL_SUM en matriz vacia", 0, r)

    d = idx.density()
    if d == 0.0:
        ok("DENSITY en matriz vacia = 0.0")
    else:
        falla("DENSITY en matriz vacia", 0.0, d)


# -----------------------------------------------------------------------------
# Test 11: Valores negativos
# -----------------------------------------------------------------------------
def test_valores_negativos():
    print("\n[11] Valores negativos")
    m, idx = matriz_con_indices(100, 100, [
        (1, 1,  10),
        (1, 2, -3),
        (1, 3,  5),
    ])

    r = idx.row_sum(1)
    if r == 12:
        ok("ROW_SUM con valores negativos = 12")
    else:
        falla("ROW_SUM con negativos", 12, r)


# -----------------------------------------------------------------------------
# Test 12: Coordenadas grandes (hasta 10^9)
# -----------------------------------------------------------------------------
def test_coordenadas_grandes():
    print("\n[12] Coordenadas grandes (hasta 10^9)")
    m, idx = matriz_con_indices(1_000_000_000, 1_000_000_000, [
        (999_999_999, 999_999_999, 15),
        (999_999_999, 1,           3),
        (1,           999_999_999, 7),
    ])

    r = idx.row_sum(999_999_999)
    if r == 18:
        ok("ROW_SUM fila 999999999 = 18")
    else:
        falla("ROW_SUM fila grande", 18, r)

    r = idx.col_sum(999_999_999)
    if r == 22:
        ok("COL_SUM col 999999999 = 22")
    else:
        falla("COL_SUM col grande", 22, r)


# -----------------------------------------------------------------------------
# Test 13: Ejemplo del enunciado
# -----------------------------------------------------------------------------
def test_ejemplo_enunciado():
    print("\n[13] Ejemplo del enunciado")
    m, idx = matriz_con_indices(1_000_000_000, 1_000_000_000, [
        (1,         1,         5),
        (1,         100,       7),
        (500,       300,       9),
        (1000,      1000,      2),
        (200000,    10,        11),
        (999999999, 999999999, 15),
    ])

    # ROW_SUM 1 = 5 + 7 = 12
    r = idx.row_sum(1)
    if r == 12:
        ok("ROW_SUM 1 = 12")
    else:
        falla("ROW_SUM 1", 12, r)

    # COL_SUM 100 = 7
    r = idx.col_sum(100)
    if r == 7:
        ok("COL_SUM 100 = 7")
    else:
        falla("COL_SUM 100", 7, r)

    # SET 1 100 20 -> actualizar
    valor_anterior = m.get(1, 100)
    m.set(1, 100, 20)
    idx.on_set(1, 100, 20, valor_anterior)

    # ROW_SUM 1 ahora = 5 + 20 = 25
    r = idx.row_sum(1)
    if r == 25:
        ok("ROW_SUM 1 = 25 tras SET 1 100 20")
    else:
        falla("ROW_SUM 1 tras SET", 25, r)

    # COL_SUM 100 ahora = 20
    r = idx.col_sum(100)
    if r == 20:
        ok("COL_SUM 100 = 20 tras SET")
    else:
        falla("COL_SUM 100 tras SET", 20, r)


# -----------------------------------------------------------------------------
# Ejecutar todos los tests
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  Tests IndicesAuxiliares")
    print("=" * 55)

    test_row_sum_basico()
    test_row_sum_vacia()
    test_col_sum_basico()
    test_col_sum_vacia()
    test_sincronizacion_set_nuevo()
    test_sincronizacion_set_actualizar()
    test_sincronizacion_delete()
    test_delete_inexistente()
    test_density()
    test_matriz_vacia()
    test_valores_negativos()
    test_coordenadas_grandes()
    test_ejemplo_enunciado()

    print("\n" + "=" * 55)
    print("  Fin de tests")
    print("=" * 55)