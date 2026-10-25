from pathlib import Path
import csv,json,re,ast,hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed'
checks=[]
def check(name,ok,detail=''):
    checks.append({'pemeriksaan':name,'lulus':bool(ok),'rincian':detail})
    assert ok,(name,detail)
expected={
'panel_gender_38_provinsi_3_periode.csv':117,
'screening_perubahan_provinsi_feb2025_feb2026.csv':39,
'panel_konteks_38_provinsi_2025.csv':38,
'kemiskinan_514_kabupaten_kota_2025.csv':514,
'kemiskinan_agregat_provinsi_2025.csv':38,
'internet_gender_desa_kota_provinsi_maret2025.csv':117,
'status_perkawinan_gender_15_49_provinsi_maret2025.csv':78,
'internet_gender_provinsi_2021_2024.csv':304,
'kamus_variabel_sakernas_agustus2025.csv':290,
}
for name,n in expected.items():
    df=pd.read_csv(OUT/name)
    check('Jumlah baris '+name,len(df)==n,str(len(df)))
context=pd.read_csv(OUT/'panel_konteks_38_provinsi_2025.csv',dtype={'kode_prov_bps':str})
check('Kunci provinsi unik',not context.kode_prov_bps.duplicated().any())
check('Nilai inti panel konteks tersedia',context.drop(columns=['catatan']).notna().all().all())
poor=pd.read_csv(OUT/'kemiskinan_514_kabupaten_kota_2025.csv')
prov=pd.read_csv(OUT/'kemiskinan_agregat_provinsi_2025.csv')
tot=poor.groupby('provinsi_sumber').penduduk_miskin_ribu.sum()
comparison=prov[['provinsi_sumber','penduduk_miskin_ribu']].copy()
comparison['jumlah_dari_kabupaten']=comparison.provinsi_sumber.map(tot)
comparison['selisih_ribu']=comparison.jumlah_dari_kabupaten-comparison.penduduk_miskin_ribu
comparison['toleransi_pembulatan_ribu']=comparison.provinsi_sumber.map(poor.groupby('provinsi_sumber').size())*0.005+0.005+1e-9
check('Rekonsiliasi jumlah miskin kabupaten-provinsi',comparison.selisih_ribu.abs().le(comparison.toleransi_pembulatan_ribu).all(),str(comparison.selisih_ribu.abs().max()))
comparison.to_csv(OUT/'audit_rekonsiliasi_kemiskinan.csv',index=False,encoding='utf-8-sig')
check('Kode kabupaten belum diisi secara spekulatif',poor.kode_bps.isna().all())
internet=pd.read_csv(OUT/'internet_gender_desa_kota_provinsi_maret2025.csv')
dki=internet[(internet.provinsi_sumber=='DKI Jakarta')&(internet.klasifikasi_daerah=='Perdesaan')]
check('DKI perdesaan tetap tidak tersedia',dki.internet_perempuan_persen.isna().all() and len(dki)==1)
digital=pd.read_csv(OUT/'internet_gender_provinsi_2021_2024.csv',dtype={'kode_prov_bps':str})
check('Kode 53 diperbaiki dengan jejak nama asli',digital[digital.kode_prov_bps=='53'].provinsi_baku.eq('Nusa Tenggara Timur').all() and digital[digital.kode_prov_bps=='53'].catatan_audit.notna().all())
catalogue=pd.read_csv(ROOT/'katalog_sumber.csv').fillna('')
check('ID katalog unik',not catalogue.id.duplicated().any())
check('URL sumber eksplisit',catalogue.url.str.startswith('https://').all())
for _,row in catalogue.iterrows():
    for file in row.berkas_lokal.split('; '):
        if file:check('Berkas sumber '+row.id,(ROOT/file).exists(),file)
for file in ROOT.rglob('*.md'):
    text=file.read_text(encoding='utf-8')
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if target.startswith(('https://','http://','#')):continue
        check('Tautan lokal '+file.name,(file.parent/target.split('#')[0]).exists(),target)
for file in (ROOT/'scripts').glob('*.py'):
    ast.parse(file.read_text(encoding='utf-8'));check('Sintaks '+file.name,True)
summary={'tanggal':'2026-10-24','pemeriksaan_lulus':len(checks),'sumber_katalog':len(catalogue),'indikator':len(pd.read_csv(ROOT/'kamus_indikator.csv')),'pdf_tersimpan':len(list((ROOT/'data/raw').glob('*.pdf'))),'hasil':checks,'batas':'Pemeriksaan struktur dan rekonsiliasi serta beberapa halaman visual. Tidak ada uji signifikansi survei atau model spasial. Mikrodata penuh dan polygon sesuai belum tersedia; ZIP garis sudah diaudit.'}
(OUT/'validasi_paket.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='hasil'},ensure_ascii=True,indent=2))
