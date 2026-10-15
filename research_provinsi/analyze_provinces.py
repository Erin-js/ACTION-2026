from pathlib import Path
import re
import csv
import json
import pdfplumber

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'Indikator_Pasar_Tenaga_Kerja_Februari_2026_BPS.pdf'
URL = 'https://www.bps.go.id/id/publication/2026/06/26/f00a5821056e518c20d1546e/indikator-pasar-tenaga-kerja-indonesia-februari-2026.html'
PROVINCES = ['Aceh','Sumatera Utara','Sumatera Barat','Riau','Jambi','Sumatera Selatan','Bengkulu','Lampung','Kep. Bangka Belitung','Kepulauan Riau','DKI Jakarta','Jawa Barat','Jawa Tengah','DI Yogyakarta','Jawa Timur','Banten','Bali','Nusa Tenggara Barat','Nusa Tenggara Timur','Kalimantan Barat','Kalimantan Tengah','Kalimantan Selatan','Kalimantan Timur','Kalimantan Utara','Sulawesi Utara','Sulawesi Tengah','Sulawesi Selatan','Sulawesi Tenggara','Gorontalo','Sulawesi Barat','Maluku','Maluku Utara','Papua Barat','Papua Barat Daya','Papua','Papua Selatan','Papua Tengah','Papua Pegunungan','Indonesia']
data = {p:{'provinsi':p} for p in PROVINCES}

def numeric(token):
    return float(token.replace('.','').replace(',','.')) if ',' in token else int(token.replace('.',''))

with pdfplumber.open(SOURCE) as pdf:
    def read_table(page_number, count):
        page = pdf.pages[page_number-1].filter(lambda o: o.get('object_type') != 'char' or abs(o.get('matrix',(1,0,0,1,0,0))[1]) < 0.001)
        text = page.extract_text(x_tolerance=2)
        (ROOT / f'table_pdf_{page_number}.txt').write_text(text,encoding='utf-8')
        rows = {}
        for line in text.splitlines():
            match=re.match(r'^([^\d]+)\s+(\d.*)$',line)
            if not match:continue
            name=re.sub(r'[^A-Za-z]','',match[1])
            for province in sorted(PROVINCES,key=len,reverse=True):
                if name==re.sub(r'[^A-Za-z]','',province):
                    tokens = match[2].split()
                    values = [numeric(x) for x in tokens]
                    assert len(values)==count,(page_number,province,values)
                    rows[province]=values
                    break
        assert set(rows)==set(PROVINCES),(page_number, set(PROVINCES)-set(rows))
        return rows

    specs = [
        (161,6,{'usia_kerja_2025':2}),
        (162,3,{'usia_kerja_2026':2}),
        (164,6,{'angkatan_kerja_2025':2}),
        (165,3,{'angkatan_kerja_2026':2}),
        (169,9,{'tpak_2025':2,'tpak_2026':8,'tpak_laki_2026':6,'tpak_perempuan_2026':7}),
        (170,6,{'bekerja_2025':2}),
        (171,3,{'bekerja_2026':2}),
        (172,9,{'epr_2025':2,'epr_2026':8}),
        (174,9,{'pekerja_keluarga_2025':6,'pekerja_keluarga_2026':8}),
        (180,9,{'paruh_waktu_orang_2025':0,'paruh_waktu_orang_2026':2,'paruh_waktu_persen_2025':3,'paruh_waktu_persen_2026':5}),
        (182,6,{'jam_1_34_persen_2025':3,'jam_1_34_persen_2026':5}),
        (183,6,{'jam_49plus_2025':3,'jam_49plus_2026':5}),
        (184,6,{'formal_2025':0,'formal_2026':2,'informal_2025':3,'informal_2026':5}),
        (185,9,{'tpt_2025':2,'tpt_2026':8,'tpt_laki_2026':6,'tpt_perempuan_2026':7}),
        (186,9,{'tpt_pendidikan_dasar_2026':2,'tpt_pendidikan_menengah_2026':5,'tpt_pendidikan_tinggi_2026':8}),
        (189,3,{'bukan_angkatan_kerja_2025':0,'bukan_angkatan_kerja_2026':2}),
        (192,9,{'upah_buruh_2025_rupiah':2,'upah_buruh_2026_rupiah':8,'upah_buruh_laki_2026_rupiah':6,'upah_buruh_perempuan_2026_rupiah':7}),
        (211,7,{'tpt_2026_rse':2,'tpt_2026_ci_lower':3,'tpt_2026_ci_upper':4}),
    ]
    provenance = {}
    for page_number,count,fields in specs:
        rows=read_table(page_number,count)
        for province,values in rows.items():
            for field,index in fields.items():data[province][field]=values[index]
        for field in fields:provenance[field]={'pdf_page':page_number,'printed_page':page_number-28,'source':URL}

