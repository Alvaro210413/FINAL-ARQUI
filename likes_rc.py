# likes_rc.py
import threading
import time

N_THREADS = 300          # Usuarios (hilos)
LIKES_POR_USUARIO = 1500 # Likes que hará cada hilo
RETARDO = 0.000001       # Forzar race conditions

class Publicacion:
    def __init__(self):
        self.likes = 0

    # Incremento SIN LOCK → vulnerable a condiciones de carrera
    def dar_like(self):
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
