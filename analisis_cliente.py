import socket

SOCK_BUFFER = 1024

if __name__ == "__main__":

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# IP de la PC: 192.168.35.147
    server_address = ("192.168.56.1", 5000)

    print(f"Conectando al servidor en {server_address[0]}:{server_address[1]}")
#-----------------------------------------------------------------------------------------------------------------
    
    sock.connect(server_address)

    msg = input("Consulta: ")
    sock.sendall(msg.encode("utf-8"))
    respuesta = sock.recv(SOCK_BUFFER)

    respuesta_str = respuesta.decode("utf-8")
    print(respuesta_str)

    sock.close()
#-----------------------------------------------------------------------------------------------------------------

   
