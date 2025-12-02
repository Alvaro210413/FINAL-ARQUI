from concurrent.futures import ThreadPoolExecutor
import time


class FakeDatabase:
    def __init__(self):
        self.value = 0
    
    def update(self, name):
        print(f"[Thread {name}] Iniciando actualizacion")
        local_copy = self.value
        local_copy += 1
        time.sleep(0.1)
        self.value = local_copy
        print(f"[Thread {name}] Ha finalizado la actualizacion")


if __name__ == '__main__':
    workers = 5
    tasks = workers + 3

    db = FakeDatabase()
    print(f"Valor inicial de la base de datos: {db.value}")
    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for idx in range(tasks):
            executor.submit(db.update, idx)
    fin = time.perf_counter()    
    
    print(f"El valor final de la base de datos es: {db.value}")
    print(f"Tiempo total de ejecucion para hilos sin lock: {(fin - inicio):.6f} segundos")
