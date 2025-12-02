#!/usr/bin/env python3
import socket
import sys
import time

HOST = "192.168.56.1"   # Cambia si tu server está en otra IP
PORT = 5000

def main():
    if len(sys.argv) != 4:
        print("Uso: python modificacion.py <codigo> <indice> <nueva_nota>")
        sys.exit(1)

    codigo = sys.argv[1]
    indice = sys.argv[2]       # número de lab o examen
    nueva = sys.argv[3]        # nueva nota

    comando = f"CORREGIR {codigo} {indice} {nueva}\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # identificarnos
        s.sendall(b"MODIFICACION\n")
        print("Cliente MODIFICACIÓN conectado al servidor.\n")

        print(f"Enviando operación: {comando.strip()}")
        s.sendall(comando.encode("utf-8"))

        # esperar respuesta
        data = s.recv(4096)
        print("Respuesta recibida:")
        print(data.decode("utf-8"))
        print("-" * 60)

        time.sleep(0.2)

if __name__ == "__main__":
    main()
