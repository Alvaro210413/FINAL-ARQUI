#!/usr/bin/env python3
import socket
import threading
import queue
import csv
import random
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000
RUTA_CSV = "notas.csv"

# Lock global para proteger acceso concurrente al CSV
csv_lock = threading.Lock()

# Colas para cada tipo de operación
consulta_queue = queue.Queue()
mod_queue = queue.Queue()
registro_queue = queue.Queue()

# ================================================================
#  UTILIDADES DE LECTURA / ESCRITURA DEL CSV
# ================================================================

def leer_csv():
    """Retorna todas las filas del CSV como lista de diccionarios."""
    with csv_lock:
        with open(RUTA_CSV, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

def escribir_csv(filas):
    """Sobrescribe el CSV con el contenido actualizado."""
    with csv_lock:
        with open(RUTA_CSV, "w", newline="", encoding="utf-8") as f:
            if not filas:
                return
            writer = csv.DictWriter(f, fieldnames=filas[0].keys())
            writer.writeheader()
            writer.writerows(filas)

def buscar_alumno(codigo):
    """Busca un alumno y retorna dict o None."""
    filas = leer_csv()
    for row in filas:
        if row["codigo"] == str(codigo):
            return row
    return None

def actualizar_nota(codigo, curso_idx, nueva_nota):
    """Modifica una nota específica en labs o exámenes."""
    filas = leer_csv()
    actualizado = False
    for row in filas:
        if row["codigo"] == str(codigo):
            if 1 <= curso_idx <= 12:
                row[f"lab{curso_idx}"] = str(nueva_nota)
            elif curso_idx == 13:
                row["e1"] = str(nueva_nota)
            elif curso_idx == 14:
                row["e2"] = str(nueva_nota)
            actualizado = True
            break

    if actualizado:
        escribir_csv(filas)
    return actualizado

def registrar_nuevo(codigo, labs, e1, e2):
    """Registra un nuevo alumno."""
    filas = leer_csv()

    filas.append({
        "codigo": codigo,
        **{f"lab{i+1}": str(labs[i]) for i in range(12)},
        "e1": str(e1),
        "e2": str(e2)
    })

    escribir_csv(filas)


# ================================================================
#  WORKERS DE CONSULTA / MODIFICACIÓN / REGISTRO
# ================================================================

def worker_consulta():
    """Procesa las consultas BUSCAR usando una cola."""
    while True:
        codigo, conn = consulta_queue.get()
        if codigo is None:
            break

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # <<< AGREGA ESTE PRINT >>>
        print(f"[Hilo-consulta] BUSCAR {codigo} a las {ts}")

        row = buscar_alumno(codigo)

        if row is None:
            respuesta = f"[CONSULTA] Codigo {codigo} NO encontrado\n{ts}\n"
        else:
            labs = [float(row[f"lab{i}"]) for i in range(1, 13)]
            e1 = float(row["e1"])
            e2 = float(row["e2"])
            final = sum(labs)/12 * 0.6 + e1 * 0.2 + e2 * 0.2

            respuesta = (
                f"[CONSULTA] {codigo} labs={labs} e1={e1} e2={e2} final={final:.2f}\n"
                f"{ts}\n"
            )

        try:
            conn.sendall(respuesta.encode("utf-8"))
        except:
            pass

        consulta_queue.task_done()



def worker_modificacion():
    """Procesa CORREGIR <codigo> <idx> <nueva_nota>."""
    while True:
        codigo, idx, nota, conn = mod_queue.get()
        if codigo is None:
            break

        exito = actualizar_nota(codigo, idx, nota)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if exito:
            print(f"[Hilo-escritura] CORREGIR {codigo} {idx} {nota} a las {ts}")
            resp = f"[MODIFICACION] CORREGIDO {codigo} {idx} {nota}\n{ts}\n"
        else:
            resp = f"[MODIFICACION] Código {codigo} NO encontrado\n{ts}\n"

        try:
            conn.sendall(resp.encode("utf-8"))
        except:
            pass

        mod_queue.task_done()


def worker_registro():
    """Procesa REGISTRAR <codigo> ..."""
    while True:
        codigo, labs, e1, e2, conn = registro_queue.get()
        if codigo is None:
            break

        registrar_nuevo(codigo, labs, e1, e2)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log en el servidor
        print(f"[Hilo-escritura] REGISTRAR {codigo} con labs={labs} e1={e1} e2={e2} a las {ts}")

        resp = f"[REGISTRO] Registrado {codigo}\n{ts}\n"
        try:
            conn.sendall(resp.encode("utf-8"))
        except:
            pass

        registro_queue.task_done()


# ================================================================
#  MANEJO DE CLIENTES (CONSULTA, MODIFICACION, REGISTRO)
# ================================================================

def handle_cliente_consulta(conn, addr):
    print(f"Cliente de consulta conectado")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            partes = data.decode().strip().split()
            if len(partes) == 2 and partes[0].upper() == "BUSCAR":
                codigo = partes[1]
                consulta_queue.put((codigo, conn))
            else:
                conn.sendall(b"Comando invalido. Use: BUSCAR <codigo>\n")
    except:
        pass
    finally:
        print("Cliente de consulta desconectado")
        conn.close()


def handle_cliente_mod(conn, addr):
    print("Cliente de modificacion conectado")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            partes = data.decode().strip().split()
            if len(partes) == 4 and partes[0].upper() == "CORREGIR":
                codigo = partes[1]
                idx = int(partes[2])
                nota = int(partes[3])
                mod_queue.put((codigo, idx, nota, conn))
            else:
                conn.sendall(b"Comando invalido. Use: CORREGIR <codigo> <idx> <nota>\n")
    except:
        pass
    finally:
        print("Cliente de modificacion desconectado")
        conn.close()


def handle_cliente_registro(conn, addr):
    print("Cliente de registro conectado")
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            partes = data.decode().strip().split()
            if partes[0].upper() == "REGISTRAR" and len(partes) == 1 + 1 + 12 + 2:
                codigo = partes[1]
                labs = list(map(int, partes[2:14]))
                e1 = int(partes[14])
                e2 = int(partes[15])

                registro_queue.put((codigo, labs, e1, e2, conn))
            else:
                conn.sendall(b"Formato invalido para REGISTRAR.\n")
    except:
        pass
    finally:
        print("Cliente de registro desconectado")
        conn.close()


def handle_client(conn, addr):
    try:
        tipo = conn.recv(1024).decode().strip().upper()
        if tipo == "CONSULTA":
            handle_cliente_consulta(conn, addr)
        elif tipo == "MODIFICACION":
            handle_cliente_mod(conn, addr)
        elif tipo == "REGISTRO":
            handle_cliente_registro(conn, addr)
        else:
            conn.sendall(b"Tipo de cliente no soportado.\n")
            conn.close()
    except:
        conn.close()


# ================================================================
# SERVIDOR PRINCIPAL
# ================================================================

def main():
    # Lanzar workers en paralelo
    threading.Thread(target=worker_consulta, daemon=True).start()
    threading.Thread(target=worker_modificacion, daemon=True).start()
    threading.Thread(target=worker_registro, daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor master escuchando en {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
