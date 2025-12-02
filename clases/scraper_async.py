import asyncio
import time

import aiohttp


async def download_site(url: str, session: aiohttp.ClientSession) -> None:
    try:
        async with session.get(url) as response:
            content = await response.read()
            print(f"Lei {len(content)} bytes de {url}")
    except Exception as e:
        print(f"Error al descargar {url}: {e}")


async def download_sites(sites: list[str]) -> None:
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        await asyncio.gather(*(download_site(url, session) for url in sites))


if __name__ == '__main__':
    sites = [
        "https://www.jython.org",
        "http://olympus.realpython.org/dice"
    ] * 160

    inicio = time.perf_counter()
    asyncio.run(download_sites(sites))
    fin = time.perf_counter()

    t_ejecucion = fin - inicio

    print(f"Tiempo de ejecucion asincrona: {t_ejecucion:.6f} segundos")
