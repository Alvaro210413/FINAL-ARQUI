import threading
import time
import random

class BankAccount:
    def __init__(self, balance):
        self.balance = balance
        self.lock = threading.Lock()

    def pay(self, amount):
        with self.lock:
            if self.balance >= amount:
                time.sleep(0.001)
                self.balance -= amount
                return True
            return False


def worker_pago(empresa, pago, resultados, idx):
    if empresa.pay(pago):
        resultados[idx] = 1
    else:
        resultados[idx] = 0


def main():
    empresa = BankAccount(50000)

    salarios = [random.randint(5000, 8000) for _ in range(100)]
    resultados = [0] * 100

    threads = []
    start = time.time()

    for i in range(100):
        t = threading.Thread(target=worker_pago, args=(empresa, salarios[i], resultados, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end = time.time()

    pagados = sum(resultados)
    no_pagados = 100 - pagados

    print("Version con lock:")
    print("Pagados:", pagados)
    print("No pagados:", no_pagados)
    print("Saldo empresa final:", empresa.balance)
    print(f"Tiempo total: {end - start:.2f} s")


if __name__ == "__main__":
    main()
