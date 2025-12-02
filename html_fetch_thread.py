#!/usr/bin/env python3
"""
html_fetch_thread.py

Versión multihilo (manual) de “HTML Fetch & Analyzer”:
- Lee URLs de urls_html.txt
- Crea un hilo por URL que:
    * Descarga el HTML con requests
    * Parsea HTML con BeautifulSoup
    * Cuenta enlaces y palabras
- Imprime por URL: número de enlaces y top-10 palabras
- Sincroniza acceso al contador global de palabras
- Mide tiempo total y guarda top-50 global a JSON
"""

import time
import re
import json
import requests
import threading
from collections import Counter
from bs4 import BeautifulSoup

# --- Configuración ---
URLS_FILE     = 'urls_html.txt'
OUTPUT_FILE   = 'results_thread.json'
TOP_K_PER_URL = 10
TOP_K_GLOBAL  = 50

# Contador global compartido
global_counter = Counter()
lock = threading.Lock()

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

def process_url(url: str):
    try:
        html = fetch_html(url)
        n_links, cnt = analyze_html(html)

        with lock:
            global_counter.update(cnt)

        top_words = cnt.most_common(TOP_K_PER_URL)
        print(f"[THREAD] {url} → enlaces={n_links}, top-{TOP_K_PER_URL}={top_words}")
    except Exception as e:
        print(f"[THREAD] Error procesando {url}: {e}")

def main():
    # Leer lista de URLs
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    threads = []
    start_time = time.time()

    # Crear y lanzar hilos
    for url in urls:
        t = threading.Thread(target=process_url, args=(url,))
        threads.append(t)
        t.start()

    # Esperar a que todos terminen
    for t in threads:
        t.join()

    total_time = time.time() - start_time
    print(f"\n[THREAD] Tiempo total: {total_time:.2f} s")

    # Guardar resultados globales
    top_global = global_counter.most_common(TOP_K_GLOBAL)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        json.dump(top_global, out, ensure_ascii=False, indent=2)
    print(f"[THREAD] Top-{TOP_K_GLOBAL} términos globales guardados en {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
