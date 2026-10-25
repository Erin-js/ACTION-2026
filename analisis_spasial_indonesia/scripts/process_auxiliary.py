from pathlib import Path
import re,json,csv
from html.parser import HTMLParser
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; TEXT=ROOT/'data/extracted'; OUT=ROOT/'data/processed'

def pages(stem):
    raw=(TEXT/(stem+'.txt')).read_text(encoding='utf-8').replace('\r','')
    parts=re.split(r'===== PDF PAGE (\d+) =====',raw)
    return {int(parts[i]):parts[i+1] for i in range(1,len(parts),2)}

def number(s):return float(s.replace('.','').replace(',','.'))

digital=[]
pg=pages('DIGITAL2024_PDF')
for page_n,sex in [(111,'Laki-laki'),(112,'Perempuan')]:
    text=pg[page_n]
    if sex=='Perempuan': assert 'Perempuan' in text and '2021' in text
    else: assert 'Laki-laki' in text and '2021' in text
    for line in text.splitlines():
        m=re.match(r'^\s*(\d{2})\.\s+(.+?)\s+((?:[\d.,]+|[–—-]|\.\.\.)\s+(?:[\d.,]+|[–—-]|\.\.\.)\s+(?:[\d.,]+|[–—-]|\.\.\.)\s+[\d.,]+)\s*$',line)
        if not m:continue
        code,name,vals=m.groups()
        for year,value in zip([2021,2022,2023,2024],vals.split()):
            digital.append({'kode_prov_bps':code,'provinsi_sumber':name,'jenis_kelamin':sex,'tahun':year,'internet_persen':number(value) if re.fullmatch(r'\d+,\d+',value) else None,'penyebut':'Jumlah penduduk dengan jenis kelamin tersebut sesuai catatan tabel; bukan khusus 15+','source_id':'DIGITAL2024','halaman_pdf':page_n,'halaman_cetak':page_n-30,'status_pemekaran':'Jangan menyambung seri Papua lintas pemekaran tanpa harmonisasi batas'})
dig=pd.DataFrame(digital)
dig['provinsi_baku']=dig.apply(lambda r:'Nusa Tenggara Timur' if r.kode_prov_bps=='53' else r.provinsi_sumber,axis=1)
dig['catatan_audit']=dig.apply(lambda r:'Sumber mencetak nama Nusa Tenggara Barat pada kode 53; nama baku Nusa Tenggara Timur berdasarkan kode BPS. Nama asli dipertahankan.' if r.kode_prov_bps=='53' else '',axis=1)
assert len(dig[dig.tahun==2024])==76, len(dig)
dig.to_csv(OUT/'internet_gender_provinsi_2021_2024.csv',index=False,encoding='utf-8-sig')

pg=pages('POVERTY2025_PDF'); rows=[]; aggregate=[]; unparsed=[]; table_started=False
pattern=r'([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.]+)'
for page_n,text in pg.items():
    if page_n<25:continue
    if 'Tabel 3.1' in text:break
    if page_n==25:table_started=True
    if not table_started:continue
    text=re.sub(r'(?m)^(\d{1,2})\s*\n(?=[A-Za-z])',r'\1 ',text)
    text=re.sub(r'(?m)^(\d{1,2}\s+[A-Za-z][^\n\d]*?)-\s*\n(?=[A-Za-z])',r'\1',text)
    text=re.sub(r'(?m)^(\d{1,2}\s+[A-Za-z][^\n\d]*?)\s*\n(?=[A-Za-z])',r'\1 ',text)
    for line in text.splitlines():
        m=re.match(r'^\s*(\d{1,2})\s+(.+?)\s+'+pattern+r'\s*$',line)
        if m:
            no,name,poor,p0,p1,p2,gk=m.groups()
            rows.append({'nomor_dalam_provinsi':int(no),'kabupaten_kota_sumber':name,'tahun':2025,'penduduk_miskin_ribu':number(poor),'p0_persen':number(p0),'p1':number(p1),'p2':number(p2),'garis_kemiskinan_rp_kap_bulan':int(gk.replace('.','')),'source_id':'POVERTY2025','halaman_pdf':page_n,'halaman_cetak':page_n-14,'kode_bps':'','status_join':'Nama sesuai sumber; kode BPS dan relasi geometri belum dipadankan'})
        else:
            if re.match(r'^\s*\d{1,2}\s+[A-Za-z]',line):unparsed.append({'page':page_n,'line':line})
            a=re.match(r'^\s*([A-Za-z][A-Za-z .]+?)\s+'+pattern+r'\s*$',line)
            if a:
                name,poor,p0,p1,p2,gk=a.groups()
                aggregate.append({'provinsi_sumber':name,'tahun':2025,'penduduk_miskin_ribu':number(poor),'p0_persen':number(p0),'p1':number(p1),'p2':number(p2),'garis_kemiskinan_rp_kap_bulan':int(gk.replace('.','')),'halaman_pdf':page_n,'source_id':'POVERTY2025','jumlah_kab_sampai_baris_ini':len(rows)})

