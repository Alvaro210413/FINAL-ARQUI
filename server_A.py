import os
import random
import socket
from io import BytesIO
from PIL import Image

IPS = ["192.168.1.10", "140.22.1.5", "200.5.100.1", "192.168.1.50", "10.0.0.1"]
HOST = "127.0.0.1"

def enviar_img(host: str, port: int, nombre: str, ip_simulada: str, data: bytes, timeout: float = 10.0) -> None:
    
    if not isinstance(data, (bytes, bytearray)) or len(data) == 0:
        raise ValueError("`data` debe ser bytes y no puede estar vacío.")
    if not nombre or "\n" in nombre:
        raise ValueError("`nombre` no puede estar vacío ni contener saltos de línea.")
    if not ip_simulada or "\n" in ip_simulada:
        raise ValueError("`ip_simulada` no puede estar vacía ni contener saltos de línea.")

    header = f"NAME:{nombre}\nIP:{ip_simulada}\nSIZE:{len(data)}\n\n".encode("utf-8")

    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(header)
        sock.sendall(data)


def elegir_destino() -> int:
   
    destino = input("Destino (B/C): ").strip().upper()
    if destino == "B":
        return 8001
    elif destino == "C":
        return 8002
    else:
        print("Destino inválido. Usa 'B' o 'C'.")
        raise SystemExit(1)


def elegir_ip_simulada() -> str:
    
    return random.choice(IPS)

def elegir_imagen_aleatoria(images_dir: str = "images") -> str:
    
    if not os.path.isdir(images_dir):
        raise FileNotFoundError(f"La carpeta '{images_dir}' no existe. Crea 'images/' y añade las imágenes.")
    archivos = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
    if not archivos:
        raise FileNotFoundError(f"No hay archivos en '{images_dir}'. Añade al menos 1 imagen (.jpg/.png).")
    return random.choice(archivos)

def imagen_a_bytes(ruta: str, formato_forzado: str = "JPEG") -> bytes:
    
    img = Image.open(ruta).convert("RGB")
    buf = BytesIO()
    img.save(buf, format=formato_forzado)
    return buf.getvalue()

if __name__ == "__main__":
    try:
        port = elegir_destino()

        ip_sim = elegir_ip_simulada()

        nombre_archivo = elegir_imagen_aleatoria("images")
        ruta_archivo = os.path.join("images", nombre_archivo)

        data_bytes = imagen_a_bytes(ruta_archivo)  

        print("=== Enviando imagen ===")
        print(f"Destino (host:port): {HOST}:{port}")
        print(f"NAME : {nombre_archivo}")
        print(f"IP   : {ip_sim}")
        print(f"SIZE : {len(data_bytes)} bytes")

        enviar_img(HOST, port, nombre_archivo, ip_sim, data_bytes)

        print("Envío completado. Revisa en el servidor destino la imagen procesada (results/).")

    except Exception as e:
        print("Ocurrió un error:", repr(e))
        raise

    
    

    