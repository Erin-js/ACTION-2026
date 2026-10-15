from pathlib import Path
import sys
import json
from collections import Counter
import numpy as np

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'plot_dependencies'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

obj=json.loads((ROOT/'data_provinsi.json').read_text(encoding='utf-8'))
ds=obj['data']; national=obj['national']; source=obj['source']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})

cols=[('tpt_2026','TPT\n(%)'),('informal_2026','Informal\n(%)'),('setengah_penganggur_perkiraan_2026','Setengah\npenganggur* (%)'),('tpak_perempuan_2026','TPAK\nperempuan (%)'),('tpt_pendidikan_tinggi_2026','TPT pendidikan\ntinggi (%)'),('jam_49plus_2026','Bekerja >=49\njam/minggu (%)')]
matrix=np.array([[d[k] for k,_ in cols] for d in ds])
normalized=(matrix-matrix.min(axis=0))/(matrix.max(axis=0)-matrix.min(axis=0))
fig,ax=plt.subplots(figsize=(12.3,16.3))
ax.imshow(normalized,aspect='auto',cmap='Blues',vmin=0,vmax=1)
ax.set_yticks(range(38),[d['provinsi'].replace('Nusa Tenggara','Nusa Tenggara') for d in ds],fontsize=10)
ax.set_xticks(range(len(cols)),[label for _,label in cols],fontsize=10)
ax.xaxis.tick_top();ax.tick_params(length=0,pad=8)
for i in range(38):
 for j in range(len(cols)):
  ax.text(j,i,f'{matrix[i,j]:.2f}'.replace('.',','),ha='center',va='center',fontsize=9.5,color='white' if normalized[i,j]>.65 else '#12304b')
ax.set_xticks(np.arange(-.5,6,1),minor=True);ax.set_yticks(np.arange(-.5,38,1),minor=True)
ax.grid(which='minor',color='white',linewidth=1.6);ax.tick_params(which='minor',length=0)
fig.suptitle('Peta perbandingan ketenagakerjaan 38 provinsi',x=.04,y=.985,ha='left',fontsize=18,fontweight='bold',color='#16364a')
fig.text(.04,.958,'Februari 2026 | Biru lebih gelap = nilai lebih besar dalam kolom yang sama.',fontsize=11,color='#405467')
fig.text(.04,.94,'Warna bukan skor kesejahteraan. Nilai besar tidak selalu berarti kondisi lebih buruk.',fontsize=10,color='#405467')
fig.text(.04,.028,'*Turunan persentase bekerja 1-34 jam dikurangi pekerja paruh waktu; pembulatan dapat berbeda sekitar 0,01 poin.',fontsize=9)
fig.text(.04,.013,'Sumber: BPS, Indikator Pasar Tenaga Kerja Indonesia Februari 2026, lampiran 7, 13, 15, 16, 17, dan 18.',fontsize=9)
fig.subplots_adjust(left=.27,right=.98,top=.9,bottom=.05)
fig.savefig(ROOT/'peta_indikator_38_provinsi.png',dpi=180)
plt.close(fig)

ordered=sorted(ds,key=lambda d:d['delta_penganggur'],reverse=True)
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(15,16),sharey=True,gridspec_kw={'width_ratios':[1.25,1]})
y=np.arange(38);v=np.array([d['delta_penganggur']/1000 for d in ordered])
ax1.barh(y,v,color=['#b8504d' if x>0 else '#2b7e87' for x in v],height=.66)
ax1.set_yticks(y,[d['provinsi'] for d in ordered],fontsize=10);ax1.invert_yaxis();ax1.axvline(0,color='#52616d',lw=.9)
ax1.set_xlim(-24,20);ax1.set_xlabel('Perubahan jumlah penganggur (ribu orang)')
ax1.set_title('Perubahan Februari 2025-Februari 2026',fontsize=12,pad=12)
for i,x in enumerate(v):ax1.text(x+(.4 if x>=0 else -.4),i,f'{x:+.2f}'.replace('.',','),ha='left' if x>=0 else 'right',va='center',fontsize=9)
tpt=np.array([d['tpt_2026'] for d in ordered]);low=np.array([d['tpt_2026_ci_lower'] for d in ordered]);high=np.array([d['tpt_2026_ci_upper'] for d in ordered])
ax2.errorbar(tpt,y,xerr=[tpt-low,high-tpt],fmt='o',color='#315e8b',ecolor='#afc3d4',capsize=2,markersize=4)
ax2.axvline(national['tpt_2026'],color='#b8504d',ls='--',lw=1.1,label='TPT nasional 4,68%')
ax2.set_xlim(0,10);ax2.set_xlabel('TPT Februari 2026 (%)');ax2.set_title('TPT dan selang kepercayaan 95%',fontsize=12,pad=12);ax2.legend(loc='lower right',fontsize=9)
for ax in [ax1,ax2]:ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
fig.suptitle('Jumlah penganggur dan tingkat pengangguran memberi informasi berbeda',x=.035,y=.975,ha='left',fontsize=16,fontweight='bold',color='#16364a')
fig.text(.035,.946,'Merah: jumlah penganggur bertambah. Toska: berkurang. Selang kepercayaan menunjukkan ketidakpastian TPT.',fontsize=10.5)
fig.text(.035,.015,'Sumber: BPS, lampiran 3, 8, 17, dan 44. Perubahan dihitung dari jumlah penduduk, bukan lowongan kerja.',fontsize=9)
fig.subplots_adjust(left=.18,right=.97,top=.92,bottom=.055,wspace=.22)
fig.savefig(ROOT/'dinamika_pengangguran_38_provinsi.png',dpi=180)
plt.close(fig)