for p,d in data.items():
    for year in [2025,2026]:
        d[f'penganggur_{year}']=d[f'angkatan_kerja_{year}']-d[f'bekerja_{year}']
        assert d[f'usia_kerja_{year}']==d[f'angkatan_kerja_{year}']+d[f'bukan_angkatan_kerja_{year}']
        assert abs(100*d[f'penganggur_{year}']/d[f'angkatan_kerja_{year}']-d[f'tpt_{year}'])<0.006
        assert abs(d[f'formal_{year}']+d[f'informal_{year}']-100)<0.011
    d['delta_angkatan_kerja']=d['angkatan_kerja_2026']-d['angkatan_kerja_2025']
    d['delta_bekerja']=d['bekerja_2026']-d['bekerja_2025']
    d['selisih_penyerapan']=d['delta_bekerja']-d['delta_angkatan_kerja']
    d['delta_penganggur']=d['penganggur_2026']-d['penganggur_2025']
    assert d['selisih_penyerapan']==-d['delta_penganggur']
    d['selisih_penyerapan_per_1000_ak2025']=d['selisih_penyerapan']/d['angkatan_kerja_2025']*1000
    d['delta_tpt_pp']=round(d['tpt_2026']-d['tpt_2025'],2)
    d['delta_tpak_pp']=round(d['tpak_2026']-d['tpak_2025'],2)
    d['delta_informal_pp']=round(d['informal_2026']-d['informal_2025'],2)
    d['setengah_penganggur_perkiraan_2025']=round(d['jam_1_34_persen_2025']-d['paruh_waktu_persen_2025'],2)
    d['setengah_penganggur_perkiraan_2026']=round(d['jam_1_34_persen_2026']-d['paruh_waktu_persen_2026'],2)
    d['gap_tpak_gender_pp']=round(d['tpak_laki_2026']-d['tpak_perempuan_2026'],2)
    d['upah_growth_nominal_persen']=(d['upah_buruh_2026_rupiah']/d['upah_buruh_2025_rupiah']-1)*100
    d['status_dinamika']=('AK naik, bekerja naik, penganggur turun' if d['delta_angkatan_kerja']>0 and d['delta_bekerja']>0 and d['selisih_penyerapan']>0 else 'AK naik, bekerja naik, penganggur naik' if d['delta_angkatan_kerja']>0 and d['delta_bekerja']>0 else 'AK turun, bekerja turun, penganggur naik' if d['delta_angkatan_kerja']<0 and d['delta_bekerja']<0 and d['delta_penganggur']>0 else 'AK turun, bekerja turun, penganggur turun' if d['delta_angkatan_kerja']<0 and d['delta_bekerja']<0 else 'Periksa pola lain')

provinces=[data[p] for p in PROVINCES[:-1]]
for field in ['usia_kerja_2025','usia_kerja_2026','angkatan_kerja_2025','angkatan_kerja_2026','bekerja_2025','bekerja_2026','bukan_angkatan_kerja_2025','bukan_angkatan_kerja_2026','paruh_waktu_orang_2025','paruh_waktu_orang_2026']:
    assert sum(d[field] for d in provinces)==data['Indonesia'][field],(field,sum(d[field] for d in provinces),data['Indonesia'][field])

with (ROOT/'data_38_provinsi_feb2025_feb2026.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(data['Aceh']));w.writeheader();w.writerows(provinces+[data['Indonesia']])
(ROOT/'data_provinsi.json').write_text(json.dumps({'source':URL,'provenance':provenance,'data':provinces,'national':data['Indonesia']},ensure_ascii=False,indent=2),encoding='utf-8')
print('Complete: 38 provinces plus national; raw integer totals reconcile.')
print(json.dumps(data['Indonesia'],ensure_ascii=False,indent=2))
