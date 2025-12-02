#!/usr/bin/env python3
"""
html_fetch_process.py

Versión multiproceso (sin pool) con impresión directa por cada proceso:
- Cada proceso descarga y analiza una página HTML
- Imprime su resultado directamente en consola (en tiempo real)
- El proceso principal solo mide tiempo y espera a que todos terminen
"""

import time
import re
import json
import requests
from bs4 import BeautifulSoup
from collections import Counter
from multiprocessing import Process, Manager

# --- Configuración ---
URLS_FILE     = 'urls_html.txt'
OUTPUT_FILE   = 'results_process.json'
TOP_K_PER_URL = 10
TOP_K_GLOBAL  = 50

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

def process_url(url: str, result_list):
    try:
        html = fetch_html(url)
        n_links, cnt = analyze_html(html)
        top_words = cnt.most_common(TOP_K_PER_URL)
        print(f"[PROCESS] {url} → enlaces={n_links}, top-{TOP_K_PER_URL}={top_words}", flush=True)
        result_list.append(cnt)
    except Exception as e:
        print(f"[PROCESS] Error en {url}: {e}", flush=True)
        result_list.append(Counter())  # empty result

def main():
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    manager = Manager()
    result_list = manager.list()

    processes = []
    start_time = time.time()

    for url in urls:
        p = Process(target=process_url, args=(url, result_list))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # Combinar resultados
    global_counter = Counter()
    for partial_counter in result_list:
        global_counter.update(partial_counter)

    total_time = time.time() - start_time
    print(f"\n[PROCESS] Tiempo total: {total_time:.2f} s", flush=True)

    top_global = global_counter.most_common(TOP_K_GLOBAL)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        json.dump(top_global, out, ensure_ascii=False, indent=2)
    print(f"[PROCESS] Top-{TOP_K_GLOBAL} términos globales guardados en {OUTPUT_FILE}", flush=True)

if __name__ == '__main__':
    main()
