import socket
import numpy as np

SOCK_BUFFER = 1024

def prom_ventas(tabla: list[str],tipo_producto: str)-> str:

    suma = 0.0
    cant_prod = 0

    for idx in range(1,len(tabla)):
        fila = tabla[idx]
        fila_separado = fila.split(",")
        # Cantidad de columnas N = 10:
        if len(fila_separado)<10:
            continue

        if fila_separado[2]==tipo_producto:
            suma = suma + float(fila_separado[8])
            cant_prod = cant_prod + 1

    promedio_ventas = suma/cant_prod

    return f"El promedio de ventas de {tipo_producto} es {promedio_ventas:.2f}."

def mejor_canal(tabla: list[str])-> str:

    cant_off = 0
    cant_on = 0
    suma_off = 0.0
    suma_on = 0.0

    for idx in range(1,len(tabla)):
        fila = tabla[idx]
        fila_separado = fila.split(",")
        # Cantidad de columnas N = 10:
        if len(fila_separado)<10:
            continue

        if fila_separado[3]=="Offline":
            cant_off = cant_off + 1
            suma_off = suma_off + float(fila_separado[8])
        else:
            cant_on = cant_on + 1
            suma_on = suma_on + float(fila_separado[8])


    if cant_on>cant_off:
        canal_venta = "Online"
        return f"El mejor canal de venta fue {canal_venta} con {cant_on} ventas y con un total de {suma_on:.2f} soles."
    else:
        canal_venta = "Offline"
        return f"El mejor canal de venta fue {canal_venta} con {cant_off} ventas y con un total de {suma_off:.2f} soles."

def desv_estandar(tabla: list[str],tipo_producto: str)-> str:

    ventas = []
    for idx in range(1,len(tabla)):
        fila = tabla[idx]
        fila_separado = fila.split(",")
        # Cantidad de columnas N = 10:
        if len(fila_separado)<10:
            continue

        if fila_separado[2]==tipo_producto:
            ventas.append(float(fila_separado[8]))
        
    desviacion_estandar = np.std(ventas)

    return f"La desviación estándar de {tipo_producto} es {desviacion_estandar:.2f}."

def ventas_sup_prom(tabla: list[str])-> str:

    ventas = []
    # Con {} se obtiene un "historial" para cuando se quiera guardar en uno de los espacios
    # lo que uno quiera, sirve para clientes en este caso:
    ventas_clientes = {}
    # {"cliente1": suma_total_ventas  "cliente2": suma_total_ventas  "cliente3": suma_total_ventas ...}

    # Promedio de ventas de la empresa:
    for idx in range(1,len(tabla)):
        fila = tabla[idx]
        fila_separado = fila.split(",")

        if len(fila_separado)<10:
            continue
        
        venta = float(fila_separado[8])

        ventas.append(float(fila_separado[8]))

        cliente = fila_separado[1]

        if cliente not in ventas_clientes:
            ventas_clientes[cliente] = venta
        else:
            ventas_clientes[cliente] = ventas_clientes[cliente] + venta


    prom_ventas_empresa = float(sum(ventas)/len(ventas))

    cantidad_clientes = 0
    # Cantidad de clientes superior al promedio:
    for cliente, total in ventas_clientes.items():
        if total > prom_ventas_empresa:
            cantidad_clientes = cantidad_clientes + 1

    return f"Los clientes con ventas superiores al promedio son: {cantidad_clientes}."

def distrib_ventas(tabla: list[str],tipo_producto: str)-> str:

    ventas = []

    for idx in range(1,len(tabla)):
        fila = tabla[idx]
        fila_separado = fila.split(",")

        if len(fila_separado)<10:
            continue

        if fila_separado[2]==tipo_producto:
            ventas.append(float(fila_separado[8]))

    media = np.mean(ventas)
    mediana = np.median(ventas)
    minimo = min(ventas)
    maximo = max(ventas)       

    return f"Distribución de ventas de {tipo_producto}: media {media:.2f}, mediana {mediana:.2f}, mínimo {minimo:.2f}, máximo {maximo:.2f}."

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("0.0.0.0", 5000)

    print(f"Iniciando el servidor en {server_address[0]}:{server_address[1]}")

    sock.bind(server_address)

    sock.listen(1)

    # Después de sock.listen(1) se coloca para leer el archivo de ventas.csv 
    # y separamos las líneas en una lista llamada tabla 
    with open("orders_data_large.csv", "r") as f:
        contenido = f.read()
    tabla = contenido.split("\n")

    mensaje_final = []
   
    while True:
        print("Esperando conexiones...")

        conn, addr = sock.accept()

        print(f"Conexión establecida desde {addr[0]}:{addr[1]}") 

        try:
            while True:
                data = conn.recv(SOCK_BUFFER)
                consulta = data.decode("utf-8")

                if consulta == "salir":
                    print("Cliente se desconectó")
                    with open("reporte.txt", "w", encoding="utf-8") as f:
                        f.write("\n".join(mensaje_final))
                    break

                if data:
                    # Promedio de ventas de un tipo de producto especificado
                    if consulta.startswith("promedio de ventas de "):
                        consulta_partes = consulta.split(" ")
                        tipo_producto = " ".join(consulta_partes[4:])
                        promedio_ventas = prom_ventas(tabla,tipo_producto)
                        respuesta = promedio_ventas
                        conn.sendall(promedio_ventas.encode("utf-8"))
                      
                    # Mejor canal de venta
                    elif consulta == "mejor canal de venta":
                        mejor_canal_ventas = mejor_canal(tabla)
                        respuesta = mejor_canal_ventas
                        conn.sendall(mejor_canal_ventas.encode("utf-8"))

                    # Desviación estándar de ventas 
                    elif consulta.startswith("desviación estándar de ventas de "):
                        consulta_parte = consulta.split(" ")
                        tipo_producto = " ".join(consulta_parte[5:])
                        desviacion_stand = desv_estandar(tabla,tipo_producto)
                        respuesta = desviacion_stand
                        conn.sendall(desviacion_stand.encode("utf-8"))

                    # Cantidad de clientes con ventas superiores al promedio
                    elif consulta == "cantidad de clientes con ventas superiores al promedio":
                        cant_clientes = ventas_sup_prom(tabla)
                        respuesta = cant_clientes
                        conn.sendall(cant_clientes.encode("utf-8"))

                    # Distribución de ventas por tipo de producto
                    elif consulta.startswith("distribución de ventas de "):
                        consulta_partes = consulta.split(" ")
                        tipo_producto = " ".join(consulta_partes[4:])
                        distribucion_ventas = distrib_ventas(tabla,tipo_producto)
                        respuesta = distribucion_ventas
                        conn.sendall(distribucion_ventas.encode("utf-8"))

                    mensaje_final.append(respuesta)

                else:
                    print("No hay mas datos.")
                    break
        except ConnectionResetError:
            print("El cliente cerró la conexión abruptamente.")
        finally:
            print("Cerrando la conexión.")
            conn.close()