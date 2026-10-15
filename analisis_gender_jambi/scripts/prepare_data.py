from pathlib import Path
import re
import json
import shutil
import hashlib
import pandas as pd
import pdfplumber

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'
OUT=ROOT/'data/processed'
OLD=ROOT.parent/'analisis_kecukupan_kerja'
for relative,old in [('panel_nasional_38_provinsi.csv',OLD/'data/processed/panel_38_provinsi_3_periode.csv'),('BPS_IPTK_Feb2026.pdf',OLD/'data/raw/BPS_Indikator_Pasar_Tenaga_Kerja_Februari_2026.pdf'),('kamus_panel_nasional.csv',OLD/'data/processed/kamus_data.csv')]:
    if not (RAW/relative).exists():shutil.copy2(old,RAW/relative)

panel=pd.read_csv(RAW/'panel_nasional_38_provinsi.csv')
checks=[]
def check(name,condition,detail=''):
    assert condition,(name,detail)
    checks.append({'pemeriksaan':name,'hasil':'LULUS','rincian':str(detail)})

def clean_page(name,page):
    path=RAW/f'{name}_p{page}.txt'
    if path.exists():return path.read_text(encoding='utf-8')
    with pdfplumber.open(RAW/(name+'.pdf')) as pdf:
        p=pdf.pages[page-1].filter(lambda o:o.get('object_type')!='char' or abs(o.get('matrix',(1,0,0,1,0,0))[1])<.001)
        text=p.extract_text(x_tolerance=2)
    path.write_text(text,encoding='utf-8')
    return text

def num(token):
    if token in ['–','—','-']:return 0
    if token in ['NA','...']:return None
    return float(token.replace('.','').replace(',','.')) if ',' in token else int(token.replace('.',''))

def age_rows(text):
    result={}
    for line in text.splitlines():
        m=re.match(r'^(15[–-]19|20[–-]24|25[–-]29|30[–-]34|35[–-]39|40[–-]44|45[–-]49|50[–-]54|55[–-]59|60\s*\+)\s+(.*)$',line)
        if m:result[m[1].replace('–','-').replace(' ','')]=[num(t) for t in m[2].split()]
    check('Sepuluh kelompok umur lengkap',len(result)==10)
    return result

def total_row(text):
    line=next(x for x in text.splitlines() if re.match(r'^Jumlah/\s*Total\s+',x))
    return [num(x) for x in re.sub(r'^Jumlah/\s*Total\s+','',line).split()]

