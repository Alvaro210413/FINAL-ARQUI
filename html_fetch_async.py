#!/usr/bin/env python3
import asyncio
import time
import re
import json
import aiohttp
from bs4 import BeautifulSoup
from collections import Counter

URLS_FILE    = 'urls_html.txt'
OUTPUT_FILE  = 'html_results_async.json'
TOP_WORDS    = 10
GLOBAL_TOP   = 50
CONCURRENCY  = 10  # usar 5 si tu red es lenta

def analyze_html(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    links = [a.get('href') for a in soup.find_all('a') if a.get('href')]
    n_links = len(links)
    text = soup.get_text()
    words = re.findall(r'\w+', text.lower())
    cnt = Counter(words)
    return n_links, cnt

async def fetch_html(session, url):
    async with session.get(url) as resp:
        resp.raise_for_status()
        return await resp.text()

async def download_one(url, session, sem, html_results):
    async with sem:
        html = await fetch_html(session, url)
        html_results.append(html)

async def main():
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    sem = asyncio.Semaphore(CONCURRENCY)
    html_results = []

    # ------------ DESCARGA ------------
    start_download = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        tasks = [download_one(url, session, sem, html_results) for url in urls]
        await asyncio.gather(*tasks)

    end_download = time.perf_counter()

    # ------------ PARSING -------------
    start_parse = time.perf_counter()
    global_counter = Counter()

    for html in html_results:
        _, cnt = analyze_html(html)
        global_counter.update(cnt)

    end_parse = time.perf_counter()

    # ------------ RESULTADOS -----------
    download_total = end_download - start_download
    parse_total = end_parse - start_parse
    total = download_total + parse_total

    print("\n===== RESULTADOS ASYNC =====")
    print(f"Tiempo total de descargas (async): {download_total:.4f} s")
    print(f"Tiempo total de parsing   (async): {parse_total:.4f} s")
    print(f"Tiempo total del programa (async): {total:.4f} s")

    top_global = global_counter.most_common(GLOBAL_TOP)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(top_global, out, ensure_ascii=False, indent=2)

    # ---- PROMEDIO POR URL ----
    num_urls = len(urls)
    promedio_por_url = download_total / num_urls
    prom_analisis = parse_total / num_urls
    print(f"Promedio de descarga por URL (async): {promedio_por_url:.4f} s")
    print(f"Promedio de análisis  por URL (async): {prom_analisis:.6f} s")
    
if __name__ == "__main__":
    asyncio.run(main())

