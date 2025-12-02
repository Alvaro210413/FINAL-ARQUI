import subprocess
import re
import matplotlib.pyplot as plt

def run_operaciones():
    print("Iniciando ejecución de ./operaciones...")
    result = subprocess.run(["./operaciones"], capture_output=True, text=True, check=True)
    # Si el que se va a leer es un archivo.py:
    # result = subprocess.run(["python3", "operaciones.py"], capture_output=True, text=True, check=True)

    print("Ejecución finalizada.")
    return result.stdout

def extract_times(text):
    cpu_hilo_times = {}
    cpu_proceso_times = {}
    io_hilo_times = {}
    io_proceso_times = {}

    pat_cpu = r"Tiempo de ejecución (secuencial|concurrente|paralela)(?: con (\d+) (hilos|procesos))?: ([0-9.]+)"
    pat_io  = r"I/O (secuencial|concurrente|paralela)(?: con (\d+) (hilos|procesos))?: ([0-9.]+)"

    for match in re.findall(pat_cpu, text):
        tipo = match[0]
        workers = match[1]
        worker_type = match[2]
        time = float(match[3])
        
        if tipo == "secuencial":
            cpu_hilo_times[1] = time 
            cpu_proceso_times[1] = time
        elif worker_type == "hilos":
            cpu_hilo_times[int(workers)] = time
        elif worker_type == "procesos":
            cpu_proceso_times[int(workers)] = time

    for match in re.findall(pat_io, text):
        tipo = match[0]
        workers = match[1]
        worker_type = match[2]
        time = float(match[3])
        
        if tipo == "secuencial":
            io_hilo_times[1] = time
            io_proceso_times[1] = time
        elif worker_type == "hilos":
            io_hilo_times[int(workers)] = time
        elif worker_type == "procesos":
            io_proceso_times[int(workers)] = time

    return cpu_hilo_times, cpu_proceso_times, io_hilo_times, io_proceso_times

output = run_operaciones()
cpu_hilo_times, cpu_proceso_times, io_hilo_times, io_proceso_times = extract_times(output)

cpu_workers = sorted(cpu_hilo_times.keys())
io_workers  = sorted(io_hilo_times.keys())

cpu_T_secuencial = cpu_hilo_times.get(1, 1.0)
io_T_secuencial = io_hilo_times.get(1, 1.0)

print("\n" + "="*30)
print("=== CÁLCULO DE SPEEDUP ===")
print("="*30)

print("\n--- SPEEDUP CPU-BOUND (Threading: Hilos) ---")
cpu_hilo_speedup = {w: cpu_T_secuencial / cpu_hilo_times[w] for w in cpu_workers if w in cpu_hilo_times}
for w in cpu_workers:
    if w in cpu_hilo_times:
        print(f"Hilos {w} → Tiempo: {cpu_hilo_times[w]:.6f}s | Speedup: {cpu_hilo_speedup.get(w, 0):.3f}")

print("\n--- SPEEDUP CPU-BOUND (Multiprocessing: Procesos) ---")
cpu_proceso_speedup = {w: cpu_T_secuencial / cpu_proceso_times[w] for w in cpu_workers if w in cpu_proceso_times}
for w in cpu_workers:
    if w in cpu_proceso_times:
        print(f"Procesos {w} → Tiempo: {cpu_proceso_times[w]:.6f}s | Speedup: {cpu_proceso_speedup.get(w, 0):.3f}")

print("\n--- SPEEDUP I/O-BOUND (Threading: Hilos) ---")
io_hilo_speedup = {w: io_T_secuencial / io_hilo_times[w] for w in io_workers if w in io_hilo_times}
for w in io_workers:
    if w in io_hilo_times:
        print(f"Hilos {w} → Tiempo: {io_hilo_times[w]:.6f}s | Speedup: {io_hilo_speedup.get(w, 0):.3f}")

print("\n--- SPEEDUP I/O-BOUND (Multiprocessing: Procesos) ---")
io_proceso_speedup = {w: io_T_secuencial / io_proceso_times[w] for w in io_workers if w in io_proceso_times}
for w in io_workers:
    if w in io_proceso_times:
        print(f"Procesos {w} → Tiempo: {io_proceso_times[w]:.6f}s | Speedup: {io_proceso_speedup.get(w, 0):.3f}")


print("\n" + "="*30)
print("=== GENERANDO GRÁFICAS ===")
print("="*30)

plt.figure(figsize=(10, 6))
plt.plot(cpu_workers, [cpu_hilo_times[w] for w in cpu_workers if w in cpu_hilo_times], marker='o', label="Threading (Hilos)", color='tab:blue')
plt.plot(cpu_workers, [cpu_proceso_times[w] for w in cpu_workers if w in cpu_proceso_times], marker='o', label="Multiprocessing (Procesos)", color='tab:orange')

plt.axhline(cpu_T_secuencial, color='gray', linestyle='--', label=f"Secuencial ({cpu_T_secuencial:.3f}s)")