ages=[]
education=[]
status=[]
sectors=[]
status_names=['Berusaha sendiri','Dibantu buruh tidak tetap/tidak dibayar','Dibantu buruh tetap','Buruh/karyawan/pegawai','Pekerja bebas','Pekerja keluarga/tidak dibayar']
sector_codes=['A','B','C','D','E','F','G','H','I','J','K','L','M,N','O','P','Q','R,S,T,U']
sector_names=['Pertanian','Pertambangan','Industri pengolahan','Listrik dan gas','Air dan limbah','Konstruksi','Perdagangan','Transportasi','Akomodasi dan makan minum','Informasi dan komunikasi','Keuangan','Real estat','Jasa perusahaan','Administrasi pemerintahan','Pendidikan','Kesehatan dan sosial','Jasa lainnya']
education_names=['SD ke bawah','SMP','SMA','SMK','Diploma I/II/III','Universitas']
for year,age_pages,edu_pages,sector_pages,status_pages in [(2024,[38,39],[44,45],[(60,61),(62,63)],[65,66]),(2025,[42,43],[48,49],[(61,62),(63,64)],[66,67])]:
    book=f'Jambi_Feb{year}'
    for sex,ap,ep,sp,stp in zip(['Laki-laki','Perempuan'],age_pages,edu_pages,sector_pages,status_pages):
        af=age_rows(clean_page(book,ap))
        for age,values in af.items():
            if year==2024:
                check('Jumlah kolom umur 2024',len(values)==13,(sex,age,len(values)))
                values=[values[0],values[3],values[4],*values[5:]]
            check('Jumlah kolom aktivitas',len(values)==11,(year,sex,age))
            d=dict(zip(['bekerja','penganggur','ak','sekolah','mengurus_rt','lainnya','bak','puk','tkk_tabel','tpt_tabel','tpak_tabel'],values))
            for key in ['bekerja','penganggur','ak','sekolah','mengurus_rt','lainnya','bak','puk']:d[key]=int(d[key])
            check('Identitas AK umur',d['ak']==d['bekerja']+d['penganggur'],(year,sex,age))
            check('Identitas PUK umur',d['puk']==d['ak']+d['bak'],(year,sex,age))
            check('Identitas kegiatan BAK umur',d['bak']==d['sekolah']+d['mengurus_rt']+d['lainnya'],(year,sex,age))
            ages.append(dict(periode=f'{year}-02',jenis_kelamin=sex,umur=age,**d,sumber=book,halaman_pdf=ap))
        es=clean_page(book,ep)
        for line in es.splitlines():
            m=re.match(r'^([0-7])\s+(\S.*)$',line)
            if not m:continue
            tokens=m[2].split()
            if len(tokens)!=(13 if year==2024 else 11):continue
            vals=[num(x) for x in tokens]
            if year==2024:vals=[vals[0],vals[3],vals[4],*vals[5:]]
            code=int(m[1]); group=(0 if code<3 else code-2) if year==2024 else code-1
            d=dict(zip(['bekerja','penganggur','ak','sekolah','mengurus_rt','lainnya','bak','puk','tkk_tabel','tpt_tabel','tpak_tabel'],vals))
            education.append(dict(periode=f'{year}-02',jenis_kelamin=sex,pendidikan=education_names[group],**d,sumber=book,halaman_pdf=ep))
        sr=age_rows(clean_page(book,stp))
        for age,vals in sr.items():
            check('Status berjumlah bekerja menurut umur',len(vals)==7 and sum(vals[:6])==vals[6],(year,sex,age))
            for name,v in zip(status_names,vals[:6]):status.append(dict(periode=f'{year}-02',jenis_kelamin=sex,umur=age,status=name,jumlah=v,sumber=book,halaman_pdf=stp))
        first=age_rows(clean_page(book,sp[0]));last=age_rows(clean_page(book,sp[1]))
        for age in first:
            vals=first[age]+last[age]
            check('Sektor berjumlah bekerja menurut umur',len(vals)==18 and sum(vals[:17])==vals[17],(year,sex,age))
            for code,name,v in zip(sector_codes,sector_names,vals[:17]):sectors.append(dict(periode=f'{year}-02',jenis_kelamin=sex,umur=age,kode_sektor=code,sektor=name,jumlah=v,klasifikasi='KBLI 2020',sumber=book,halaman_pdf=f'{sp[0]};{sp[1]}'))

age=pd.DataFrame(ages)
edu=pd.DataFrame(education)
edu=edu.groupby(['periode','jenis_kelamin','pendidikan','sumber','halaman_pdf'],as_index=False)[['bekerja','penganggur','ak','sekolah','mengurus_rt','lainnya','bak','puk']].sum()
for df in [age,edu]:
    df['tpak']=100*df.ak/df.puk
    df['tpt']=100*df.penganggur/df.ak
    df['epr']=100*df.bekerja/df.puk
    df['rt_per_puk']=100*df.mengurus_rt/df.puk
    df['rt_per_bak']=100*df.mengurus_rt/df.bak

