from pathlib import Path
import re
import json
import csv
import shutil
import hashlib
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / 'research_provinsi'
RAW = ROOT / 'data/raw'
OUT = ROOT / 'data/processed'
SOURCE = RAW / 'BPS_Indikator_Pasar_Tenaga_Kerja_Februari_2026.pdf'
if not SOURCE.exists():
    shutil.copy2(OLD / 'Indikator_Pasar_Tenaga_Kerja_Februari_2026_BPS.pdf', SOURCE)
URL = 'https://www.bps.go.id/id/publication/2026/06/26/f00a5821056e518c20d1546e/indikator-pasar-tenaga-kerja-indonesia-februari-2026.html'
SULBAR = 'https://sulbar.bps.go.id/id/pressrelease/2026/05/05/1373/tingkat-pengangguran-terbuka--tpt--sulawesi-barat-pada-februari-2026-sebesar-2-93-persen--turun-0-24-persen-poin-dibanding-februari-2025.html'
OLD_DATA = json.loads((OLD / 'data_provinsi.json').read_text(encoding='utf-8'))
PROVINCES = [x['provinsi'] for x in OLD_DATA['data']] + ['Indonesia']
PERIODS = ['2025-02', '2025-08', '2026-02']
rows = {(p, t): {'provinsi': p, 'periode': t, 'wilayah': 'Nasional' if p == 'Indonesia' else 'Provinsi'} for p in PROVINCES for t in PERIODS}
dictionary = []
checks = []

def write_csv(path, values):
    values = list(values)
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(values[0]))
        w.writeheader()
        w.writerows(values)

def num(x):
    return float(x.replace('.', '').replace(',', '.')) if ',' in x else int(x.replace('.', ''))