plt.xlabel("Número de workers (hilos/procesos)")
plt.ylabel("Tiempo de ejecución (s)")
plt.title("CPU-bound: Threading vs Multiprocessing (tiempo vs número de workers)")
plt.grid(True)
plt.legend()
plt.savefig("cpu_bound_vs_workers.png")
print("Gráfica CPU-bound generada: cpu_bound_vs_workers.png")


plt.figure(figsize=(10, 6))
plt.plot(io_workers, [io_hilo_times[w] for w in io_workers if w in io_hilo_times], marker='o', label="Threading (Hilos)", color='tab:blue')
plt.plot(io_workers, [io_proceso_times[w] for w in io_workers if w in io_proceso_times], marker='o', label="Multiprocessing (Procesos)", color='tab:orange')

plt.axhline(io_T_secuencial, color='gray', linestyle='--', label=f"Secuencial ({io_T_secuencial:.3f}s)")

plt.xlabel("Número de workers (hilos/procesos)")
plt.ylabel("Tiempo de ejecución (s)")
plt.title("I/O-bound: Threading vs Multiprocessing (tiempo vs número de workers)")
plt.grid(True)
plt.legend()
plt.savefig("io_bound_vs_workers.png")
print("Gráfica I/O-bound generada: io_bound_vs_workers.png")
print("\nBenchmarking finalizado. Archivos de imagen generados en el mismo directorio.")


-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import subprocess           # Para ejecutar el programa C desde Python
import re                   # Expresiones regulares → extracción de tiempos
import matplotlib.pyplot as plt  # Para generar las gráficas


# =================================================================================
# 1. FUNCIÓN QUE EJECUTA ./operaciones Y CAPTURA TODA LA SALIDA DE TEXTO
# =================================================================================

def run_operaciones():
    """
    Ejecuta el programa compilado en C (./operaciones), captura toda su salida
    estándar y la retorna como texto. Esto permite analizar los tiempos que imprime.
    """
    print("Iniciando ejecución de ./operaciones...")

    # subprocess.run ejecuta el binario como si estuvieras en la terminal
    result = subprocess.run(
        ["./operaciones"],        # programa a ejecutar
        capture_output=True,      # captura la salida como texto
        text=True,                # convierte bytes → string automáticamente
        check=True                # lanza error si ./operaciones falla
    )

    print("Ejecución finalizada.")
    return result.stdout          # retorna TODO el output del programa C



# =================================================================================
# 2. FUNCIÓN PARA EXTRAER LOS TIEMPOS USANDO REGEX (CPU e IO)
# =================================================================================

def extract_times(text):
    """
    Busca en la salida del programa C todas las líneas que contengan tiempos.
    Clasifica los tiempos en 4 categorías:
      - CPU con hilos
      - CPU con procesos
      - IO con hilos
      - IO con procesos
    """

    cpu_hilo_times = {}      # Ej: {1: 3.5, 2: 2.1, 4: 1.4, ...}
    cpu_proceso_times = {}
    io_hilo_times = {}
    io_proceso_times = {}

    # Regex para CPU
    # Captura: tipo (secuencial, concurrente, paralela), workers, tipoWorker, tiempo
    pat_cpu = r"Tiempo de ejecución (secuencial|concurrente|paralela)(?: con (\d+) (hilos|procesos))?: ([0-9.]+)"

    # Regex para IO
    pat_io  = r"I/O (secuencial|concurrente|paralela)(?: con (\d+) (hilos|procesos))?: ([0-9.]+)"

    # ---------------------
    # EXTRAER CPU TIMES
    # ---------------------

    for match in re.findall(pat_cpu, text):
        tipo = match[0]          # secuencial / concurrente / paralela
        workers = match[1]       # número de workers (si aplica)
        worker_type = match[2]   # hilos o procesos
        time = float(match[3])   # tiempo encontrado

        if tipo == "secuencial":
            # Por conveniencia asignamos workers = 1 para secuencial
            cpu_hilo_times[1] = time
            cpu_proceso_times[1] = time

        elif worker_type == "hilos":
            cpu_hilo_times[int(workers)] = time

        elif worker_type == "procesos":
            cpu_proceso_times[int(workers)] = time


    # ---------------------
    # EXTRAER IO TIMES
    # ---------------------

    for match in re.findall(pat_io, text):
        tipo = match[0]
        workers = match[1]
        worker_type = match[2]
        time = float(match[3])

        if tipo == "secuencial":
            io_hilo_times[1] = time
            io_proceso_times[1] = time

        elif worker_type == "hilos":
            io_hilo_times[int(workers)] = time

        elif worker_type == "procesos":
            io_proceso_times[int(workers)] = time

    return cpu_hilo_times, cpu_proceso_times, io_hilo_times, io_proceso_times



# =================================================================================
# 3. EJECUTAR ./operaciones Y EXTRAER LOS TIEMPOS
# =================================================================================

output = run_operaciones()

cpu_hilo_times, cpu_proceso_times, io_hilo_times, io_proceso_times = extract_times(output)

# Ordenar workers para que los gráficos salgan bien
cpu_workers = sorted(cpu_hilo_times.keys())
io_workers  = sorted(io_hilo_times.keys())