summary=[]
for (period,sex),g in age.groupby(['periode','jenis_kelamin']):
    sums=g[['bekerja','penganggur','ak','sekolah','mengurus_rt','lainnya','bak','puk']].sum()
    summary.append(dict(periode=period,jenis_kelamin=sex,**sums.to_dict(),sumber=g.sumber.iloc[0],halaman_pdf=g.halaman_pdf.iloc[0]))
    e=edu.query('periode == @period and jenis_kelamin == @sex')
    for col in ['bekerja','penganggur','ak','sekolah','mengurus_rt','lainnya','bak','puk']:
        check('Rekonsiliasi umur-pendidikan',sums[col]==e[col].sum(),(period,sex,col))

history=[]
base=pd.DataFrame(summary)
for _,r in base.query("periode == '2024-02'").iterrows():
    history.append(dict(provinsi='Jambi',periode=r.periode,jenis_kelamin=r.jenis_kelamin,**r[['puk','ak','bekerja','penganggur','bak']].to_dict(),upah=None,sumber=r.sumber,halaman_pdf=str(r.halaman_pdf)))
for _,r in panel.iterrows():
    for sex,suffix in [('Laki-laki','laki'),('Perempuan','perempuan')]:
        history.append(dict(provinsi=r.provinsi,periode=r.periode,jenis_kelamin=sex,puk=int(r['puk_'+suffix]),ak=int(r['ak_'+suffix]),bekerja=int(r['bekerja_'+suffix]),penganggur=int(r['ak_'+suffix]-r['bekerja_'+suffix]),bak=int(r['puk_'+suffix]-r['ak_'+suffix]),upah=r['upah_'+suffix],sumber='BPS_IPTK_2026',halaman_pdf='161–171;192'))
hist=pd.DataFrame(history)
for f,numr,den in [('tpak','ak','puk'),('epr','bekerja','puk'),('tpt','penganggur','ak')]:hist[f]=100*hist[numr]/hist[den]
hist['tkk']=100-hist.tpt
hist['periode_label']=hist.periode.str.replace('-02',' Februari').str.replace('-08',' Agustus')
for sex in ['Laki-laki','Perempuan']:
    b=base.query("periode == '2025-02' and jenis_kelamin == @sex").iloc[0]
    h=hist.query("provinsi=='Jambi' and periode=='2025-02' and jenis_kelamin == @sex").iloc[0]
    for f in ['puk','ak','bekerja','penganggur','bak']:check('BPS Jambi dan BPS nasional konsisten',b[f]==h[f],(sex,f))

for name,df in [('aktivitas_umur_feb2024_2025',age),('aktivitas_pendidikan_feb2024_2025',edu),('status_umur_feb2024_2025',pd.DataFrame(status)),('sektor_umur_feb2024_2025',pd.DataFrame(sectors)),('aktivitas_total_feb2024_2025',base),('panel_gender_38_provinsi',hist)]:
    df.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')

admin=pd.read_csv(RAW/'SDI_Jambi_Pencari_Kerja_2023.csv')
regencies={1501:'Kerinci',1502:'Merangin',1503:'Sarolangun',1504:'Batang Hari',1505:'Muaro Jambi',1506:'Tanjung Jabung Timur',1507:'Tanjung Jabung Barat',1508:'Tebo',1509:'Bungo',1571:'Kota Jambi',1572:'Kota Sungai Penuh'}
admin['kabupaten_kota']=admin.kode_kabupaten_kota.map(regencies)
admin['jenis_kelamin']=admin.jenis_kelamin.map({'LAKI-LAKI':'Laki-laki','PEREMPUAN':'Perempuan'})
months=['JANUARI','FEBRUARI','MARET','APRIL','MEI','JUNI','JULI','AGUSTUS','SEPTEMBER','OKTOBER','NOVEMBER','DESEMBER']
admin['bulan_angka']=admin.bulan.map({m:i+1 for i,m in enumerate(months)})
check('SDI grid lengkap 11×12×2',len(admin)==264 and not admin.duplicated(['kode_kabupaten_kota','bulan_angka','jenis_kelamin','tahun']).any())
check('SDI kode wilayah terpetakan',admin.kabupaten_kota.notna().all())
check('SDI tidak ada jumlah negatif',(admin.jumlah>=0).all())
admin['sumber']='SDI_JAMBI_PENCAKER_2023'
admin.to_csv(OUT/'pencari_kerja_terdaftar_2023.csv',index=False,encoding='utf-8-sig')