with pdfplumber.open(SOURCE) as pdf:
    def table(page, count):
        clean = pdf.pages[page - 1].filter(lambda o: o.get('object_type') != 'char' or abs(o.get('matrix', (1, 0, 0, 1, 0, 0))[1]) < .001)
        text = clean.extract_text(x_tolerance=2)
        (RAW / f'nasional_halaman_{page}.txt').write_text(text, encoding='utf-8')
        result = {}
        for line in text.splitlines():
            m = re.match(r'^([^\d]+)\s+(\d.*)$', line)
            if not m:
                continue
            name = re.sub('[^A-Za-z]', '', m[1])
            for p in PROVINCES:
                if re.sub('[^A-Za-z]', '', p) == name:
                    vals = [num(x) for x in m[2].split()]
                    assert len(vals) == count, (page, p, vals)
                    result[p] = vals
                    break
        assert set(result) == set(PROVINCES), (page, set(PROVINCES) - set(result))
        return result

    def add(page, count, fields):
        values = table(page, count)
        for field, indices, unit, denominator, definition in fields:
            for k, idx in enumerate(indices):
                if idx is not None:
                    for p in PROVINCES:
                        rows[p, PERIODS[k]][field] = values[p][idx]
            dictionary.append(dict(variabel=field, satuan=unit, penyebut=denominator, definisi=definition, sumber='BPS_IPTK_2026', halaman_pdf=page, halaman_cetak=page-28, metode='Angka tabel BPS'))

    for base, p1, p2 in [('puk', 161, 162), ('ak', 164, 165), ('bekerja', 170, 171)]:
        for page, count, indices in [(p1, 6, [[0,3,None],[1,4,None],[2,5,None]]), (p2,3,[[None,None,0],[None,None,1],[None,None,2]])]:
            add(page, count, [(base + suf, ix, 'orang', '-', {'puk':'Penduduk usia kerja 15 tahun ke atas', 'ak':'Angkatan kerja', 'bekerja':'Penduduk bekerja'}[base] + lab) for suf, ix, lab in zip(['_laki','_perempuan',''], indices, [' laki-laki',' perempuan',' total'])])
    for page, base, definition in [(169,'tpak','Angkatan kerja dibagi penduduk usia kerja'), (172,'epr','Bekerja dibagi penduduk usia kerja'), (185,'tpt','Penganggur dibagi angkatan kerja'), (192,'upah','Rata-rata upah/gaji bersih sebulan buruh/karyawan/pegawai')]:
        add(page,9,[(base+suf,[i,i+3,i+6],'rupiah/bulan' if base=='upah' else 'persen', 'Buruh/karyawan/pegawai' if base=='upah' else ('Angkatan kerja sesuai jenis kelamin' if base=='tpt' else 'Penduduk usia kerja sesuai jenis kelamin'), definition+lab) for i,suf,lab in [(0,'_laki',' laki-laki'),(1,'_perempuan',' perempuan'),(2,'',' total')]])
    add(173,9,[(f, [i,i+1,i+2], 'persen', 'Penduduk bekerja', d) for f,i,d in [('buruh',0,'Buruh/karyawan/pegawai'),('berusaha_tetap',3,'Berusaha dibantu buruh tetap'),('berusaha_tidak_tetap',6,'Berusaha dibantu buruh tidak tetap/tidak dibayar')]])
    add(174,9,[(f,[i,i+1,i+2],'persen','Penduduk bekerja',d) for f,i,d in [('berusaha_sendiri',0,'Berusaha sendiri'),('pekerja_bebas',3,'Pekerja bebas pertanian dan nonpertanian'),('pekerja_keluarga',6,'Pekerja keluarga/tidak dibayar')]])
    add(180,9,[('paruh_orang',[0,1,2],'orang','-','Pekerja <35 jam, tidak mencari dan tidak bersedia menerima pekerjaan lain'),('paruh',[3,4,5],'persen','Penduduk bekerja','Tingkat pekerja paruh waktu'),('share_perempuan_paruh',[6,7,8],'persen','Seluruh pekerja paruh waktu','Komposisi perempuan di antara pekerja paruh waktu; bukan tingkat paruh waktu perempuan')])
    add(182,6,[('jam0',[0,1,2],'persen','Penduduk bekerja','Sementara tidak bekerja'),('jam1_34',[3,4,5],'persen','Penduduk bekerja','Bekerja 1–34 jam seminggu')])
    add(183,6,[('jam35_48',[0,1,2],'persen','Penduduk bekerja','Bekerja 35–48 jam seminggu'),('jam49plus',[3,4,5],'persen','Penduduk bekerja','Bekerja minimal 49 jam seminggu; bukan bukti pelanggaran hukum')])
    add(184,6,[('formal',[0,1,2],'persen','Penduduk bekerja','Buruh/karyawan/pegawai dan berusaha dibantu buruh tetap'),('informal',[3,4,5],'persen','Penduduk bekerja','Status pekerjaan selain dua status formal BPS; bukan ukuran langsung kelayakan')])
    for page, prefix, definition, denominator in [(186,'tpt_edu','TPT dalam kelompok pendidikan','Angkatan kerja kelompok pendidikan'),(187,'share_u_edu','Komposisi pendidikan di antara penganggur','Seluruh penganggur'),(188,'share_under_edu','Komposisi pendidikan di antara setengah penganggur','Seluruh setengah penganggur'),(191,'share_ak_edu','Komposisi pendidikan di antara angkatan kerja','Seluruh angkatan kerja')]:
        add(page,9,[(prefix+'_'+g,[i,i+1,i+2],'persen',denominator,definition+' '+g) for g,i in [('dasar',0),('menengah',3),('tinggi',6)]])
    add(189,3,[('bak',[0,1,2],'orang','-','Bukan angkatan kerja; bukan otomatis penganggur tersembunyi')])
    add(211,7,[('tpt_se',[None,None,1],'persen poin','-','Standard error TPT Februari 2026'),('tpt_rse',[None,None,2],'persen','Estimasi TPT','Relative standard error TPT'),('tpt_ci_lower',[None,None,3],'persen','Angkatan kerja','Batas bawah selang kepercayaan TPT yang dipublikasikan BPS'),('tpt_ci_upper',[None,None,4],'persen','Angkatan kerja','Batas atas selang kepercayaan TPT yang dipublikasikan BPS')])
    for page in [106,108,175,176,177,178,179,181]:
        (RAW / f'nasional_halaman_{page}.txt').write_text(pdf.pages[page-1].filter(lambda o:o.get('object_type')!='char' or abs(o.get('matrix',(1,0,0,1,0,0))[1])<.001).extract_text(x_tolerance=2),encoding='utf-8')

