import socket
import time


SOCK_BUFFER = 1024


def calc_nota_final(labs: list[int], e1: int, e2: int) -> float:
    """
    Calcula nota final a partir de las notas parciales de labs y examenes
    """
    prom_lab = sum(labs) / len(labs)

    nota_final = ((prom_lab * 5) + (e1 * 2.5) + (e2 * 2.5)) / 10

    return nota_final    


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("localhost", 5000)

    print(f"Conectando al servidor en {server_address[0]}:{server_address[1]}")

    inicio_io = time.perf_counter()
    sock.connect(server_address)

    codigo = "20250051"
    sock.sendall(codigo.encode("utf-8"))
    data = sock.recv(SOCK_BUFFER)

    data_str = data.decode("utf-8")

    print(f"Recibido: {data_str}")

    sock.close()
    fin_io = time.perf_counter()

    inicio_proceso = time.perf_counter()
    notas = data_str.split(",")
    labs = [int(notas[i]) for i in range(1, 13)]
    e1 = int(notas[13])
    e2 = int(notas[14])

    nota_final = calc_nota_final(labs, e1, e2)
    fin_proceso = time.perf_counter()
    print(f"La nota final del alumno con codigo {codigo}, es {nota_final:.2f}")
    
    print(f"El tiempo de I/O: {(fin_io - inicio_io):.6f} segundos")
    print(f"El tiempo de procesamiento: {(fin_proceso - inicio_proceso):.6f} segundos")
