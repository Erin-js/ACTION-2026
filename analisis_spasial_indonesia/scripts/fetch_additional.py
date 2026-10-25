from concurrent.futures import ThreadPoolExecutor
from fetch_sources import fetch,ROOT,RAW
from html.parser import HTMLParser
import json
class Links(HTMLParser):
    def __init__(self):super().__init__();self.urls=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k=='href' and v and 'download.php?' in v:self.urls.append(v)
jobs=[
('SUSENAS2026_PUB','https://www.bps.go.id/id/publication/2026/10/05/7e415878a8af3678e51f3e0a/statistik-kesejahteraan-rakyat-2026.html'),
('KONSUMSI2025','https://www.bps.go.id/id/publication/2025/10/10/755ea866289ba29e5104e58d/pengeluaran-untuk-konsumsi-penduduk-indonesia-maret-2025.html'),
('BRIDGING_BPS','https://sig.bps.go.id/bridging-kode/index'),
('SDI_GEOMETRI','https://data.go.id/dataset/dataset/peta-batas-administrasi-provinsi-dan-kabupaten-kota'),
('BPS_KODE53','https://sirusa.bps.go.id/webadmin/doc/MFD_2010_Buku_3.pdf')
]
with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(fetch,jobs))
for sid in ['SUSENAS2026_PUB','KONSUMSI2025']:
    page=RAW/(sid+'.html')
    if page.exists():
        parser=Links();parser.feed(page.read_text(encoding='utf-8'))
        if parser.urls:results.append(fetch((sid+'_PDF',parser.urls[0])))
(ROOT/'data/additional_access_log.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:print(json.dumps({k:r[k] for k in ['id','status','berkas','bytes','error'] if k in r}),flush=True)
