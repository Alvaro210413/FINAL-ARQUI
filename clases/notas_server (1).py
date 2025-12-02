import socket

SOCK_BUFFER = 1024

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


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("0.0.0.0", 5000)

    print(f"Iniciando el servidor en {server_address[0]}:{server_address[1]}")

    sock.bind(server_address)

    sock.listen(10)

    while True:
        print("Esperando conexiones...")

        conn, addr = sock.accept()

        print(f"Conexión establecida desde {addr[0]}:{addr[1]}")

        try:
            while True:
                data = conn.recv(SOCK_BUFFER)
                if data:
                    print(f"Recibido: {data.decode('utf-8')}")
                    cod = data.decode("utf-8")
                    fila_notas = busca_fila(cod)
                    conn.sendall(fila_notas.encode("utf-8"))
                else:
                    print("No hay mas datos.")
                    break
        except ConnectionResetError:
            print("El cliente cerró la conexión abruptamente.")
        finally:
            print("Cerrando la conexión.")
            conn.close()
