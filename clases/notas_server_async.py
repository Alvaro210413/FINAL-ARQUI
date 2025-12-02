import asyncio

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
    


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    print("Cliente conectado")

    try:
        while True:
            data = await reader.read(SOCK_BUFFER)
            if data:
                print(f"Recibido: {data.decode('utf-8')}")
                cod = data.decode("utf-8")
                fila_notas = busca_fila(cod)
                writer.write(fila_notas.encode("utf-8"))
                await writer.drain()
            else:
                print("No hay mas datos.")
                break
    except ConnectionResetError:
        print("El cliente cerro la conexion abruptamente")
    finally:
        writer.close()
        await writer.wait_closed()
    
    print("Conexion cerrada")


async def main():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 5000)

    async with server:
        print(f"Iniciando el servidor en 0.0.0.0:5000")
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
