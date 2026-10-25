from pathlib import Path
import concurrent.futures as cf
import json
from fetch_sources import fetch, ROOT

jobs=[
('META_DES','https://sirusa.bps.go.id/metadata/variabel/658ca45a-3492-c2ba-967b-23da16b2c629'),
('META_DWY','https://sirusa.bps.go.id/sirusa/variabel/65bc8347-e65e-4c7d-c453-d574a0c8ac88'),
('META_AVN','https://sirusa.bps.go.id/metadata/variabel/090e3f86-e7be-623b-a27b-d2bbd66e74e9'),
('WB_CARE_PRESENTATION','https://thedocs.worldbank.org/en/doc/9ba3f2a164cacef01a472fd443cdedcf-0070012024/original/Report-Presentation-The-Care-Economy-in-Indonesia-Final-20240902.pdf'),
('WB_CARE_REPORT_ID','https://openknowledge.worldbank.org/bitstreams/def01f54-3416-4d85-b57a-4746be7a988d/download'),
('ILO_CARE','https://www.ilo.org/sites/default/files/2024-10/GEDI-STAT%20brief_formatted_28.10.24_final.pdf'),
('ILO_JOBSGAP','https://ilostat.ilo.org/blog/women-are-more-likely-than-men-to-want-a-job-but-not-have-one/'),
('SAK2025_DOCUMENTATION','https://drive.bps.go.id/s/WE3A734gea2sa3d/download'),
('BIG_SERVICE','https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH/BATAS_WILAYAH/MapServer?f=pjson'),
('SIG_BPS','https://sig.bps.go.id'),
('IFLS','https://www.rand.org/health/surveys/FLS/IFLS.html'),
('PAUD_REFERENSI','https://referensi.data.kemendikdasmen.go.id/pendidikan/paud'),
('BPS_TPAK_TABLE','https://www.bps.go.id/id/statistics-table/2/MjIwMCMy/tingkat-partisipasi-angkatan-kerja')
]
with cf.ThreadPoolExecutor(max_workers=6) as pool:
    results=[]
    for r in pool.map(fetch,jobs):
        results.append(r)
        print(json.dumps({k:r[k] for k in ['id','status','berkas','bytes','error'] if k in r}),flush=True)
(ROOT/'data/evidence_access_log.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
