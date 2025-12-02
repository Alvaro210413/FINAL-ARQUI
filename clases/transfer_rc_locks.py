import time
from threading import Thread, Lock

NUM_THREADS = 10
OPERATIONS_PER_THREAD = 1000


class BankAccount:
    def __init__(self, balance):
        self.balance = balance
        self.total_deposits = 0
        self.total_withdrawals = 0
        self.lock = Lock()

    def deposit(self, amount):
        with self.lock:
            temp = self.balance
            time.sleep(0.000001)
            self.balance = temp + amount
            self.total_deposits += 1

    def withdraw(self, amount):
        with self.lock:
            temp = self.balance
            time.sleep(0.000001)
            if temp >= amount:
                self.balance = temp - amount
                self.total_withdrawals += 1


def realizar_transacciones(cuenta: BankAccount, thread_id: int):
    print(f"[Thread {thread_id}] Iniciando transacciones")
    for i in range(OPERATIONS_PER_THREAD):
        if i % 2 == 0:
            cuenta.deposit(10)
        else:
            cuenta.withdraw(5)
    
    print(f"[Thread {thread_id}] Transacciones completadas")


if __name__ == '__main__':
    account = BankAccount(1000)

    print(f"Balance inicial: {account.balance}")
    print(f"Operaciones por hilo: {OPERATIONS_PER_THREAD}")
    print(f"Total de hilos: {NUM_THREADS}")

    inicio = time.perf_counter()

    threads = list()
    for i in range(NUM_THREADS):
        t = Thread(target=realizar_transacciones, args=(account, i))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    fin = time.perf_counter()

    t_ejecucion = fin - inicio

    depositos_esperados = NUM_THREADS * (OPERATIONS_PER_THREAD // 2) * 10
    retiros_esperados = NUM_THREADS * (OPERATIONS_PER_THREAD // 2) * 5
    balance_esperado = 1000 + depositos_esperados - retiros_esperados

    print(f"balance final: {account.balance}")
    print(f"balance esperado: {balance_esperado}")
    print(f"Depositos registrados: {account.total_deposits} - esperados: {NUM_THREADS * (OPERATIONS_PER_THREAD // 2)}")
    print(f"Retiros registrados: {account.total_withdrawals} - esperados: {NUM_THREADS * (OPERATIONS_PER_THREAD // 2)}")
    print(f"Diferencia: ${account.balance - balance_esperado}")
    print(f"Tiempo de ejecucion: {(fin - inicio):.6f} segundos")
