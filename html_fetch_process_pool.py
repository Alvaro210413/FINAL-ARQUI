#!/usr/bin/env python3
"""
html_fetch_process_pool.py

Versión multiproceso con Pool de “HTML Fetch & Analyzer”:
- Usa multiprocessing.Pool para procesar múltiples URLs en paralelo
- Cada worker descarga y analiza su página HTML
- El proceso principal imprime resultados conforme llegan (en tiempo real)
- Al final se acumulan resultados globales y se escriben a JSON
"""

import time
import re
import json
import requests
from bs4 import BeautifulSoup
from collections import Counter
from multiprocessing import Pool, cpu_count

# --- Configuración ---
URLS_FILE     = 'urls_html.txt'
OUTPUT_FILE   = 'results_process_pool.json'
TOP_K_PER_URL = 10
TOP_K_GLOBAL  = 50
NUM_WORKERS   = min(8, cpu_count())

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
    """Ejecutado por cada worker del Pool."""
    try:
        html = fetch_html(url)
        n_links, cnt = analyze_html(html)
        return (url, n_links, cnt)
    except Exception as e:
        print(f"[POOL-PROC] Error procesando {url}: {e}", flush=True)
        return (url, 0, Counter())

def main():
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    start_time = time.time()
    global_counter = Counter()

    with Pool(processes=NUM_WORKERS) as pool:
        for url, n_links, cnt in pool.imap_unordered(process_url, urls):
            global_counter.update(cnt)
            top_words = cnt.most_common(TOP_K_PER_URL)
            print(f"[POOL-PROC] {url} → enlaces={n_links}, top-{TOP_K_PER_URL}={top_words}", flush=True)

    total_time = time.time() - start_time
    print(f"\n[POOL-PROC] Tiempo total: {total_time:.2f} s", flush=True)

    top_global = global_counter.most_common(TOP_K_GLOBAL)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        json.dump(top_global, out, ensure_ascii=False, indent=2)
    print(f"[POOL-PROC] Top-{TOP_K_GLOBAL} términos globales guardados en {OUTPUT_FILE}", flush=True)

if __name__ == '__main__':
    main()
