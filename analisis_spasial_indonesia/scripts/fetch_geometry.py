import json,re
from fetch_sources import ROOT,fetch
page=(ROOT/'data/raw/SDI_GEOMETRI.html').read_text(encoding='utf-8')
urls=re.findall(r'https://map\.kemendagri\.go\.id/geoserver/ows\?[^"<> ]+',page)
urls=[x.replace('\\u0026','&').rstrip('\\') for x in urls if 'outputFormat=SHAPE-ZIP' in x]
results=[]
if urls:
    r=fetch(('KEMENDAGRI_WFS_ZIP',urls[0]));results.append(r)
    print(json.dumps({k:r[k] for k in ['id','status','berkas','bytes','error'] if k in r}))
(ROOT/'data/geospatial_access_log.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
