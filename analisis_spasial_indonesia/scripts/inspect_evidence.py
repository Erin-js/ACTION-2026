from pathlib import Path
import pypdfium2 as pdfium
import re, json

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'; TEXT=ROOT/'data/extracted'; QA=ROOT/'data/qa'
QA.mkdir(parents=True,exist_ok=True)
targets=['SAK2025_KUESIONER','SAK2025_NON_DISEMINASI','WB_CARE_REPORT_ID','WB_CARE_PRESENTATION','ILO_CARE','BPS_IPTK_Feb2026']
for stem in targets:
    p=RAW/(stem+'.pdf')
    if not p.exists():continue
    doc=pdfium.PdfDocument(str(p)); pages=[]
    for i in range(len(doc)):
        page=doc[i]; tp=page.get_textpage(); text=tp.get_text_range()
        pages.append(f'\n\n===== PDF PAGE {i+1} =====\n'+text)
        tp.close();page.close()
    (TEXT/(stem+'.txt')).write_text(''.join(pages),encoding='utf-8')
    print(stem,len(pages),flush=True)
    doc.close()

for stem,printed in [('DIGITAL2024_PDF','82'),('POVERTY2025_PDF','11')]:
    content=(TEXT/(stem+'.txt')).read_text(encoding='utf-8')
    pages=re.split(r'===== PDF PAGE (\d+) =====',content)
    target=None
    for j in range(1,len(pages),2):
        t=pages[j+1]
        if (stem=='DIGITAL2024_PDF' and 'Lampiran' in t and 'Perempuan' in t and '2021' in t and len(re.findall(r'\d+,\d+',t))>80 and '\n82\n' in t) or (stem=='POVERTY2025_PDF' and '1 Simeulue 15,58' in t):
            target=int(pages[j]);break
    if target:
        doc=pdfium.PdfDocument(str(RAW/(stem+'.pdf')));page=doc[target-1]
        page.render(scale=1.5).to_pil().save(QA/(stem+f'_p{target}.png'))
        page.close();doc.close();print('QA',stem,target,flush=True)
