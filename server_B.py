import os
import socket
import time
from io import BytesIO
from PIL import Image

HOST = "0.0.0.0"
PORT = 8001
SOCK_BUFFER = 4096  

def leer_encabezado(conn) -> tuple[dict, bytes]:
    
    buffer = bytearray()
    delim = b"\n\n"
    while True:
        chunk = conn.recv(SOCK_BUFFER)
        if not chunk:
            break
        buffer.extend(chunk)
        idx = buffer.find(delim)
        if idx != -1:
            header_bytes = bytes(buffer[:idx])         
            leftover = bytes(buffer[idx + len(delim):])  
            
            texto = header_bytes.decode("utf-8", errors="replace")
            headers = {}
            for line in texto.splitlines():
                if ":" not in line:
                    continue
                k, v = line.split(":", 1)
                headers[k.strip().upper()] = v.strip()
            return headers, leftover
    raise ValueError("Encabezado incompleto o conexión cerrada antes de \\n\\n.")

def leer_exactos(conn, total_bytes: int, primeros: bytes = b"") -> bytes:
    
    data = bytearray(primeros)
    faltan = total_bytes - len(data)
    while faltan > 0:
        chunk = conn.recv(min(SOCK_BUFFER, faltan))
        if not chunk:
            raise ConnectionError("Conexión cerrada antes de recibir todos los bytes del payload.")
        data.extend(chunk)
        faltan -= len(chunk)
    return bytes(data)

def procesar_grayscale(y_bytes: bytes) -> bytes:
    
    with Image.open(BytesIO(y_bytes)) as img:
        
        img_gray = img.convert("L")
        out = BytesIO()
        img_gray.save(out, format="JPEG")
        return out.getvalue()

def asegurar_directorio(path: str):
    os.makedirs(path, exist_ok=True)

if __name__ == "__main__":
    asegurar_directorio("results")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (HOST, PORT)
    print(f"Iniciando el servidor en {server_address[0]}:{server_address[1]}")
    sock.bind(server_address)
    sock.listen(2)

    while True:
        print("Esperando conexiones...")
        conn, addr = sock.accept()
        print(f"Conexión establecida desde {addr[0]}:{addr[1]}")

        try:
            # Leer encabezado
            headers, leftover = leer_encabezado(conn)

            nombre = headers.get("NAME", "desconocido")
            ip_sim = headers.get("IP", "0.0.0.0")
            try:
                size = int(headers.get("SIZE", "0"))
            except ValueError:
                size = 0

            if size <= 0:
                raise ValueError("SIZE inválido en el encabezado.")

            print("=== Encabezado recibido ===")
            print(f"NAME : {nombre}")
            print(f"IP   : {ip_sim}")
            print(f"SIZE : {size} bytes")

            # Leer el payload binario completo
            payload = leer_exactos(conn, size, primeros=leftover)

            # Procesar imagen en escala de grises
            start = time.time()
            procesada = procesar_grayscale(payload)
            dur_ms = int((time.time() - start) * 1000)

            # Guardar imagen en results/
            ts = time.strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(nombre))[0]
            out_name = f"B_{base_name}_{ip_sim.replace('.', '-')}_{ts}.jpg"
            out_path = os.path.join("results", out_name)

            with open(out_path, "wb") as f:
                f.write(procesada)

            print(f"Imagen procesada (grayscale) guardada en: {out_path} ({dur_ms} ms)")


        except Exception as e:
            print(f"Error durante el manejo de la conexión: {e}")
        finally:
            print("Cerrando la conexión.")
            conn.close()
