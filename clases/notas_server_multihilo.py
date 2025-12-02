import socket
from threading import Thread
from typing import Union

SOCK_BUFFER = 1024

contador_clientes = 0


def busca_fila(codigo: str) -> str:
    """
    Busca una fila correspondiente a las notas, referidas por codigo de alumno en el archivo 'notas.csv'
    """
    try:
        with open("notas.csv", "r") as f:
            contenido = f.read()
    except FileNotFoundError:
        print("Archivo no existe")
        return ""
    tabla = contenido.split("\n")

    notas = ""

    for idx in range(1, len(tabla)):
        fila = tabla[idx]
        if codigo in fila:
            return fila
    
    return notas            


def handle_client(c_sock: socket.socket, c_addr: Union[str, int]):
    global contador_clientes
    print(f"Conexión establecida desde {c_addr[0]}:{c_addr[1]}")

    contador_clientes += 1
    print(f"Numero de clientes con|ectados concurrentemente: {contador_clientes}")
    try:
        while True:
            data = c_sock.recv(SOCK_BUFFER)
            if data:
                print(f"Recibido: {data.decode('utf-8')}")
                cod = data.decode("utf-8")
                fila_notas = busca_fila(cod)
                c_sock.sendall(fila_notas.encode("utf-8"))
            else:
                print("No hay mas datos.")
                break
    except ConnectionResetError:
        print("El cliente cerró la conexión abruptamente.")
    finally:
        print("Cerrando la conexión.")
        contador_clientes -= 1
        c_sock.close()


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("0.0.0.0", 5000)

    print(f"Iniciando el servidor en {server_address[0]}:{server_address[1]}")

    sock.bind(server_address)

    sock.listen(10)

    while True:
        print("Esperando conexiones...")

        conn, addr = sock.accept()

        t = Thread(target=handle_client, args=(conn, addr))
        t.start()
        