# Guardamos tiempo secuencial de CPU y IO (worker=1)
cpu_T_secuencial = cpu_hilo_times.get(1, 1.0)
io_T_secuencial = io_hilo_times.get(1, 1.0)



# =================================================================================
# 4. CALCULAR SPEEDUP (T_secuencial / T_paralelo)
# =================================================================================

print("\n" + "="*30)
print("=== CÁLCULO DE SPEEDUP ===")
print("="*30)

# -------------------------------------
#  CPU – THREADING (HILOS)
# -------------------------------------

print("\n--- SPEEDUP CPU-BOUND (Threading: Hilos) ---")
cpu_hilo_speedup = {
    w: cpu_T_secuencial / cpu_hilo_times[w]
    for w in cpu_workers if w in cpu_hilo_times
}

for w in cpu_workers:
    if w in cpu_hilo_times:
        print(f"Hilos {w} → Tiempo: {cpu_hilo_times[w]:.6f}s | Speedup: {cpu_hilo_speedup[w]:.3f}")


# -------------------------------------
#  CPU – MULTIPROCESSING (PROCESOS)
# -------------------------------------

print("\n--- SPEEDUP CPU-BOUND (Multiprocessing: Procesos) ---")
cpu_proceso_speedup = {
    w: cpu_T_secuencial / cpu_proceso_times[w]
    for w in cpu_workers if w in cpu_proceso_times
}

for w in cpu_workers:
    if w in cpu_proceso_times:
        print(f"Procesos {w} → Tiempo: {cpu_proceso_times[w]:.6f}s | Speedup: {cpu_proceso_speedup[w]:.3f}")


# -------------------------------------
#  I/O – THREADING
# -------------------------------------

print("\n--- SPEEDUP I/O-BOUND (Threading: Hilos) ---")
io_hilo_speedup = {
    w: io_T_secuencial / io_hilo_times[w]
    for w in io_workers if w in io_hilo_times
}

for w in io_workers:
    if w in io_hilo_times:
        print(f"Hilos {w} → Tiempo: {io_hilo_times[w]:.6f}s | Speedup: {io_hilo_speedup[w]:.3f}")


# -------------------------------------
#  I/O – PROCESOS
# -------------------------------------

print("\n--- SPEEDUP I/O-BOUND (Multiprocessing: Procesos) ---")
io_proceso_speedup = {
    w: io_T_secuencial / io_proceso_times[w]
    for w in io_workers if w in io_proceso_times
}

for w in io_workers:
    if w in io_proceso_times:
        print(f"Procesos {w} → Tiempo: {io_proceso_times[w]:.6f}s | Speedup: {io_proceso_speedup[w]:.3f}")



# =================================================================================
# 5. GRÁFICAS: CPU BOUND
# =================================================================================

print("\n" + "="*30)
print("=== GENERANDO GRÁFICAS ===")
print("="*30)

plt.figure(figsize=(10, 6))

# Tiempo vs workers usando hilos
plt.plot(
    cpu_workers,
    [cpu_hilo_times[w] for w in cpu_workers],
    marker='o',
    label="Threading (Hilos)",
    color='tab:blue'
)

# Tiempo vs workers usando procesos
plt.plot(
    cpu_workers,
    [cpu_proceso_times[w] for w in cpu_workers],
    marker='o',
    label="Multiprocessing (Procesos)",
    color='tab:orange'
)

# Línea horizontal con el tiempo secuencial (referencia)
plt.axhline(
    cpu_T_secuencial,
    color='gray',
    linestyle='--',
    label=f"Secuencial ({cpu_T_secuencial:.3f}s)"
)

plt.xlabel("Número de workers (hilos/procesos)")
plt.ylabel("Tiempo de ejecución (s)")
plt.title("CPU-bound: Threading vs Multiprocessing (tiempo vs número de workers)")
plt.grid(True)
plt.legend()
plt.savefig("cpu_bound_vs_workers.png")

print("Gráfica CPU-bound generada: cpu_bound_vs_workers.png")



# =================================================================================
# 6. GRÁFICAS: IO BOUND
# =================================================================================

plt.figure(figsize=(10, 6))

plt.plot(
    io_workers,
    [io_hilo_times[w] for w in io_workers],
    marker='o',
    label="Threading (Hilos)",
    color='tab:blue'
)

plt.plot(
    io_workers,
    [io_proceso_times[w] for w in io_workers],
    marker='o',
    label="Multiprocessing (Procesos)",
    color='tab:orange'
)

plt.axhline(
    io_T_secuencial,
    color='gray',
    linestyle='--',
    label=f"Secuencial ({io_T_secuencial:.3f}s)"
)

plt.xlabel("Número de workers (hilos/procesos)")
plt.ylabel("Tiempo de ejecución (s)")
plt.title("I/O-bound: Threading vs Multiprocessing (tiempo vs número de workers)")
plt.grid(True)
plt.legend()
plt.savefig("io_bound_vs_workers.png")

print("Gráfica I/O-bound generada: io_bound_vs_workers.png")
print("\nBenchmarking finalizado. Archivos de imagen generados en el mismo directorio.")
