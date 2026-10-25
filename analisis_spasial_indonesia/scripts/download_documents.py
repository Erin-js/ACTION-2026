from pathlib import Path
from html.parser import HTMLParser
import concurrent.futures as cf
import json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_sources import fetch, ROOT, RAW

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.urls=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k=='href' and v and 'download.php?' in v:
                self.urls.append(v)

jobs=[]
for sid in ['SUSENAS2025_PUB','POVERTY2025','DIGITAL2024','PODES2024_PUB','PENDIDIKAN2025','PEMUDA2025','SAK2025_PUB']:
    p=RAW/(sid+'.html')
    if p.exists():
        links=Links(); links.feed(p.read_text(encoding='utf-8'))
        if links.urls: jobs.append((sid+'_PDF',links.urls[0]))
with cf.ThreadPoolExecutor(max_workers=4) as pool:
    results=list(pool.map(fetch,jobs))
(ROOT/'data'/'download_log.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:
    print(json.dumps({k:r[k] for k in ['id','status','berkas','bytes','error'] if k in r}),flush=True)
