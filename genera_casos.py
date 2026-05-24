import random

def generar(ruta, F, C, N, operaciones):
    with open(ruta, "w") as f:
        f.write(f"{F} {C} {N}\n")
        usados = set()
        escritos = 0
        while escritos < N:
            fila = random.randint(1, F)
            col  = random.randint(1, C)
            if (fila, col) not in usados:
                usados.add((fila, col))
                valor = random.randint(-1000, 1000)
                while valor == 0:
                    valor = random.randint(-1000, 1000)
                f.write(f"{fila} {col} {valor}\n")
                escritos += 1
        f.write(f"{len(operaciones)}\n")
        for op in operaciones:
            f.write(op + "\n")
    print(f"Generado: {ruta}  (N={N}, Q={len(operaciones)})")


# ---- caso pequeño (exactamente el del enunciado) ----
generar("entrada_pequeno.txt", 1_000_000_000, 1_000_000_000, 6, [
    "GET 500 300",
    "ROW_SUM 1",
    "COL_SUM 100",
    "SET 1 100 20",
    "GET 1 100",
    "REGION_SUM 1 1 1000 1000",
    "TOP_K 3",
])

# ---- caso mediano ----
random.seed(42)
filas_med  = [random.randint(1, 10**9) for _ in range(500)]
cols_med   = [random.randint(1, 10**9) for _ in range(500)]
ops_med = []
for i in range(200):
    f, c = filas_med[i % 500], cols_med[i % 500]
    ops_med.append(f"GET {f} {c}")
for i in range(50):
    ops_med.append(f"ROW_SUM {filas_med[i]}")
for i in range(50):
    ops_med.append(f"COL_SUM {cols_med[i]}")
f1,c1 = min(filas_med[:10]), min(cols_med[:10])
f2,c2 = max(filas_med[:10]), max(cols_med[:10])
ops_med.append(f"REGION_SUM {f1} {c1} {f2} {c2}")
ops_med.append("TOP_K 10")
ops_med.append("DENSITY")
ops_med.append("TRANSPOSE")
ops_med.append(f"ROW_SUM {cols_med[0]}")
generar("entrada_mediano.txt", 10**9, 10**9, 1000, ops_med)

# ---- caso grande ----
random.seed(99)
N_grande = 50000
Q_grande = 1000
ops_grande = []
for _ in range(300):
    f = random.randint(1, 10**9)
    c = random.randint(1, 10**9)
    ops_grande.append(f"GET {f} {c}")
for _ in range(200):
    f = random.randint(1, 10**9)
    ops_grande.append(f"ROW_SUM {f}")
for _ in range(200):
    c = random.randint(1, 10**9)
    ops_grande.append(f"COL_SUM {c}")
for _ in range(100):
    f1 = random.randint(1, 5*10**8)
    c1 = random.randint(1, 5*10**8)
    f2 = f1 + random.randint(0, 10**6)
    c2 = c1 + random.randint(0, 10**6)
    ops_grande.append(f"REGION_SUM {f1} {c1} {f2} {c2}")
for _ in range(100):
    f = random.randint(1, 10**9)
    c = random.randint(1, 10**9)
    v = random.randint(1, 9999)
    ops_grande.append(f"SET {f} {c} {v}")
for _ in range(50):
    f = random.randint(1, 10**9)
    c = random.randint(1, 10**9)
    ops_grande.append(f"DELETE {f} {c}")
ops_grande.append("TOP_K 20")
ops_grande.append("TOP_K 1")
ops_grande.append("DENSITY")
ops_grande.append("TRANSPOSE")
ops_grande.append("TOP_K 5")
ops_grande += [f"ROW_SUM {random.randint(1,10**9)}" for _ in range(Q_grande - len(ops_grande))]
generar("entrada_grande.txt", 10**9, 10**9, N_grande, ops_grande)

# ---- casos limite ----
# Matriz vacia
generar("entrada_vacia.txt", 10**9, 10**9, 0, [
    "GET 1 1",
    "ROW_SUM 1",
    "COL_SUM 1",
    "REGION_SUM 1 1 1000 1000",
    "TOP_K 3",
    "DENSITY",
    "TRANSPOSE",
])

# Un solo elemento
generar("entrada_uno.txt", 10**9, 10**9, 1, [
    "GET 500000000 500000000",
    "ROW_SUM 500000000",
    "TOP_K 1",
    "TOP_K 5",
    "TRANSPOSE",
    "COL_SUM 500000000",
])

# Valores negativos y SET que sobreescribe
generar("entrada_negativos.txt", 1000, 1000, 5, [
    "ROW_SUM 1",
    "SET 1 1 -999",
    "ROW_SUM 1",
    "TOP_K 3",
    "DELETE 1 1",
    "DELETE 1 1",
    "REGION_SUM 1 1 1000 1000",
])
