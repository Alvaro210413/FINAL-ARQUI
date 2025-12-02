import time

from calc_notas_completo import calc_notas_full
from calc_notas_individual import calc_notas_individual


def corre_uno(f) -> float:
    """
    Ejecuta la funcion que pasamos como argumento y retorna el tiempo de ejecucion
    """
    inicio = time.perf_counter()
    f()
    fin = time.perf_counter()

    return fin - inicio


def benchmark(func, warmup: bool, iter: int, op: str = "avg") -> float:
    ejecuciones = list()

    if warmup:
        corre_uno(func)
    
    for _ in range(iter):
        res = corre_uno(func)
        ejecuciones.append(res)
    
    match op:
        case "avg":
            r = sum(ejecuciones) / len(ejecuciones)
        case "median":
            ejecuciones.sort()
            r = ejecuciones[len(ejecuciones) // 2]
        case _:
            print("No se escogio una operacion valida, realizando promedio")
            r = sum(ejecuciones) / len(ejecuciones)

    return r

if __name__ == '__main__':
    res_completo = benchmark(calc_notas_full, True, 10)
    res_individual = benchmark(calc_notas_individual, True, 10)

    print(f"Tiempo de ejecucion completo: {res_completo:.6f} segundos\tTiempo de ejecucion individual: {res_individual:.6f} segundos")
