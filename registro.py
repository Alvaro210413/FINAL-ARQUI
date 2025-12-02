#!/usr/bin/env python3
import socket
import sys
import random
import time

HOST = "192.168.56.1"   # IP de tu servidor
PORT = 5000

def main():
    if len(sys.argv) != 2:
        print("Uso: python registro.py <codigoPUCP>")
        return

    codigo_base = sys.argv[1]

    # Generar 12 labs + examen 1 + examen 2 para el alumno principal
    labs = [random.randint(0, 20) for _ in range(12)]
    e1 = random.randint(0, 20)
    e2 = random.randint(0, 20)

    print("Cliente REGISTRO conectado al servidor.\n")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"REGISTRO\n")

        print("Registrando alumno principal:")
        print(f"Código: {codigo_base}")
        print(f"Labs : {labs}")
        print(f"E1   : {e1}")
        print(f"E2   : {e2}")
        print("\nEsperando confirmación...\n")

        # Mandar SOLO un registro (ya no los 200)
        # → el servidor se encargará de los siguientes 200 silenciosos
        data_str = " ".join(str(x) for x in labs)
        op = f"REGISTRAR {codigo_base} {data_str} {e1} {e2}\n"
        s.sendall(op.encode("utf-8"))

        # Esperar respuesta
        data = s.recv(4096)
        print("Respuesta recibida:")
        print(data.decode("utf-8"))
        print("-" * 60)

        time.sleep(0.5)

if __name__ == "__main__":
    main()