context=[]
def ctx(ind,group,value,den,page):context.append(dict(periode='2024-08',indikator=ind,jenis_kelamin=group,nilai=value,satuan='persen',penyebut=den,sumber='BPS_GENDER_JAMBI_2024',halaman_pdf=page))
for sex,vals in [('Laki-laki',[86.04,83.73,2.68,28.67,8.52,54.48]),('Perempuan',[51.17,47.27,7.62,43.66,8.25,65.43])]:
    for ind,val,den,page in zip(['tpak','epr','tpt','pekerja_tidak_penuh','under','informal'],vals,['PUK jenis kelamin','PUK jenis kelamin','AK jenis kelamin','Bekerja jenis kelamin','Bekerja jenis kelamin','Bekerja jenis kelamin'],[33,37,42,44,48,56]):ctx(ind,sex,val,den,page)
for sex,vals in [('Laki-laki',[23.83,14.84,10.43,5.37]),('Perempuan',[23.70,10.17,4.00,27.56])]:
    for ind,val in zip(['berusaha_sendiri','dibantu_tidak_tetap','pekerja_bebas','pekerja_keluarga'],vals):ctx(ind,sex,val,'Bekerja jenis kelamin',57)
for reg,l,f in [('Kerinci',88.08,63.38),('Merangin',84.92,57.96),('Sarolangun',84.80,43.88),('Batang Hari',83.07,37.43),('Muaro Jambi',87.70,44.38),('Tanjung Jabung Timur',87.72,39.74),('Tanjung Jabung Barat',83.71,46.30),('Tebo',85.65,48.32),('Bungo',83.28,45.95),('Kota Jambi',77.40,45.57),('Kota Sungai Penuh',76.24,50.79)]:
    for sex,val in [('Laki-laki',l),('Perempuan',f)]:context.append(dict(periode='2024-08',indikator='epr_kabupaten',jenis_kelamin=sex,nilai=val,satuan='persen',penyebut='PUK jenis kelamin di '+reg,sumber='BPS_GENDER_JAMBI_2024',halaman_pdf=38))
pd.DataFrame(context).to_csv(RAW/'transkripsi_konteks_gender_agustus2024.csv',index=False,encoding='utf-8-sig')

context25=[]
for sex,vals in [('Laki-laki',[85.60,4.04,31.88,22.01,9.87,21.01,14.53,5.65,13.30,9.19]),('Perempuan',[50.63,4.63,44.06,35.85,8.21,20.20,11.93,24.33,5.68,17.04])]:
    for ind,val,den,page in zip(['tpak','tpt','pekerja_tidak_penuh','paruh','under','berusaha_sendiri','dibantu_tidak_tetap','pekerja_keluarga','pekerja_bebas','jam_kurang15'],vals,['PUK kelompok','AK kelompok',*['Bekerja kelompok']*8],[33,42,44,46,47,56,56,56,56,49]):
        context25.append(dict(periode='2025-08',indikator=ind,jenis_kelamin=sex,nilai=val,satuan='persen',penyebut=den,sumber='BPS_GENDER_JAMBI_2025',halaman_pdf=page))
context25.append(dict(periode='2025-08',indikator='mengurus_rt_per_puk',jenis_kelamin='Perempuan',nilai=38.18,satuan='persen',penyebut='PUK perempuan',sumber='BPS_GENDER_JAMBI_2025',halaman_pdf=34))
for sex,value in [('Laki-laki',41.19),('Perempuan',56.45)]:
    context25.append(dict(periode='2025-08',indikator='tiga_status_resmi',jenis_kelamin=sex,nilai=value,satuan='persen',penyebut='Bekerja kelompok',sumber='BPS_GENDER_JAMBI_2025',halaman_pdf=56))