for (p,t),r in rows.items():
    r['penganggur'] = r['ak'] - r['bekerja']
    r['under_turunan'] = round(r['jam1_34'] - r['paruh'],2)
    r['under'] = r['under_turunan']
    r['status_under'] = 'Turunan dua persentase dibulatkan; galat pembulatan sekitar 0,01 pp'
    if p=='Indonesia':
        r['under'] = [8.00,7.91,7.27][PERIODS.index(t)]
        r['status_under'] = 'Resmi: BPS IPTK PDF halaman 108'
    if p=='Sulawesi Barat' and t in ['2025-02','2026-02']:
        r['under'] = {'2025-02':14.15,'2026-02':13.36}[t]
        r['status_under'] = 'Resmi: BPS Sulbar PDF halaman 14–15'
    r['under_estimasi_orang'] = round(r['under']/100*r['bekerja'])
    r['gap_tpak_gender'] = round(r['tpak_laki']-r['tpak_perempuan'],2)
    r['gap_upah_gender_persen'] = 100*(r['upah_laki']-r['upah_perempuan'])/r['upah_laki']
    r['beban_u_under_persen_ak'] = 100*(r['penganggur']+r['under']/100*r['bekerja'])/r['ak']
    r['berat_penyebut'] = r['ak']/r['puk']
    assert r['puk']==r['ak']+r['bak']
    assert r['ak']==r['ak_laki']+r['ak_perempuan']
    assert r['bekerja']==r['bekerja_laki']+r['bekerja_perempuan']
    assert abs(100*r['penganggur']/r['ak']-r['tpt'])<.006
    assert abs(r['formal']+r['informal']-100)<.011
    assert abs(sum(r[x] for x in ['jam0','jam1_34','jam35_48','jam49plus'])-100)<.021
    assert abs(sum(r[x] for x in ['buruh','berusaha_tetap','berusaha_tidak_tetap','berusaha_sendiri','pekerja_bebas','pekerja_keluarga'])-100)<.031
    for k in ['tpt_se','tpt_rse','tpt_ci_lower','tpt_ci_upper']:
        r.setdefault(k,None)

for t in PERIODS:
    for f in ['puk','ak','bekerja','bak','paruh_orang','puk_laki','puk_perempuan','ak_laki','ak_perempuan','bekerja_laki','bekerja_perempuan']:
        total=sum(rows[p,t][f] for p in PROVINCES[:-1])
        assert total==rows['Indonesia',t][f],(t,f,total,rows['Indonesia',t][f])
        checks.append(dict(pemeriksaan='Jumlah 38 provinsi = Indonesia',periode=t,variabel=f,hasil='LULUS',nilai=total))

derived = [
 ('penganggur','orang','-','ak - bekerja'),
 ('under_turunan','persen','Penduduk bekerja','jam1_34 - paruh; selisih persentase dibulatkan'),
 ('under','persen','Penduduk bekerja','Angka resmi untuk Indonesia dan Sulbar Februari; turunan untuk lainnya; lihat status_under'),
 ('under_estimasi_orang','orang','-','under/100 × bekerja; estimasi bukan jumlah resmi'),
 ('gap_tpak_gender','persen poin','-','tpak_laki - tpak_perempuan'),
 ('gap_upah_gender_persen','persen','Upah rata-rata buruh laki-laki','100 × (upah laki-laki - perempuan)/laki-laki; gap kasar tanpa penyesuaian'),
 ('beban_u_under_persen_ak','persen','Angkatan kerja','100 × (penganggur + under/100 × bekerja)/ak; proksi turunan, bukan LU2 resmi'),
 ('berat_penyebut','proporsi','Penduduk usia kerja','ak / puk')]
for f,u,d,m in derived:
    dictionary.append(dict(variabel=f,satuan=u,penyebut=d,definisi=m,sumber='Turunan dari BPS; lihat sumber variabel asal',halaman_pdf='',halaman_cetak='',metode=m))
write_csv(OUT / 'panel_38_provinsi_3_periode.csv', rows.values())
write_csv(OUT / 'kamus_data.csv', dictionary)
write_csv(OUT / 'audit_rekonsiliasi.csv', checks)

context=[]
for group, rates, counts in [
 ('Indonesia',[8,7.91,7.27],[11.67,11.60,10.73]),
 ('Laki-laki',[8.36,8.30,7.60],[7.31,7.31,6.74]),
 ('Perempuan',[7.47,7.33,6.76],[4.36,4.29,3.98]),
 ('Perkotaan',[6.47,6.37,6.01],[5.56,5.59,5.42]),
 ('Perdesaan',[10.20,10.22,9.23],[6.11,6.01,5.30])]:
    for t, rate, count in zip(PERIODS,rates,counts):
        context.append(dict(kelompok=group,periode=t,tingkat_under=rate,jumlah_under_juta=count,sumber='BPS_IPTK_2026',halaman_pdf='106;108'))
write_csv(RAW / 'transkripsi_under_nasional.csv',context)

