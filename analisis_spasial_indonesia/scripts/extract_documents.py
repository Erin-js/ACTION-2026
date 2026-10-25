from pathlib import Path
import json, concurrent.futures as cf
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'
TEXT=ROOT/'data/extracted'
TEXT.mkdir(parents=True,exist_ok=True)

def extract(path):
    out=TEXT/(path.stem+'.txt')
    if out.exists():
        return {'berkas':str(path.relative_to(ROOT)),'status':'Ekstraksi tersedia; dipertahankan','text':str(out.relative_to(ROOT))}
    reader=PdfReader(path)
    pages=[]
    for i,page in enumerate(reader.pages,1):
        pages.append(f'\n\n===== PDF PAGE {i} =====\n'+(page.extract_text() or ''))
    out.write_text(''.join(pages),encoding='utf-8')
    return {'berkas':str(path.relative_to(ROOT)),'pages':len(pages),'text':str(out.relative_to(ROOT))}

with cf.ThreadPoolExecutor(max_workers=3) as pool:
    results=list(pool.map(extract,RAW.glob('*.pdf')))
(ROOT/'data/pdf_inventory.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
