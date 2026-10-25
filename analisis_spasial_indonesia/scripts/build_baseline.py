from pathlib import Path
import pandas as pd
import json, shutil, hashlib

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'analisis_gender_jambi'
RAW=ROOT/'data/raw'
OUT=ROOT/'data/processed'
OUT.mkdir(parents=True,exist_ok=True)
copies=[('data/raw/panel_nasional_38_provinsi.csv','panel_nasional_sumber_lokal.csv'),('data/raw/kamus_panel_nasional.csv','kamus_panel_sumber_lokal.csv'),('data/raw/BPS_IPTK_Feb2026.pdf','BPS_IPTK_Feb2026.pdf')]
provenance=[]
for src,dst in copies:
    origin=OLD/src; target=RAW/dst
    if not target.exists(): shutil.copy2(origin,target)
    provenance.append({'file':str(target.relative_to(ROOT)),'origin':str(origin),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'catatan':'Disalin dari riset lokal terdahulu; bukan unduhan baru. Sumber asal BPS IPTK Februari 2026.'})
(ROOT/'data/local_provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
df=pd.read_csv(RAW/'panel_nasional_sumber_lokal.csv')
assert len(df)==117
cols=['provinsi','periode','wilayah','puk_laki','puk_perempuan','ak_laki','ak_perempuan','bekerja_laki','bekerja_perempuan','tpak_laki','tpak_perempuan','epr_laki','epr_perempuan','tpt_laki','tpt_perempuan','upah_laki','upah_perempuan']
data=df[cols].copy()
for sex in ['laki','perempuan']:
    data['penganggur_'+sex]=data['ak_'+sex]-data['bekerja_'+sex]
    data['bak_'+sex]=data['puk_'+sex]-data['ak_'+sex]
    for indicator,num,den in [('tpak','ak','puk'),('epr','bekerja','puk'),('tpt','penganggur','ak')]:
        data[indicator+'_'+sex]=100*data[num+'_'+sex]/data[den+'_'+sex]
data['gap_tpak_pp']=data.tpak_laki-data.tpak_perempuan
data['source_id']='BPS_IPTK_2026'
data['status']='Estimasi survei; disalin dari panel lokal terdahulu; perhitungan rasio dari jumlah'
data.to_csv(OUT/'panel_gender_38_provinsi_3_periode.csv',index=False,encoding='utf-8-sig')
feb=data[data.periode.isin(['2025-02','2026-02'])].copy()
old=feb[feb.periode=='2025-02'].set_index('provinsi')
new=feb[feb.periode=='2026-02'].set_index('provinsi')
changes=pd.DataFrame(index=new.index)
for col in ['tpak_perempuan','epr_perempuan','tpt_perempuan','gap_tpak_pp','bekerja_perempuan','ak_perempuan','bak_perempuan','bekerja_laki']:
    changes[col+'_2025']=old[col]
    changes[col+'_2026']=new[col]
    changes['perubahan_'+col]=new[col]-old[col]
changes['tpak_perempuan_turun']=changes.perubahan_tpak_perempuan < -0.02
changes['tpt_dan_tpak_perempuan_turun']=(changes.perubahan_tpt_perempuan < -0.02)&changes.tpak_perempuan_turun
changes['kebutuhan_bekerja_terhambat_terbukti']='BELUM DIUKUR'
changes['catatan']='Saringan deskriptif, bukan peringkat urgensi; ambang 0,02 pp hanya toleransi pembulatan, bukan signifikansi'
changes.reset_index().to_csv(OUT/'screening_perubahan_provinsi_feb2025_feb2026.csv',index=False,encoding='utf-8-sig')
p=changes.drop(index='Indonesia')
national=changes.loc['Indonesia']
summary={'rows_panel':len(data),'provinces':data[data.wilayah=='Provinsi'].provinsi.nunique(),'periods':sorted(data.periode.unique()),'n_prov_tpak_perempuan_turun':int(p.tpak_perempuan_turun.sum()),'n_prov_tpt_dan_tpak_perempuan_turun':int(p.tpt_dan_tpak_perempuan_turun.sum()),'nasional_tpak_perempuan_2025':float(national.tpak_perempuan_2025),'nasional_tpak_perempuan_2026':float(national.tpak_perempuan_2026),'nasional_delta_tpak_pp':float(national.perubahan_tpak_perempuan),'daerah_tpak_turun':p[p.tpak_perempuan_turun].sort_values('perubahan_tpak_perempuan').index.tolist(),'status':'Belum mengukur urgensi, hambatan individual, atau signifikansi survei.'}
(OUT/'baseline_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
assert data.groupby('periode').size().eq(39).all()
assert data[['puk_laki','puk_perempuan','ak_laki','ak_perempuan','bekerja_laki','bekerja_perempuan']].notna().all().all()
assert (data.ak_perempuan >= data.bekerja_perempuan).all()
assert (data.puk_perempuan >= data.ak_perempuan).all()
print(json.dumps(summary,ensure_ascii=True,indent=2))
