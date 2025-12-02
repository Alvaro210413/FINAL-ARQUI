#!/usr/bin/env python3
import socket
import sys

HOST = "127.0.0.1"     # o la IP del servidor si estás en red
PORT = 5000

def main():
    if len(sys.argv) != 2:
        print("Uso: python consulta.py <codigo>")
        return

    codigo = sys.argv[1]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # IDENTIFICARSE
        s.sendall(b"CONSULTA\n")
        print("Cliente CONSULTA conectado al servidor.\n")

        # ENVIAR COMANDO BUSCAR
        comando = f"BUSCAR {codigo}\n"
        print(f"Enviando consulta por alumno {codigo}...")
        s.sendall(comando.encode("utf-8"))

        # RECIBIR RESPUESTA
        data = s.recv(4096)
        if not data:
            print("Servidor cerró la conexión.")
            return

        print("\nRespuesta recibida:")
        print(data.decode("utf-8"))

        print("-" * 50)


if __name__ == "__main__":
    main()