def fmt(value,decimals=2):
 return f'{value:,.{decimals}f}'.replace(',','X').replace('.',',').replace('X','.')

def table(headers,rows):
 return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)+'\n'

headline='''# Analisis Ketenagakerjaan Seluruh 38 Provinsi

**Periode:** Februari 2025–Februari 2026. **Tanggal penelusuran:** 14 Oktober 2026.

Analisis ini menggunakan tabel nasional BPS agar cakupan wilayah, periode, dan definisi konsisten. Februari 2026 dipilih karena publikasi lengkap dengan indikator lintas provinsi dan tabel ketidakpastian berhasil diperoleh. Rilis nasional Mei 2026 tersedia, tetapi tidak dicampurkan ke dalam pemetaan tahunan ini. Semua 38 provinsi tercakup, termasuk enam provinsi di wilayah Papua; Indonesia merupakan baris pembanding nasional, bukan provinsi ke-39.

## 1. Temuan utama

1. **Perbaikan nasional belum merata.** Angkatan kerja bertambah 1.861.748 orang, sedangkan penduduk bekerja bertambah 1.896.450 orang. Jumlah penganggur nasional berkurang 34.702 orang. Namun, jumlah penganggur bertambah di 13 provinsi dan berkurang di 25 provinsi. Kenaikan pada 13 provinsi mencapai 46.609 orang, sedangkan pengurangan pada 25 provinsi mencapai 81.311 orang.
2. **TPT turun dapat disertai kenaikan jumlah penganggur.** Pola ini ditemukan di Riau, Kep. Bangka Belitung, Kepulauan Riau, Nusa Tenggara Timur, Sulawesi Selatan, dan Sulawesi Tenggara. Artinya, pemetaan berdasarkan perubahan TPT saja dapat melewatkan pertambahan orang yang menganggur.
3. **TPT rendah tidak cukup untuk menilai kecukupan pekerjaan.** Sebanyak 15 provinsi memiliki TPT di bawah nasional, tetapi proporsi pekerja informal di atas nasional. Ini tidak membuktikan pekerjaan tidak layak, tetapi menuntut pemeriksaan jam kerja, pendapatan, dan perlindungan kerja.
4. **Pendidikan dan gender menunjukkan pola yang berbeda antarwilayah.** TPT pendidikan tinggi melebihi TPT pendidikan menengah di 18 provinsi. TPAK perempuan di bawah 50% ditemukan di tujuh provinsi. Kedua pola belum menjelaskan penyebabnya.
5. **Perubahan jumlah bekerja tidak selalu positif ketika pengangguran turun.** Di delapan provinsi, angkatan kerja, penduduk bekerja, dan penganggur sama-sama berkurang. Penurunan pengangguran di kelompok ini tidak dapat dipresentasikan sebagai bukti pertumbuhan jumlah pekerjaan.

## 2. Sumber, ukuran, dan batas interpretasi

Sumber utama adalah [BPS, Indikator Pasar Tenaga Kerja Indonesia Februari 2026](SOURCE_URL), dirilis 26 Juni 2026, nomor publikasi 04100.26024. Nomor halaman di bawah merujuk halaman cetak; halaman PDF = halaman cetak + 28.

| Aspek | Ukuran yang digunakan | Sumber dan halaman cetak |
|---|---|---|
| Penyerapan dan pasokan tenaga kerja | Jumlah angkatan kerja dan penduduk bekerja; perubahan 2025–2026 | Lampiran 3, hlm. 136–137; lampiran 8, hlm. 142–143 |
| Pengangguran | Jumlah penganggur = angkatan kerja − bekerja; TPT total dan menurut gender | Lampiran 17, hlm. 157 |
| Partisipasi | TPAK total, laki-laki, perempuan; selisih gender | Lampiran 7, hlm. 141 |
| Penduduk bekerja terhadap usia kerja | EPR, bukan persentase bekerja terhadap angkatan kerja | Lampiran 9, hlm. 144 |
| Struktur pekerjaan | Formal/informal dan pekerja keluarga/tanpa dibayar | Lampiran 16, hlm. 156; lampiran 10, hlm. 146 |
| Jam kerja | Paruh waktu, bekerja 1–34 jam, dan bekerja 49 jam atau lebih | Lampiran 13, hlm. 152; lampiran 15, hlm. 154–155 |
| Pendidikan | TPT pendidikan dasar ke bawah, menengah, dan tinggi | Lampiran 18, hlm. 158 |
| Upah | Rata-rata upah buruh/karyawan/pegawai, bukan seluruh penduduk bekerja | Lampiran 24, hlm. 164 |
| Ketidakpastian | RSE dan selang kepercayaan 95% TPT | Lampiran 44, hlm. 183 |

**Selisih penyerapan = perubahan penduduk bekerja − perubahan angkatan kerja.** Secara identitas, nilainya sama dengan negatif perubahan jumlah penganggur. Karena itu, selisih tersebut bukan indikator independen tambahan dan bukan bukti penyebab pengangguran. Nilai positif berarti jumlah penganggur turun, tetapi perlu dibaca bersama arah perubahan angkatan kerja dan penduduk bekerja.

**Setengah pengangguran dalam tabel ini merupakan angka turunan:** persentase bekerja 1–34 jam dikurangi tingkat pekerja paruh waktu. Penduduk bekerja kurang dari 35 jam terdiri atas setengah penganggur dan pekerja paruh waktu. Semua kolom ini diberi penanda “perkiraan” pada CSV. Pembulatan kedua masukan dapat menimbulkan perbedaan sekitar 0,01 poin persentase dari angka resmi yang dihitung sebelum pembulatan. Contoh nasional: turunan 7,26%, sedangkan angka resmi nasional 7,27%. Angka tersebut tidak menggantikan angka resmi apabila tersedia untuk pendalaman provinsi.

TPT berpenyebut angkatan kerja. Formal/informal, paruh waktu, setengah pengangguran, pekerja keluarga, dan jam kerja berlebih berpenyebut penduduk bekerja. TPAK berpenyebut penduduk usia kerja. TPT pendidikan tinggi berpenyebut angkatan kerja berpendidikan tinggi, bukan seluruh lulusan pendidikan tinggi atau seluruh penganggur.

## 3. Dinamika angkatan kerja, bekerja, dan penganggur

Empat pola deskriptif ditemukan:

| Pola Februari 2025–2026 | Jumlah provinsi | Makna terbatas |
|---|---:|---|
| Angkatan kerja dan bekerja naik; penganggur turun | 17 | Pertambahan bekerja melampaui pertambahan angkatan kerja. |
| Angkatan kerja dan bekerja naik; penganggur naik | 11 | Pertambahan bekerja belum mengimbangi tambahan angkatan kerja. |
| Angkatan kerja dan bekerja turun; penganggur naik | 2 | Jumlah bekerja turun lebih besar; terjadi di Aceh dan Papua Selatan. |
| Angkatan kerja dan bekerja turun; penganggur turun | 8 | Pengurangan penganggur disertai menyusutnya angkatan kerja dan jumlah bekerja. |

Pada kelompok terakhir, penyebab keluar dari angkatan kerja belum diketahui. Jangan otomatis menyebutnya putus asa mencari pekerjaan, migrasi, atau pensiun tanpa data pendukung.

### Tabel seluruh provinsi: perubahan jumlah dan TPT

Satuan perubahan jumlah adalah **orang**, bukan lowongan. Δ berarti Februari 2026 dikurangi Februari 2025. Penganggur dihitung dari jumlah angkatan kerja dan penduduk bekerja. Nilai jumlah dipertahankan sesuai estimasi BPS; perubahan kecil belum tentu signifikan secara statistik.

TABLE_DYNAMICS

![Perubahan pengangguran dan ketidakpastian TPT](dinamika_pengangguran_38_provinsi.png)

**Kalimantan Barat** memiliki kenaikan jumlah penganggur terbesar secara absolut, 15.797 orang. Angkatan kerja bertambah 131.638 orang, sedangkan penduduk bekerja bertambah 115.841 orang. TPT naik dari 4,23% menjadi 4,57%. Ini kandidat untuk menelusuri mengapa pertumbuhan jumlah bekerja belum mengimbangi tambahan angkatan kerja, bukan bukti bahwa suatu sektor atau kelompok tertentu menjadi penyebabnya.

**Aceh** memiliki pola berbeda: jumlah angkatan kerja turun 47.911 dan penduduk bekerja turun 55.341; penganggur bertambah 7.430. TPAK turun 2,19 poin. Karena pasokan yang aktif juga menyusut, masalahnya tidak tepat diringkas sebagai “terlalu banyak lulusan baru”.

**Jawa Barat** mencatat pengurangan jumlah penganggur terbesar secara absolut, 20.786 orang. Namun, jumlah penganggur yang tersisa masih 1.786.425 orang dan TPT 6,64%. Besarnya penurunan dan besarnya beban pengangguran saat ini merupakan informasi yang berbeda. Lima provinsi dengan jumlah penganggur terbanyak—Jawa Barat, Jawa Tengah, Jawa Timur, Banten, dan Sumatera Utara—menampung sekitar 61,35% penganggur nasional. Ini ukuran konsentrasi jumlah, bukan ukuran risiko individual.

## 4. Struktur pekerjaan dan jam kerja

### Tabel seluruh provinsi: informalitas, kecukupan jam, dan jam panjang

Semua angka adalah persentase penduduk bekerja pada Februari 2026. Setengah penganggur bertanda * merupakan turunan dari dua persentase yang dibulatkan. Pekerja paruh waktu tidak otomatis kekurangan pekerjaan karena mereka tidak mencari/tidak bersedia menerima tambahan pekerjaan menurut definisi yang digunakan.

TABLE_QUALITY

**Sulawesi Barat** menonjol: TPT 2,93%, informal 71,77%, dan setengah pengangguran sekitar 13,35%. Dibanding TPT nasional 4,68%, angka pengangguran terbukanya rendah, tetapi kecukupan jam kerja masih perlu diperiksa. Arah analisis yang relevan adalah apakah masyarakat sudah bekerja namun belum memperoleh jam kerja yang diinginkan.

**Nusa Tenggara Timur** memiliki TPT 3,16%, informal 75,28%, pekerja keluarga/tanpa dibayar 26,20%, dan setengah pengangguran sekitar 9,29%. Ini alasan untuk membaca pengangguran bersama struktur pekerjaan, tanpa menyatakan semua pekerja informal atau keluarga hidup tidak sejahtera.

**Papua Pegunungan** memiliki TPT 1,70%, informal 95,37%, dan pekerja keluarga/tanpa dibayar 53,33%. Rendahnya pengangguran terbuka tidak dapat langsung dipakai sebagai bukti melimpahnya pekerjaan bergaji. Namun, indikator ini juga belum mengukur pendapatan usaha atau kesejahteraan rumah tangga secara keseluruhan.

**Kalimantan Timur** memiliki proporsi bekerja 49 jam atau lebih sebesar 34,13%, terbesar secara deskriptif di tabel ini. Jam panjang tidak otomatis membuktikan pelanggaran aturan kerja karena ukuran mencakup seluruh pekerjaan dan beragam status pekerja. Perlu pendalaman status pekerjaan, upah, dan jumlah pekerjaan sebelum menilai beban kerja serta kompensasinya.

![Peta perbandingan indikator seluruh provinsi](peta_indikator_38_provinsi.png)

## 5. Gender, pendidikan, dan upah

### Tabel seluruh provinsi: partisipasi, pendidikan tinggi, dan upah buruh

Gap TPAK adalah TPAK laki-laki dikurangi perempuan, dalam poin persentase. Upah merupakan rata-rata nominal bulanan buruh/karyawan/pegawai. Angka upah tidak dapat langsung dibandingkan sebagai ukuran daya beli karena biaya hidup, komposisi pekerjaan, dan jam kerja berbeda.

TABLE_ACCESS

**Jambi** memiliki gap TPAK gender terbesar, 39,60 poin: laki-laki 85,21%, perempuan 45,61%. Tujuh provinsi memiliki TPAK perempuan di bawah 50%: Aceh, Riau, Jambi, Kepulauan Riau, Banten, Kalimantan Timur, dan Sulawesi Utara. Rendahnya partisipasi tidak otomatis membuktikan diskriminasi atau kekurangan lowongan; dapat terkait pendidikan, tanggung jawab rumah tangga, preferensi, dan hambatan lain yang belum diuji.

**Pendidikan tinggi:** Sulawesi Utara (9,08%), Maluku (9,02%), Papua Barat Daya (8,97%), Sumatera Barat (8,77%), dan Sulawesi Selatan (8,74%) memiliki estimasi TPT pendidikan tinggi terbesar. Di 18 provinsi, TPT pendidikan tinggi lebih besar daripada pendidikan menengah. Temuan ini belum mengukur kemampuan coding, Excel, atau kebutuhan jurusan tertentu. Pengelompokan publikasi mengacu ISCED-97 yang disesuaikan: menengah mencakup SMA/MA, SMK, dan Paket C; tinggi mencakup Diploma I/II/III, Diploma IV/S1, serta S2/S3 (penjelasan hlm. cetak 123). Perbedaan usia, masa transisi setelah lulus, dan preferensi pekerjaan perlu dipertimbangkan.

**Upah:** rata-rata nominal buruh tertinggi ditemukan di DKI Jakarta, Rp5.229.472 per bulan, dan terendah di Jawa Tengah, Rp2.462.759. Papua Tengah memiliki rata-rata Rp5.091.978 meskipun informalitas 86,16%. Tidak ada kontradiksi: rata-rata tersebut hanya menggambarkan buruh/karyawan/pegawai, bukan semua penduduk bekerja. Menggunakan angka itu sebagai gambaran pendapatan seluruh pekerja Papua Tengah akan keliru.

## 6. Kandidat pendalaman berdasarkan bukti

Tiga arah berikut belum merupakan keputusan konsep infografis. Pemilihannya berasal dari pola yang berbeda dan dapat dipertajam bersama pengguna.

| Arah pertanyaan | Kandidat wilayah | Dasar pemilihan | Data lanjutan yang diperlukan |
|---|---|---|---|
| Mengapa pertumbuhan jumlah bekerja belum mengimbangi tambahan angkatan kerja? | Kalimantan Barat; Sulawesi Selatan sebagai pembanding | Penganggur bertambah 15.797 dan 8.322 orang ketika jumlah bekerja dan angkatan kerja sama-sama naik. | Perubahan lapangan usaha, status pekerjaan, pendidikan dan usia angkatan kerja; beberapa tahun pengamatan. |
| Apakah TPT rendah disertai kecukupan pekerjaan? | Sulawesi Barat dan Nusa Tenggara Timur | TPT rendah, informalitas tinggi, dan setengah pengangguran di atas angka nasional. | Upah/pendapatan menurut status kerja, sektor, kebutuhan tambahan jam, serta indikator kesejahteraan yang sepadan. |
| Siapa yang masih menghadapi hambatan meskipun indikator agregat membaik? | Sulawesi Utara atau Sumatera Barat untuk pendidikan; Jambi untuk partisipasi perempuan | TPT pendidikan tinggi relatif tinggi atau gap partisipasi gender besar. | Karakteristik umur, durasi mencari pekerjaan, bidang studi jika tersedia, dan alasan tidak aktif secara ekonomi. |

Aceh tetap layak menjadi kandidat terpisah apabila fokus bergeser pada penurunan jumlah bekerja dan partisipasi perempuan. Jangan menggabungkan semua kandidat ke dalam satu poster tanpa pertanyaan utama yang jelas.

## 7. Keterbatasan dan langkah validasi

- Data merupakan estimasi survei. Peringkat berdasarkan angka titik tidak membuktikan perbedaan signifikan. Contohnya, TPT Papua 7,02% memiliki CI 95% 5,06–8,98%; Kepulauan Riau 6,87% memiliki CI 4,79–8,94%. Selang yang lebar membuat klaim “provinsi pertama pasti lebih buruk” tidak tepat.
- Kenaikan/penurunan tahunan belum diuji signifikansinya. CI TPT satu tahun tidak cukup untuk menguji perubahan tahunan; diperlukan varians perubahan dan, jika relevan, kovarians antarperiode.
- Selisih penyerapan merupakan perubahan bersih, bukan jumlah lowongan, rekrutmen, PHK, atau penempatan lulusan baru. Provinsi penduduk juga tidak otomatis menunjukkan lokasi perusahaan tempat mereka bekerja, terutama bila ada komuter.
- Setengah pengangguran adalah turunan dengan potensi selisih pembulatan; verifikasi angka resmi wilayah terpilih sebelum digunakan pada karya akhir.
- Informalitas, pekerja keluarga, jam panjang, dan upah rata-rata merupakan indikator terpisah. Tidak dibuat skor gabungan “provinsi terburuk” karena pembobotan dan maknanya belum disepakati.
- Data tidak membuktikan penyebab: ketidakcocokan keterampilan, syarat usia/penampilan, kualitas jurusan, atau eksploitasi kerja belum diukur langsung.
- Sektor ekonomi dan pengangguran usia muda belum dimasukkan sebagai tabel lengkap lintas provinsi dalam tahap ini. Keduanya dapat digunakan untuk pendalaman wilayah, dengan sumber serta periode yang sepadan.

**Validasi berikutnya:** pilih pertanyaan dan 2–3 wilayah kandidat, periksa konsistensi selama beberapa tahun dengan bulan sama, konfirmasi angka turunan pada BRS daerah, lalu telusuri komposisi sektor, umur, dan pendidikan. Rekomendasi tindakan disusun setelah pola tersebut memperoleh dukungan bukti, bukan dari peringkat satu tahun saja.

## 8. Berkas dan pemeriksaan data

- `data_38_provinsi_feb2025_feb2026.csv`: 38 baris provinsi dan satu baris nasional; mencakup nilai sumber serta hasil perhitungan.
- `data_provinsi.json`: data yang sama beserta lokasi halaman sumber untuk setiap indikator masukan.
- `Indikator_Pasar_Tenaga_Kerja_Februari_2026_BPS.pdf`: publikasi resmi yang diunduh dari BPS.
- `peta_indikator_38_provinsi.png` dan `dinamika_pengangguran_38_provinsi.png`: visual eksplorasi data.

Pemeriksaan yang dilakukan: cakupan 38 provinsi, kesesuaian nama wilayah, identitas penduduk usia kerja = angkatan kerja + bukan angkatan kerja, penganggur = angkatan kerja − bekerja, kecocokan TPT hasil perhitungan terhadap angka publikasi, formal + informal = 100%, serta penjumlahan provinsi terhadap total nasional untuk jumlah penduduk dan pekerja paruh waktu. Tabel formal/informal dan ketidakpastian TPT juga diperiksa secara visual pada PDF sumber.
'''

