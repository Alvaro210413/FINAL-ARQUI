import numpy as np
import time

M = 5000
N = 5000


def mult_vector(x: list[np.int32], y: list[np.int32]) -> np.int32:
    suma = 0

    for i in range(len(x)):
        suma += x[i] * y[i]
    
    return suma


if __name__ == '__main__':
    resultados = list()

    mat_M = np.random.randint(100, size=(M, N))
    vector_A = np.random.randint(100, size=(N, ))

    inicio = time.perf_counter()
    for vector in mat_M:
        resultados.append(mult_vector(vector, vector_A))

    resultado = sum(resultados)
    fin = time.perf_counter()

    t_ejecucion = fin - inicio

    print(f"El tiempo total de ejecucion es: {t_ejecucion:.6f} segundos")
