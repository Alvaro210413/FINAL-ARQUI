#!/usr/bin/env python3
"""
html_fetch_thread_pool.py

Versión multihilo con ThreadPoolExecutor:
- Usa un pool de hilos para descargar y analizar páginas HTML
- Cada worker descarga con requests y analiza con BeautifulSoup
- Imprime por URL: número de enlaces y top-10 palabras
- Acumula conteo global con sincronización
- Al final mide tiempo total y guarda top-50 global en JSON
"""

import time
import re
import json
import requests
from bs4 import BeautifulSoup
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# --- Configuración ---
URLS_FILE     = 'urls_html.txt'
OUTPUT_FILE   = 'results_thread_pool.json'
TOP_K_PER_URL = 10
TOP_K_GLOBAL  = 50
MAX_WORKERS   = 10  # número de hilos en el pool

global_counter = Counter()
lock = Lock()

def fetch_html(url: str) -> str:
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

def analyze_html(html: str) -> tuple[int, Counter]:
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    n_links = len(links)
    text = soup.get_text(separator=' ')
    words = re.findall(r'\w+', text.lower())
    return n_links, Counter(words)

def process_url(url: str) -> tuple[str, int, Counter]:
    try:
        html = fetch_html(url)
        n_links, cnt = analyze_html(html)
        return url, n_links, cnt
    except Exception as e:
        print(f"[POOL-THREAD] Error procesando {url}: {e}")
        return url, 0, Counter()

def main():
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_url, url) for url in urls]

        for future in as_completed(futures):
            url, n_links, cnt = future.result()
            with lock:
                global_counter.update(cnt)
            top_words = cnt.most_common(TOP_K_PER_URL)
            print(f"[POOL-THREAD] {url} → enlaces={n_links}, top-{TOP_K_PER_URL}={top_words}")

    total_time = time.time() - start_time
    print(f"\n[POOL-THREAD] Tiempo total: {total_time:.2f} s")

    top_global = global_counter.most_common(TOP_K_GLOBAL)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        json.dump(top_global, out, ensure_ascii=False, indent=2)
    print(f"[POOL-THREAD] Top-{TOP_K_GLOBAL} términos globales guardados en {OUTPUT_FILE}")

import matplotlib.pyplot as plt

workers = [2, 4, 8, 16]
tiempos = [45.3, 32.3, 26.8, 25.4]       # reemplazar con tus valores
memoria = [95, 97, 101, 121]            # reemplazar con tus valores

plt.figure(figsize=(8,4))

# --- Grafico de tiempo ---
plt.subplot(1, 2, 1)
plt.plot(workers, tiempos, marker='o')
plt.title('Escalabilidad de Pool (Tiempo)')
plt.xlabel('Workers')
plt.ylabel('Tiempo (s)')

# --- Grafico de memoria ---
plt.subplot(1, 2, 2)
plt.plot(workers, memoria, marker='o', color='orange')
plt.title('Escalabilidad de Pool (Memoria)')
plt.xlabel('Workers')
plt.ylabel('Memoria (MiB)')

plt.tight_layout()
plt.savefig('escalabilidad_pool.png')
plt.show()


if __name__ == '__main__':
    main()

