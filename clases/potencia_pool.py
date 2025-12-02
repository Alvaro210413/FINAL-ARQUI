import time
from multiprocessing import Pool, cpu_count

N = 200_000
proc_num = 224


def calc_potencia(base: int, exp: int = N // proc_num) -> int:
    potencia = 1

    while exp > 0:
        potencia *= base
        exp -= 1
    

    return potencia


if __name__ == '__main__':
    procesos = list()
    workers = cpu_count() * 2
    inicio = time.perf_counter()
    p = Pool(processes=workers)
    res = p.map(calc_potencia, [N] * proc_num)
    p.close()
    p.join()
    fin = time.perf_counter()

    t_ejecucion = fin - inicio
    print(f"Tiempo total: {t_ejecucion:.6f} segundos")