# Tabel menempatkan agregat provinsi setelah baris kabupaten/kotanya.
start=0
for a in aggregate:
    if a['provinsi_sumber'].lower()=='indonesia':continue
    end=a['jumlah_kab_sampai_baris_ini']
    for row in rows[start:end]: row['provinsi_sumber']=a['provinsi_sumber']
    start=end
poverty=pd.DataFrame(rows)
(OUT/'poverty_extraction_unparsed.json').write_text(json.dumps(unparsed,ensure_ascii=False,indent=2),encoding='utf-8')
if len(poverty)!=514:print(json.dumps({'rows':len(poverty),'aggregates':aggregate,'unparsed':unparsed},ensure_ascii=True),flush=True)
assert len(poverty)==514, f'Perlu audit ekstraksi kemiskinan: {len(poverty)} baris'
assert poverty.provinsi_sumber.notna().all()
assert not poverty.duplicated(['provinsi_sumber','kabupaten_kota_sumber','tahun']).any()
assert poverty.p0_persen.between(0,100).all()
poverty.to_csv(OUT/'kemiskinan_514_kabupaten_kota_2025.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(aggregate).to_csv(OUT/'kemiskinan_agregat_provinsi_2025.csv',index=False,encoding='utf-8-sig')

class TableParser(HTMLParser):
    def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='tr':self.row=[]
        if tag in ['td','th'] and self.row is not None:self.cell=[]
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ['td','th'] and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
        if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
parser=TableParser();parser.feed((ROOT/'data/raw/SAK2025_METADATA.html').read_text(encoding='utf-8'))
meta=[{'nomor':r[0],'variabel':r[1],'label_resmi':r[2],'tipe':r[3],'partisi':r[4],'source_id':'SAK2025_METADATA'} for r in parser.rows if len(r)>=5 and r[0].isdigit()]
pd.DataFrame(meta).to_csv(OUT/'kamus_variabel_sakernas_agustus2025.csv',index=False,encoding='utf-8-sig')

sus=pages('SUSENAS2025_PUB_PDF')
internet2025=[];marriage=[]
for line in sus[240].splitlines():
    m=re.match(r'^([A-Za-z][A-Za-z .]+?)\s+((?:\d+,\d+|[–—-])(?:\s+(?:\d+,\d+|[–—-])){8})\s*$',line)
    if not m:continue
    name,vals=m.groups();vals=vals.split()
    for start,area in [(0,'Perkotaan'),(3,'Perdesaan'),(6,'Perkotaan+Perdesaan')]:
        internet2025.append({'provinsi_sumber':name,'klasifikasi_daerah':area,'tahun':2025,'internet_laki_persen':number(vals[start]) if ',' in vals[start] else None,'internet_perempuan_persen':number(vals[start+1]) if ',' in vals[start+1] else None,'internet_total_persen':number(vals[start+2]) if ',' in vals[start+2] else None,'penyebut':'Penduduk umur 5 tahun ke atas dengan jenis kelamin dan klasifikasi daerah terkait','periode':'Maret 2025; penggunaan internet dalam 3 bulan terakhir','source_id':'SUSENAS2025_PUB','tabel':'7.4','halaman_pdf':240,'halaman_cetak':196})
for line in sus[68].splitlines():
    m=re.match(r'^([A-Za-z][A-Za-z .]+?)\s+((?:\d+,\d+)(?:\s+\d+,\d+){9})\s*$',line)
    if not m:continue
    name,vals=m.groups();vals=[number(x) for x in vals.split()]
    for start,sex in [(0,'Laki-laki'),(5,'Perempuan')]:
        marriage.append({'provinsi_sumber':name,'jenis_kelamin':sex,'tahun':2025,'belum_kawin_persen':vals[start],'kawin_persen':vals[start+1],'cerai_hidup_persen':vals[start+2],'cerai_mati_persen':vals[start+3],'penyebut':'Penduduk umur 15-49 tahun dengan jenis kelamin terkait','periode':'Susenas Maret 2025','source_id':'SUSENAS2025_PUB','tabel':'2.7','halaman_pdf':68,'halaman_cetak':24})
internet2025=pd.DataFrame(internet2025);marriage=pd.DataFrame(marriage)
assert len(internet2025)==117,len(internet2025)
assert len(marriage)==78,len(marriage)
assert (marriage[['belum_kawin_persen','kawin_persen','cerai_hidup_persen','cerai_mati_persen']].sum(axis=1)-100).abs().max()<0.03
internet2025.to_csv(OUT/'internet_gender_desa_kota_provinsi_maret2025.csv',index=False,encoding='utf-8-sig')
marriage.to_csv(OUT/'status_perkawinan_gender_15_49_provinsi_maret2025.csv',index=False,encoding='utf-8-sig')

def canonical(name):
    return {'Kep. Bangka Belitung':'Kepulauan Bangka Belitung','Bangka Belitung':'Kepulauan Bangka Belitung','Kep. Riau':'Kepulauan Riau'}.get(name,name)
baseline=pd.read_csv(OUT/'panel_gender_38_provinsi_3_periode.csv')
context=baseline[(baseline.periode=='2025-08')&(baseline.wilayah=='Provinsi')][['provinsi','tpak_perempuan','epr_perempuan','tpt_perempuan','gap_tpak_pp']].copy()
context['provinsi']=context.provinsi.map(canonical)
for subset,cols in [(internet2025[internet2025.klasifikasi_daerah=='Perkotaan+Perdesaan'],['internet_perempuan_persen','internet_laki_persen']), (marriage[marriage.jenis_kelamin=='Perempuan'],['kawin_persen','belum_kawin_persen']), (pd.DataFrame(aggregate),['p0_persen','p1','p2'])]:
    right=subset[['provinsi_sumber']+cols].copy();right['provinsi']=right.provinsi_sumber.map(canonical)
    context=context.merge(right.drop(columns='provinsi_sumber'),on='provinsi',how='left',validate='one_to_one')
codes=dig[(dig.tahun==2024)&(dig.jenis_kelamin=='Perempuan')][['kode_prov_bps','provinsi_baku']].copy();codes['provinsi']=codes.provinsi_baku.map(canonical)
context=context.merge(codes.drop(columns='provinsi_baku'),on='provinsi',how='left',validate='one_to_one')
assert len(context)==38
assert context.drop(columns='provinsi').notna().all().all(),context[context.isna().any(axis=1)].to_dict('records')
context['periode_kerja']='Agustus 2025'
context['periode_internet_perkawinan_kemiskinan']='Maret 2025'
context['catatan']='Konteks wilayah; umur penyebut TPAK 15+, internet 5+, perkawinan 15-49. Bukan hubungan individual atau sebab-akibat.'
context.to_csv(OUT/'panel_konteks_38_provinsi_2025.csv',index=False,encoding='utf-8-sig')
summary={'internet_rows':len(dig),'internet_2024_prov_gender':len(dig[dig.tahun==2024]),'internet_gender_desa_kota_2025_rows':len(internet2025),'perkawinan_gender_1549_2025_rows':len(marriage),'panel_konteks_rows':len(context),'poverty_kab_kota':len(poverty),'poverty_provinsi':poverty.provinsi_sumber.nunique(),'sakernas_metadata_variables':len(meta),'peringatan':'Kemiskinan tidak menurut gender. Data berbeda periode/umur penyebut. Kode kabupaten dan geometri belum dipadankan.'}
(OUT/'auxiliary_validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
