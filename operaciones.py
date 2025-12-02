#!/usr/bin/env python3
import csv
import time
import threading
import multiprocessing
from collections import Counter

# ============================================================
# CONFIGURACIÓN
# ============================================================
N_LABS = 8
TOTAL_REP = 1000

# Estas listas se llenan en main()
labs_arr = []
ex1_arr = []
ex2_arr = []

# ============================================================
# FUNCIONES ESTADÍSTICAS
# ============================================================
def safe_mean(vals):
    if not vals:
        return 0
    return sum(vals) / len(vals)

def min_val(vals):
    return min(vals) if vals else 0

def max_val(vals):
    return max(vals) if vals else 0

def moda(vals):
    return Counter(vals).most_common(1)[0][0] if vals else 0

def nota_final(labs, ex1, ex2):
    p = safe_mean(labs)
    return (6*p + 2*ex1 + 2*ex2) / 10.0

# ============================================================
# PROCESAR POR COLUMNA
# ============================================================
def procesar_por_columna():
    total = len(labs_arr)

    # LAB1 a LAB8
    for col in range(N_LABS):
        columna = [labs_arr[i][col] for i in range(total)]

        p = safe_mean(columna)
        mn = min_val(columna)
        mx = max_val(columna)
        mo = moda(columna)

    # EX1
    col_ex1 = ex1_arr[:]
    p1 = safe_mean(col_ex1)
    mn1 = min_val(col_ex1)
    mx1 = max_val(col_ex1)
    mo1 = moda(col_ex1)

    # EX2
    col_ex2 = ex2_arr[:]
    p2 = safe_mean(col_ex2)
    mn2 = min_val(col_ex2)
    mx2 = max_val(col_ex2)
    mo2 = moda(col_ex2)

    # Nota final por fila
    for i in range(total):
        nf = nota_final(labs_arr[i], ex1_arr[i], ex2_arr[i])

def procesar_todos():
    procesar_por_columna()

# ============================================================
# CPU – SECUENCIAL
# ============================================================
def ejecucion_secuencial():
    t0 = time.perf_counter()
    for _ in range(TOTAL_REP):
        procesar_todos()
    t1 = time.perf_counter()
    print(f"Tiempo de ejecución secuencial: {t1 - t0:.6f}")

# ============================================================
# CPU – THREADING
# ============================================================
def worker_hilo(reps):
    for _ in range(reps):
        procesar_todos()

def ejecucion_concurrente(n_hilos):
    reps = TOTAL_REP // n_hilos
    hilos = []

    t0 = time.perf_counter()

    for _ in range(n_hilos):
        h = threading.Thread(target=worker_hilo, args=(reps,))
        h.start()
        hilos.append(h)

    for h in hilos:
        h.join()

    t1 = time.perf_counter()
    print(f"Tiempo de ejecución concurrente con {n_hilos} hilos: {t1 - t0:.6f}")

# ============================================================
# CPU – PROCESOS (WINDOWS SAFE VERSION)
# ============================================================

# Muy importante: cada proceso debe recargar el dataset
def cargar_dataset():
    global labs_arr, ex1_arr, ex2_arr

    labs_arr = []
    ex1_arr = []
    ex2_arr = []

    with open("notas_alumnos.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            labs_arr.append(list(map(float, row[1:1+N_LABS])))
            ex1_arr.append(float(row[1+N_LABS]))
            ex2_arr.append(float(row[2+N_LABS]))

def worker_proceso(reps):
    cargar_dataset()  # <<<<<< CLAVE PARA QUE NO ESTÉ VACÍO
    for _ in range(reps):
        procesar_todos()

def ejecucion_paralela(n_proc):
    reps = TOTAL_REP // n_proc
    procesos = []

    t0 = time.perf_counter()

    for _ in range(n_proc):
        p = multiprocessing.Process(target=worker_proceso, args=(reps,))
        p.start()
        procesos.append(p)

    for p in procesos:
        p.join()

    t1 = time.perf_counter()

    print(f"Tiempo de ejecución paralela con {n_proc} procesos: {t1 - t0:.6f}")

# ============================================================
# I/O BOUND
# ============================================================
def tarea_io():
    with open("notas_alumnos.csv", "r") as f:
        for _ in f:
            pass

def io_secuencial():
    t0 = time.perf_counter()
    for _ in range(TOTAL_REP):
        tarea_io()
    t1 = time.perf_counter()
    print(f"I/O secuencial: {t1 - t0:.6f}")

# THREADS
def worker_io_hilo(reps):
    for _ in range(reps):
        tarea_io()

def io_concurrente(n_hilos):
    reps = TOTAL_REP // n_hilos
    hilos = []

    t0 = time.perf_counter()
    for _ in range(n_hilos):
        h = threading.Thread(target=worker_io_hilo, args=(reps,))
        h.start()
        hilos.append(h)
    for h in hilos:
        h.join()
    t1 = time.perf_counter()

    print(f"I/O concurrente con {n_hilos} hilos: {t1 - t0:.6f}")

# PROCESOS (SIN LAMBDA)
def worker_io_proceso(reps):
    for _ in range(reps):
        tarea_io()

def io_paralela(n_proc):
    reps = TOTAL_REP // n_proc
    procesos = []

    t0 = time.perf_counter()
    for _ in range(n_proc):
        p = multiprocessing.Process(target=worker_io_proceso, args=(reps,))
        p.start()
        procesos.append(p)
    for p in procesos:
        p.join()
    t1 = time.perf_counter()

    print(f"I/O paralela con {n_proc} procesos: {t1 - t0:.6f}")

# ============================================================
# MAIN
# ============================================================
def main():
    # Cargar dataset 1 vez para secuencial y threading
    cargar_dataset()

    print("Total alumnos cargados:", len(labs_arr))

    print("\n=== CPU BOUND ===")
    ejecucion_secuencial()

    for w in range(2, 20):
        ejecucion_concurrente(w)

    for w in range(2, 20):
        ejecucion_paralela(w)

    print("\n=== I/O BOUND ===")
    io_secuencial()

    for w in range(2, 20):
        io_concurrente(w)

    for w in range(2, 20):
        io_paralela(w)

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")  # WINDOWS OBLIGATORIO
    main()