pd.DataFrame(context25).to_csv(RAW/'transkripsi_konteks_gender_agustus2025.csv',index=False,encoding='utf-8-sig')
reg25=[]
for reg,l,f in [('Kerinci',81.94,63.98),('Merangin',83.81,47.61),('Sarolangun',84.73,45.22),('Batang Hari',81.37,45.29),('Muaro Jambi',84.49,54.95),('Tanjung Jabung Timur',83.48,50.97),('Tanjung Jabung Barat',84.17,36.82),('Tebo',86.41,41.58),('Bungo',84.14,49.20),('Kota Jambi',74.62,48.27),('Kota Sungai Penuh',76.75,55.61)]:
    for sex,val in [('Laki-laki',l),('Perempuan',f)]:reg25.append(dict(periode='2025-08',kabupaten_kota=reg,jenis_kelamin=sex,epr=val,sumber='BPS_GENDER_JAMBI_2025',halaman_pdf=38))
pd.DataFrame(reg25).to_csv(RAW/'transkripsi_epr_kabupaten_agustus2025.csv',index=False,encoding='utf-8-sig')
ageaug=[]
for year,sex,vals in [(2024,'Laki-laki',[29.96,85.09,96.35,98.20,98.65,98.68,98.42,97.89,95.26,74.69]),(2024,'Perempuan',[19.85,55.03,53.63,51.85,56.04,61.68,64.94,62.48,58.76,38.67]),(2025,'Laki-laki',[34.56,83.94,97.90,98.99,98.32,99.00,98.40,97.06,91.63,69.37]),(2025,'Perempuan',[20.59,54.65,53.62,53.36,54.77,60.99,62.47,62.24,56.89,37.54])]:
    for agegroup,val in zip(af,vals):ageaug.append(dict(periode=f'{year}-08',jenis_kelamin=sex,umur=agegroup,tpak=val,sumber=f'BPS_GENDER_JAMBI_{year}',halaman_pdf=34))
pd.DataFrame(ageaug).to_csv(RAW/'transkripsi_tpak_umur_agustus2024_2025.csv',index=False,encoding='utf-8-sig')
sec25=[]
for sex,vals in [('Laki-laki',[48.31,5.81,4.92,.24,.26,6.61,13.71,4.94,2.91,.44,.77,.18,1.38,4.30,2.71,.67,1.85]),('Perempuan',[34.68,.62,5.72,.13,.43,.81,21.87,.38,10.28,.68,.83,.02,.67,4.63,11.03,3.42,3.79])]:
    check('Pangsa sektor Agustus 2025 sekitar 100',abs(sum(vals)-100)<.04,sex)
    for c,s,v in zip(sector_codes,sector_names,vals):sec25.append(dict(periode='2025-08',jenis_kelamin=sex,kode_sektor=c,sektor=s,persen=v,klasifikasi='KBLI 2020',sumber='BPS_GENDER_JAMBI_2025',halaman_pdf=39))
