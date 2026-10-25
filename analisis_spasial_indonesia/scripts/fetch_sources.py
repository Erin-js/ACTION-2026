from pathlib import Path
import concurrent.futures as cf
import urllib.request, urllib.error, json, re, hashlib, html, csv

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
RAW.mkdir(parents=True, exist_ok=True)

def fetch(item):
    sid, url = item
    out = {'id': sid, 'url': url, 'tanggal_akses': '2026-10-24'}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 research source retrieval'})
        with urllib.request.urlopen(req, timeout=45) as response:
            content = response.read(60 * 1024 * 1024)
            out.update(http_status=response.status, final_url=response.url, content_type=response.headers.get('Content-Type', ''))
        is_pdf = content[:4] == b'%PDF'
        ext = '.pdf' if is_pdf else ('.zip' if content[:2] == b'PK' else '.html')
        path = RAW / (sid + ext)
        path.write_bytes(content)
        out.update(berkas=str(path.relative_to(ROOT)).replace('\\','/'), bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
        if ext == '.html':
            text = content.decode('utf-8', errors='replace')
            links = re.findall(r'(?:href|src)=[\"\']([^\"\']+)', text)
            out['candidate_download_links'] = [html.unescape(x) for x in links if any(v in x.lower() for v in ['download', '.pdf', '.xlsx', '.zip'])][:25]
            clean = re.sub(r'<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>', '', text, flags=re.S|re.I)
            clean = html.unescape(re.sub('<[^>]+>', ' ', clean))
            clean = re.sub(r'[ \t]+', ' ', clean)
            (RAW / (sid+'.txt')).write_text(clean, encoding='utf-8')
        out['status'] = 'PDF tersimpan' if is_pdf else ('ZIP tersimpan' if ext=='.zip' else 'Halaman tersimpan; isi perlu diperiksa')
    except Exception as exc:
        out.update(status='Gagal diakses langsung', error=str(exc))
    return out

if __name__ == '__main__':
    jobs = json.loads((ROOT/'sources_to_fetch.json').read_text(encoding='utf-8'))
    results = []
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        for result in pool.map(fetch, jobs):
            results.append(result)
            print(json.dumps({k:v for k,v in result.items() if k not in ['sha256','candidate_download_links']}, ensure_ascii=True), flush=True)
    (ROOT/'data'/'access_log.json').write_text(json.dumps(results,ensure_ascii=False,indent=2), encoding='utf-8')