rows1=[];rows2=[];rows3=[]
for d in ds+[national]:
 rows1.append([d['provinsi'],fmt(d['delta_angkatan_kerja'],0),fmt(d['delta_bekerja'],0),fmt(d['delta_penganggur'],0),fmt(d['tpt_2025']),fmt(d['tpt_2026']),fmt(d['delta_tpt_pp']),fmt(d['delta_tpak_pp'])])
 rows2.append([d['provinsi'],fmt(d['informal_2026']),fmt(d['pekerja_keluarga_2026']),fmt(d['paruh_waktu_persen_2026']),fmt(d['setengah_penganggur_perkiraan_2026'])+'*',fmt(d['jam_49plus_2026'])])
 rows3.append([d['provinsi'],fmt(d['tpak_2026']),fmt(d['tpak_perempuan_2026']),fmt(d['gap_tpak_gender_pp']),fmt(d['tpt_pendidikan_tinggi_2026']),fmt(d['upah_buruh_2026_rupiah'],0)])

report=headline.replace('SOURCE_URL',source).replace('TABLE_DYNAMICS',table(['Provinsi','Δ angkatan kerja','Δ bekerja','Δ penganggur','TPT 2025 (%)','TPT 2026 (%)','Δ TPT (pp)','Δ TPAK (pp)'],rows1)).replace('TABLE_QUALITY',table(['Provinsi','Informal (%)','Pekerja keluarga (%)','Paruh waktu (%)','Setengah penganggur* (%)','>=49 jam (%)'],rows2)).replace('TABLE_ACCESS',table(['Provinsi','TPAK total (%)','TPAK perempuan (%)','Gap TPAK (pp)','TPT pendidikan tinggi (%)','Upah buruh (Rp)'],rows3))
(ROOT/'analisis_38_provinsi.md').write_text(report,encoding='utf-8')
print('Created report and two figures.')