pd.DataFrame(sec25).to_csv(RAW/'transkripsi_sektor_agustus2025.csv',index=False,encoding='utf-8-sig')
source_audit=[
 {'sumber':'BPS_GENDER_JAMBI_2025','halaman_pdf':'56','masalah':'Komponen perempuan 20,20 + 11,93 + 24,33 = 56,46; total resmi 56,45','keputusan':'Pakai total resmi 56,45; selisih pembulatan 0,01 pp dicatat'},
 {'sumber':'BPS_GENDER_JAMBI_2025','halaman_pdf':'34','masalah':'Narasi TPAK laki-laki 40–44 tahun 99,90; grafik 99,00','keputusan':'Pakai angka grafik 99,00 yang diperiksa secara visual; catat konflik'},
 {'sumber':'BPS_GENDER_JAMBI_2025','halaman_pdf':'47','masalah':'Narasi under laki-laki 8,52; grafik 9,87','keputusan':'Pakai grafik 9,87, konsisten dengan 31,88 - 22,01 = 9,87'},
 {'sumber':'BPS_GENDER_JAMBI_2024;BPS_GENDER_JAMBI_2025','halaman_pdf':'57;56','masalah':'2024 total rentan mencakup pekerja bebas; tabel tiga status 2025 tidak','keputusan':'Hitung ulang tiga status yang sama; formalitas 2025 boleh dihitung dari semua status informal sebagai turunan'},
 {'sumber':'BPS_BRS_JAMBI_2026','halaman_pdf':'Halaman web abstraksi','masalah':'Under disebut turun 15,47 persen poin','keputusan':'Tidak dipakai; tidak sesuai skala indikator dalam tabel nasional'},
 {'sumber':'BPS_GENDER_JAMBI_2024;BPS_GENDER_JAMBI_2025','halaman_pdf':'Narasi sejumlah bab','masalah':'Narasi normatif peran gender dan dugaan penyebab tidak disertai pengujian dalam tabulasi','keputusan':'Gunakan angka terverifikasi; narasi tersebut bukan instruksi, fakta kausal, atau kesimpulan notebook'},
]
pd.DataFrame(source_audit).to_csv(OUT/'audit_kritik_sumber.csv',index=False,encoding='utf-8-sig')

