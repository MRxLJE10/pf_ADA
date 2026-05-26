
# Motor Algorítmico para Procesamiento Eficiente de Matrices Dispersas

Proyecto Final — Análisis y Diseño de Algoritmos I  
Universidad — 2026-I

---

## Integrantes

| Nombre| Codigo |
|---------|--------|
| Mariana Rios Coronado | 2459759 |
| Juan Sebastian Perez Cruz | 2459371 |
| Victor Murillo Goyes | 2459569 |
| Juan Felipe Aristizabal Davalos | 2459364 |

---

## Descripción general

El sistema procesa una matriz dispersa de dimensiones hasta 10^9 x 10^9 sin construirla en memoria. Solo almacena los valores no nulos usando una tabla hash propia. Lee operaciones desde `entrada.txt` y escribe los resultados en `salida.txt`.

---

## Estructura del proyecto

```
pf_ADA/
├── hash_table.py       # MatrizDispersa — tabla hash con sondeo lineal
├── indices.py          # IndicesAuxiliares — índices por fila y columna
├── ops_avanzadas.py    # OperacionesAvanzadas — REGION_SUM, TOP_K, TRANSPOSE
├── main.py             # Punto de entrada — integra todos los módulos
├── entrada.txt         # Datos de entrada
├── salida.txt          # Resultados generados automáticamente
├── test_indices.py     # Tests de IndicesAuxiliares
└── .gitignore
```

---

## Correr el programa:

```bash
python main.py
```

* El resultado queda en `salida.txt`.

---