sectors=[('A','Pertanian, kehutanan, perikanan',42491616,50.83),('B','Pertambangan',1720729,.22),('C','Industri',20034316,7.60),('D','Listrik dan gas',361219,.14),('E','Air dan pengelolaan limbah',630034,.22),('F','Konstruksi',8968129,4.29),('G','Perdagangan',26505686,13.16),('H','Transportasi',6196271,2.39),('I','Akomodasi dan makan minum',11661902,3.61),('J,K','Penerbitan dan telekomunikasi',1237425,.45),('L','Keuangan dan asuransi',1741591,.45),('M','Real estat',563001,.08),('N,O','Profesional dan administrasi',2644411,.88),('P','Administrasi pemerintahan',5408301,5.98),('Q','Pendidikan',7379576,6.02),('R','Kesehatan dan sosial',2520232,1.27),('S,T,U,V','Kesenian dan jasa lainnya',7603191,2.42)]
assert sum(x[2] for x in sectors)==rows['Indonesia','2026-02']['bekerja']
write_csv(RAW/'transkripsi_sektor_2026.csv',[dict(kode=code,sektor=name,indonesia_orang=n,sulbar_persen=s,periode='2026-02',klasifikasi='KBLI 2025',sumber_nasional='BPS_IPTK_2026 PDF 177–178',sumber_sulbar='BPS_SULBAR_2026 PDF 15') for code,name,n,s in sectors])

sulbar=[]
specs=[('TPT','Laki-laki',2.27,2.15,2.92,10),('TPT','Perempuan',4.17,4.73,2.95,10),('TPT','Perkotaan',3.42,5.74,4.12,10),('TPT','Perdesaan',2.91,2.39,2.51,10),('TPT pendidikan','SD ke bawah',2.45,2.95,2.86,10),('TPT pendidikan','SMP',1.10,2.39,1.62,10),('TPT pendidikan','SMA',4.47,4.04,3.15,10),('TPT pendidikan','SMK',8.09,1.16,2.72,10),('TPT pendidikan','Diploma I/II/III',None,8.85,None,10),('TPT pendidikan','Diploma IV/S1/S2/S3',2.89,3.74,4.60,10),('Setengah pengangguran','Laki-laki',16.36,14.26,15.11,8),('Setengah pengangguran','Perempuan',11.93,13.99,10.80,8),('Setengah pengangguran','Total',14.63,14.15,13.36,8),('Paruh waktu','Laki-laki',30.90,30.40,31.80,9),('Paruh waktu','Perempuan',40.70,44.82,40.42,9),('Paruh waktu','Total',34.72,36.00,35.31,9)]
for ind,group,a,b,c,page in specs:
    for t,v in zip(['2024-02','2025-02','2026-02'],[a,b,c]):
        sulbar.append(dict(indikator=ind,kelompok=group,periode=t,nilai=v,satuan='persen',sumber='BPS_SULBAR_2026',halaman_pdf=page,catatan='NA berarti sampel tidak cukup; bukan nol' if v is None else 'Angka resmi; perubahan dihitung dari angka tampilan'))
sulbar.append(dict(indikator='TPT umur',kelompok='15–24 tahun',periode='2026-02',nilai=16.36,satuan='persen',sumber='BPS_SULBAR_2026',halaman_pdf=11,catatan='Narasi rilis; RSE kelompok umur tidak disertakan di ekstrak ini'))
write_csv(RAW/'transkripsi_sulbar_rincian.csv',sulbar)

annual=[13.83,9.05,10.69,8.98,9.27,8.98,9.71,11.29,7.38,5.01,3.22,8.35,7,5.56,6.56,6.66,2.80,13.94,11.44,8.39,5.97,7.39,5.66,4.71,7.77,8.04,7.93,7.94,6.82,11.33,11.49,10.56,9.74,7.49,8.63,6.45,16.89,5.37,7.91]
write_csv(RAW/'BPS_tabel_under_tahun_2025.csv',[dict(provinsi=p,tahun_label=2025,under_tabel=v,catatan='Tabel web berlabel tahun; seluruh angka sesuai turunan Agustus 2025 dalam toleransi 0,01 pp. Dipakai validasi, tidak digabung ke Februari.') for p,v in zip(PROVINCES,annual)])