sources=[
 {'id':'BPS_IPTK_2026','judul':'Indikator Pasar Tenaga Kerja Indonesia Februari 2026','url':'https://www.bps.go.id/id/publication/2026/06/26/f00a5821056e518c20d1546e/indikator-pasar-tenaga-kerja-indonesia-februari-2026.html','produsen':'BPS','periode':'Feb 2025, Agu 2025, Feb 2026','rilis':'2026-06-26','status':'Numerik: panel 38 provinsi, gender, upah, RSE TPT total','berkas':'data/raw/BPS_IPTK_Feb2026.pdf','batas':'RSE gender dan varians selisih tidak dicakup panel; sebagian indikator lama hasil turunan tidak menjadi bukti penyebab.'},
 {'id':'Jambi_Feb2024','judul':'Keadaan Angkatan Kerja Provinsi Jambi Februari 2024','url':'https://jambi.bps.go.id/id/publication/2024/10/15/3adc831481925a5d4c1db8a7/keadaan-angkatan-kerja-provinsi-jambi-februari-2024.html','produsen':'BPS Provinsi Jambi','periode':'Feb 2024','rilis':'2024-10-15','status':'Numerik: umur, pendidikan, sektor, status, kegiatan BAK','berkas':'data/raw/Jambi_Feb2024.pdf','batas':'Tabulasi sampel; sel rinci kecil perlu kehati-hatian; bukan panel individu.'},
 {'id':'Jambi_Feb2025','judul':'Keadaan Angkatan Kerja Provinsi Jambi Februari 2025','url':'https://jambi.bps.go.id/id/publication/2025/10/15/b34e37af1c865d4f14110a15/keadaan-angkatan-kerja-provinsi-jambi-februari-2025.html','produsen':'BPS Provinsi Jambi','periode':'Feb 2025','rilis':'2025-10-15','status':'Numerik: umur, pendidikan, sektor, status, kegiatan BAK','berkas':'data/raw/Jambi_Feb2025.pdf','batas':'SD ke bawah digabung dari tiga kategori 2024 agar sebanding; penyebab perubahan 2026 belum dapat diidentifikasi.'},
 {'id':'BPS_GENDER_JAMBI_2024','judul':'Analisis Gender Provinsi Jambi 2024','url':'https://jambi.bps.go.id/id/publication/2025/07/28/1c440abe44b6428bb6416e13/analisis-gender-provinsi-jambi-2024.html','produsen':'BPS Provinsi Jambi','periode':'Sakernas Agu 2024; Susenas Mar 2024','rilis':'2025-07-28','status':'Numerik: konteks terpisah Agu 2024, termasuk 11 kabupaten/kota','berkas':'data/raw/Analisis_Gender_Jambi_2024.pdf','batas':'Tidak dijahit menjadi tren Februari; narasi tentang kewajiban peran gender dan interpretasi yang tidak sesuai tabel tidak diadopsi.'},
 {'id':'SDI_JAMBI_PENCAKER_2023','judul':'Data Pencari Kerja 2023','url':'https://opendata.jambiprov.go.id/web-datasets/9dea8a2f-794e-498f-9076-fa2ebd0b7394/data-pencari-kerja-2023','produsen':'Disnakertrans; walidata Diskominfo Jambi','periode':'Bulanan Jan–Des 2023; 11 kabupaten/kota; gender','rilis':'2025-01-08; pembaruan 2025-01-22','status':'Numerik: 264 baris CSV diunduh dari portal Satu Data/Open Data Jambi','berkas':'data/raw/SDI_Jambi_Pencari_Kerja_2023.csv','batas':'Pendaftaran layanan administratif, bukan seluruh penganggur; penjumlahan bulan belum menjamin orang unik.'},
 {'id':'BPS_BRS_JAMBI_2026','judul':'TPT Februari 2026 sebesar 3,99 persen','url':'https://jambi.bps.go.id/id/pressrelease/2026/05/05/853/tingkat-pengangguran-terbuka--tpt--februari-2026-sebesar-3-99-persen-.html','produsen':'BPS Provinsi Jambi','periode':'Feb 2026; perbandingan Feb 2025','rilis':'2026-05-05','status':'Pemeriksaan silang halaman resmi; bukan sumber rincian gender baru','berkas':'','batas':'Abstraksi menyebut under turun 15,47 pp, bertentangan dengan skala tabel nasional; klaim tersebut tidak dipakai.'},
 {'id':'SDI_MIRROR_FEB2025','judul':'Salinan publikasi Keadaan Angkatan Kerja Jambi Februari 2025','url':'https://jdac.jambiprov.go.id/assets/publikasi/1767758043.pdf','produsen':'BPS; salinan pada portal Pemerintah Provinsi Jambi','periode':'Feb 2025','rilis':'Publikasi asli 2025-10-15','status':'Ditemukan dan diperiksa metadata; unduhan penuh gagal, angka diambil dari berkas BPS asli','berkas':'','batas':'Tidak mengklaim mengunduh PDF ini dari portal SDI.'},
 {'id':'SDI_MIRROR_GENDER2024','judul':'Analisis Gender Provinsi Jambi 2024 (salinan SDI)','url':'https://satudata.jambiprov.go.id/assets/publikasi/1758769974.pdf','produsen':'BPS; salinan pada Satu Data Jambi','periode':'2024','rilis':'Publikasi asli 2025-07-28','status':'Metadata ditemukan; unduhan penuh gagal; memakai berkas asli BPS','berkas':'','batas':'Keberhasilan sumber numerik SDI dalam riset ini berasal dari CSV pencari kerja.'},
 {'id':'BPS_GENDER_JAMBI_2025','judul':'Analisis Gender Provinsi Jambi 2025','url':'https://jambi.bps.go.id/id/publication/2026/07/27/fa53cf73b32d0ab1a6895625/analisis-gender-provinsi-jambi-2025.html','produsen':'BPS Provinsi Jambi','periode':'Agu 2025 dan Mar 2025','rilis':'2026-07-27','status':'Publikasi lebih baru ditemukan; lihat addendum bila PDF berhasil diunduh','berkas':'','batas':'Tidak mengganti angka Feb 2026 dengan angka Agustus 2025.'},
 {'id':'BI_JAMBI_MEI2026','judul':'Laporan Perekonomian Provinsi Jambi Mei 2026','url':'https://www.bi.go.id/id/publikasi/laporan/lpp/Pages/Laporan-Perekonomian-Provinsi-Jambi-Mei-2026.aspx','produsen':'Bank Indonesia','periode':'Konteks triwulan I 2026; ketenagakerjaan Feb 2026','rilis':'Mei 2026','status':'Pendukung naratif dan pemeriksaan arah jumlah bekerja; bukan sumber angka gender','berkas':'','batas':'Pembulatan berbeda; penjelasan makro tidak membuktikan penyebab penyusutan pekerja perempuan.'},
 {'id':'WB_CHILDCARE','judul':'Access to childcare can improve women’s labor market outcomes in Indonesia','url':'https://www.worldbank.org/en/country/indonesia/publication/access-to-childcare-can-improve-womens-labor-market-outcomes-in-indonesia','produsen':'World Bank','periode':'Kajian Indonesia dengan periode berbeda dari 2026','rilis':'Tanggal laman tidak dipastikan','status':'Pendukung hipotesis pengasuhan; angka nasional lama tidak digabung ke panel','berkas':'','batas':'Bukti konteks nasional tidak membuktikan penyebab perubahan Jambi Feb 2025–Feb 2026.'},
]
for s in sources:
    if s['id']=='BPS_GENDER_JAMBI_2025':
        s['status']='Numerik: konteks Agu 2025, sektor, jam, status, umur, dan 11 kabupaten/kota'
        s['berkas']='data/raw/Analisis_Gender_Jambi_2025.pdf'
        s['batas']='Gunakan angka grafik terverifikasi saat narasi berbeda; tiga status rentan tidak sama dengan total informal.'
    s['tanggal_akses']='2026-10-15'
    s['sha256']=hashlib.sha256((ROOT/s['berkas']).read_bytes()).hexdigest() if s['berkas'] else ''
