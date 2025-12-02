# likes_rc_locks.py
import threading
import time

N_THREADS = 300
LIKES_POR_USUARIO = 1500
RETARDO = 0.000001       # Igual que antes

class Publicacion:
    def __init__(self):
        self.likes = 0
        self.lock = threading.Lock()

    # Incremento CON lock → operación segura
    def dar_like(self):
        with self.lock:
            actual = self.likes
            time.sleep(RETARDO)
            self.likes = actual + 1

def worker(pub):
    for _ in range(LIKES_POR_USUARIO):
        pub.dar_like()

def main():
    pub = Publicacion()
    hilos = []

    inicio = time.time()

    for _ in range(N_THREADS):
        t = threading.Thread(target=worker, args=(pub,))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    fin = time.time()

    likes_esperados = N_THREADS * LIKES_POR_USUARIO
    print("Likes contados:", pub.likes)
    print("Likes esperados:", likes_esperados)
    print("Diferencia:", likes_esperados - pub.likes)
    print("Tiempo total:", round(fin - inicio, 2), "s")

if __name__ == "__main__":
    main()
