import asyncio
import time

SOCK_BUFFER = 1024
notas_num = 200
codigo_inicial = 20250001

NUM_CODIGOS = 5

def calc_nota_final(labs: list[int], e1: int, e2: int) -> float:
    """
    Calcula nota final a partir de las notas parciales de labs y examenes
    """
    prom_lab = sum(labs) / len(labs)

    nota_final = ((prom_lab * 5) + (e1 * 2.5) + (e2 * 2.5)) / 10

    return nota_final    


async def obten_notas_parciales(codigo: str) -> list[int]:
    reader, writer = await asyncio.open_connection("localhost", 5000)

    writer.write(codigo.encode("utf-8"))
    await writer.drain()

    data = await reader.read(SOCK_BUFFER)

    writer.close()
    await writer.wait_closed()

    data_str = data.decode("utf-8")
    notas = data_str.split(",")
    return [int(notas[i]) for i in range(1, len(notas))]


async def calc_una_nota(codigo: str):
    notas_parciales = await obten_notas_parciales(codigo)
    nota_final = calc_nota_final(notas_parciales[:12], notas_parciales[12], notas_parciales[13])

    return nota_final


async def main(codigos: list[str]):
    notas = await asyncio.gather(*(calc_una_nota(codigo) for codigo in codigos))

    return notas

if __name__ == '__main__':
    inicio = time.perf_counter() 
    
    codigos = list()
    for i in range(NUM_CODIGOS):
        codigo = codigo_inicial + i
        codigos.append(f"{codigo}")
    
    notas_finales = asyncio.run(main(codigos))

    nota_final_promedio = sum(notas_finales) / len(notas_finales)
    fin = time.perf_counter()

    t_ejecucion = fin - inicio

    print(f"El promedio de notas finales es: {nota_final_promedio}")
    print(f"Tiempo total de ejecucion: {t_ejecucion:.6f} segundos")
    print("fin del programa")