pd.DataFrame(sources).to_csv(ROOT/'sources.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(checks).to_csv(OUT/'audit_rekonsiliasi.csv',index=False,encoding='utf-8-sig')
dictionary=[]
for key,unit,den,definition in [('puk','orang','-','Penduduk usia 15 tahun ke atas'),('ak','orang','-','Bekerja + penganggur'),('bekerja','orang','-','Penduduk bekerja menurut Sakernas, termasuk pekerja keluarga dan sementara tidak bekerja'),('penganggur','orang','-','Penganggur menurut definisi Sakernas'),('bak','orang','-','PUK - AK; bukan otomatis orang yang ingin bekerja'),('sekolah','orang','-','Kegiatan utama di luar angkatan kerja: sekolah'),('mengurus_rt','orang','-','Kegiatan utama di luar angkatan kerja: mengurus rumah tangga; bukan seluruh pelaku kerja domestik'),('lainnya','orang','-','Kegiatan BAK lainnya; bukan ukuran langsung putus asa mencari kerja'),('tpak','persen','PUK kelompok','100 × AK/PUK'),('tpt','persen','AK kelompok','100 × penganggur/AK'),('epr','persen','PUK kelompok','100 × bekerja/PUK'),('tkk','persen','AK kelompok','100 - TPT; bukan EPR'),('upah','rupiah/bulan','Buruh/karyawan/pegawai kelompok','Rata-rata upah bersih nominal; bukan pendapatan semua pekerja'),('jumlah','orang atau catatan pendaftaran','Sesuai tabel','Hitungan pada status/sektor Sakernas; catatan layanan administratif pada dataset SDI'),('rt_per_puk','persen','PUK kelompok','100 × mengurus_rt/PUK'),('rt_per_bak','persen','BAK kelompok','100 × mengurus_rt/BAK')]:
    dictionary.append(dict(variabel=key,satuan=unit,penyebut=den,definisi=definition))
pd.DataFrame(dictionary).to_csv(OUT/'kamus_variabel_utama.csv',index=False,encoding='utf-8-sig')
print('Prepared',len(hist),'panel gender;',len(age),'umur;',len(edu),'pendidikan;',len(status),'status;',len(sectors),'sektor;',len(admin),'SDI;',len(checks),'checks passed.')
