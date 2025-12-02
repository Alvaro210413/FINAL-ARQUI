import time
from multiprocessing import cpu_count
import threading

import concurrent.futures
import requests

thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    
    return thread_local.session


def download_site(url: str) -> None:
    session = get_session()
    with session.get(url) as response:
        if response.status_code == 200:
            print("Respuesta del servidor exitosa (200 OK)")
            print(f"Lei {len(response.content)} bytes de {url}")
        else:
            print(f"El servidor retorno el siguiente status code: {response.status_code}")


def download_sites(sites: list[str]) -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        executor.map(download_site, sites)


if __name__ == '__main__':
    sites = [
        "https://www.jython.org",
        "http://olympus.realpython.org/dice"
    ] * 160

    inicio = time.perf_counter()
    download_sites(sites)
    fin = time.perf_counter()

    t_ejecucion = fin - inicio

    print(f"Tiempo de ejecucion multihilo: {t_ejecucion:.6f} segundos")
