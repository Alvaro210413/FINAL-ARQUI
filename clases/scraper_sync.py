import time

import requests


def download_site(url: str, session: requests.Session) -> None:
    with session.get(url) as response:
        if response.status_code == 200:
            print("Respuesta del servidor exitosa (200 OK)")
            print(f"Lei {len(response.content)} bytes de {url}")
        else:
            print(f"El servidor retorno el siguiente status code: {response.status_code}")


def download_sites(sites: list[str]) -> None:
    with requests.Session() as session:
        for url in sites:
            download_site(url, session)


if __name__ == '__main__':
    sites = [
        "https://www.jython.org",
        "http://olympus.realpython.org/dice"
    ] * 160

    inicio = time.perf_counter()
    download_sites(sites)
    fin = time.perf_counter()

    t_ejecucion = fin - inicio

    print(f"Tiempo de ejecucion sincrono: {t_ejecucion:.6f} segundos")