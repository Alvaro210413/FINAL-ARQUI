import time
from multiprocessing import Process


def calc_potencia(base: int, exp: int) -> int:
    potencia = 1

    while exp > 0:
        potencia *= base
        exp -= 1
    

    return potencia


if __name__ == '__main__':
    N = 200_000
    procesos = list()
    proc_num = 16
    inicio = time.perf_counter()
    for _ in range(proc_num):
        p = Process(target=calc_potencia, args=(N, N // proc_num))
        p.start()
        procesos.append(p)

    for p in procesos:
        p.join()

    fin = time.perf_counter()

    t_ejecucion = fin - inicio
    print(f"Tiempo total: {t_ejecucion:.6f} segundos")

