#!/usr/bin/env python3
"""
html_fetch_sync.py

Versión síncrona de “HTML Fetch & Analyzer”:
- Lee URLs de urls_html.txt
- Descarga cada página con requests de forma bloqueante
- Parsea HTML con BeautifulSoup:
    * Cuenta enlaces (<a href="…">)
    * Extrae texto, tokeniza y cuenta palabras
- Imprime por URL: número de enlaces y top-10 palabras
- Al final imprime tiempo total y vuelca top-50 global a JSON
"""

import time
import re
import json
import requests
from collections import Counter
from bs4 import BeautifulSoup

# --- Configuración ---
URLS_FILE     = 'urls_html.txt'
OUTPUT_FILE   = 'results_sync.json'
TOP_K_PER_URL = 10      # Top-10 palabras por página
TOP_K_GLOBAL  = 50      # Top-50 palabras global

def fetch_html(url: str) -> str:
    """Descarga el HTML de una URL y devuelve el texto."""
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

def analyze_html(html: str) -> tuple[int, Counter]:
    """
    Parsea HTML y devuelve:
      - número de enlaces <a href="…">
      - Counter de palabras en el texto de la página
    """
    soup = BeautifulSoup(html, 'html.parser')
    # Contar enlaces
    links = soup.find_all('a', href=True)
    n_links = len(links)
    # Extraer y tokenizar texto
    text = soup.get_text(separator=' ')
    words = re.findall(r'\w+', text.lower())
    counter = Counter(words)
    return n_links, counter

def main():
    # Leer lista de URLs
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    global_counter = Counter()
    start_time = time.time()

    download_times = []
    analisis_times = []

    # Procesamiento secuencial
    for url in urls:

        t0 = time.perf_counter()
        html = fetch_html(url)
        t1 = time.perf_counter()
        download_time = t1 - t0
        download_times.append(download_time)

        t2 = time.perf_counter()
        n_links, cnt = analyze_html(html)
        t3 = time.perf_counter()
        analisis_time = t3 - t2
        analisis_times.append(analisis_time)

        global_counter.update(cnt)

        top_words = cnt.most_common(TOP_K_PER_URL)
        print(f"[SYNC] {url} → enlaces={n_links}, top-{TOP_K_PER_URL}={top_words}")

    total_time = time.time() - start_time
    print(f"\n[SYNC] Tiempo total: {total_time:.6f} s")
    descargas_prom  = sum(download_times)/len(download_times)
    analisis_prom = sum(analisis_times)/len(analisis_times)
    print(f"Promedio de descarga: {descargas_prom:.6f} s")
    print(f"Promedio de parsing: {analisis_prom:.6f} s")

    # Guardar resultados globales
    top_global = global_counter.most_common(TOP_K_GLOBAL)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        json.dump(top_global, out, ensure_ascii=False, indent=2)
    print(f"[SYNC] Top-{TOP_K_GLOBAL} términos globales guardados en {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