sources=[
 dict(id='BPS_IPTK_2026',judul='Indikator Pasar Tenaga Kerja Indonesia Februari 2026',produsen='BPS',url=URL,tanggal_rilis='2026-06-26',cakupan='38 provinsi dan Indonesia; Feb 2025, Agu 2025, Feb 2026',status='Dipakai: sumber angka utama; PDF tersimpan',berkas='data/raw/'+SOURCE.name,catatan='KBLI berubah 2020 ke 2025; label Agustus 2024 di tabel jam kerja PDF 183 tidak konsisten dengan periode publikasi; dibaca sebagai Agustus 2025 berdasarkan seri dan tabel nasional 181.'),
 dict(id='BPS_SULBAR_2026',judul='Keadaan Ketenagakerjaan Sulawesi Barat Februari 2026',produsen='BPS Provinsi Sulawesi Barat',url=SULBAR,tanggal_rilis='2026-05-05',cakupan='Sulawesi Barat; Feb 2024–2026',status='Dipakai: angka resmi dan studi wilayah',berkas='data/raw/BPS_Sulbar_Februari_2026.pdf',catatan='Narasi penurunan under 0,80 pp; selisih angka tabel 14,15-13,36=0,79 pp. Narasi tidak dipakai untuk menghitung perubahan.'),
 dict(id='BPS_WEB_UNDER',judul='Tingkat Setengah Pengangguran Menurut Provinsi (Persen)',produsen='BPS',url='https://www.bps.go.id/id/statistics-table/2/MTE4MSMy/tingkat-setengah-pengangguran-menurut-provinsi--persen-.html',tanggal_rilis='2026-02-24 (pembaruan tabel)',cakupan='Tabel tahun 2025; 38 provinsi',status='Dipakai: validasi silang angka Agustus 2025',berkas='data/raw/BPS_tabel_under_tahun_2025.csv',catatan='Transkripsi tabel yang terlihat pada situs; tanggal pembaruan bukan periode observasi.'),
 dict(id='SDI_UNDER',judul='Tingkat Setengah Pengangguran Menurut Provinsi',produsen='BPS melalui Satu Data Indonesia',url='https://data.go.id/dataset/dataset/tingkat-setengah-pengangguran-menurut-provinsi',tanggal_rilis='2022-10-08; metadata dimodifikasi 2024-08-18',cakupan='Katalog tingkat provinsi; periode terkini belum terkonfirmasi',status='Metadata saja; berkas numerik tidak berhasil diakses',berkas='',catatan='Tombol unduh tidak menghasilkan berkas yang dapat diverifikasi; tidak mengklaim angka 2026 dari SDI.'),
 dict(id='SDI_TPT',judul='Tingkat Pengangguran Terbuka Menurut Provinsi',produsen='BPS melalui Satu Data Indonesia',url='https://data.go.id/dataset/dataset/tingkat-pengangguran-terbuka-menurut-provinsi',tanggal_rilis='Metadata 2024',cakupan='Sumber lama; tidak setara panel Feb 2026',status='Metadata saja; tidak digabung ke panel',berkas='',catatan='Katalog bukan sumber pengganti angka PDF 2026.'),
 dict(id='SDI_FORMAL',judul='Persentase Tenaga Kerja Formal Menurut Provinsi',produsen='BPS melalui Satu Data Indonesia',url='https://data.go.id/dataset/dataset/persentase-tenaga-kerja-formal-menurut-provinsi',tanggal_rilis='Metadata 2024',cakupan='Katalog provinsi',status='Metadata saja; tidak digabung ke panel',berkas='',catatan='Definisi dan periode perlu diperiksa sebelum penggabungan.'),
 dict(id='SDI_BONTANG',judul='Proporsi Penciptaan Lapangan Kerja Formal',produsen='Pemerintah Kota Bontang melalui SDI',url='https://data.go.id/dataset/dataset/proporsi-penciptaan-lapangan-kerja-formal',tanggal_rilis='Tidak dipakai',cakupan='Kota Bontang',status='Dikeluarkan: cakupan dan definisi berbeda',berkas='',catatan='Formal berbasis kontrak/jaminan sosial tidak setara definisi status pekerjaan BPS.'),
 dict(id='BPS_MEI_2026',judul='Keadaan Ketenagakerjaan Mei 2026',produsen='BPS',url='https://www.bps.go.id/id/pressrelease/2026/08/05/2606',tanggal_rilis='2026-08-05',cakupan='Konteks rilis nasional yang lebih baru',status='Dicatat sebagai batas kemutakhiran; tidak digabung',berkas='',catatan='Panel Februari dipilih karena seluruh variabel 38 provinsi tersedia bersama; bukan klaim data paling baru pada tanggal riset.'),
]
for s in sources:
    s['tanggal_akses']='2026-10-15'
    s['sha256']=hashlib.sha256((ROOT/s['berkas']).read_bytes()).hexdigest() if s['berkas'] else ''
write_csv(ROOT/'sources.csv',sources)
(ROOT/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Panel selesai: {len(rows)} baris, {len(next(iter(rows.values())))} kolom; {len(checks)} rekonsiliasi total lulus.')
