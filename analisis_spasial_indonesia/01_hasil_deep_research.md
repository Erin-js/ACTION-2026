# Riset nasional: kapan penurunan partisipasi kerja perempuan menjadi urgensi?

Tanggal riset: **24 Oktober 2026**, Asia/Jakarta. Cakupan: Indonesia; penyaringan 38 provinsi dan kebutuhan pendalaman kabupaten/kota. Angka awal, sumber data, bukti penelitian, dan rancangan analisis dibedakan di bawah.

## 1. Jawaban utama

Data yang paling menentukan adalah **keinginan bekerja yang belum terpenuhi**, bukan besarnya kesenjangan TPAK saja. Urgensi lebih kuat apabila perempuan menyatakan ingin bekerja, mengalami hambatan yang dapat diidentifikasi, dan menghadapi keterbatasan ekonomi atau kehilangan pilihan pekerjaan. Tingkat partisipasi yang rendah tanpa informasi tersebut belum membedakan pilihan pribadi, sekolah, kesehatan, komposisi umur, dan hambatan akses.

Rangkaian bukti yang dicari:

1. **Gejala:** partisipasi dan proporsi bekerja menurun, atau perbedaannya antarkelompok melebar.
2. **Kebutuhan:** ada perempuan tidak bekerja yang ingin memperoleh pekerjaan.
3. **Hambatan:** alasan tidak mencari, tidak siap bekerja, atau berhenti bekerja dapat dikenali.
4. **Konsekuensi:** kebutuhan ekonomi tidak terpenuhi atau kondisi pekerjaan/penghasilan memburuk.
5. **Lokasi dan tindakan:** kebutuhan terkonsentrasi di wilayah tertentu dan dapat dihubungkan dengan dukungan yang relevan.

Tidak semua lapisan harus menunjukkan arah yang sama. Penurunan TPAK karena peningkatan sekolah merupakan penjelasan alternatif yang perlu diperiksa, bukan dipaksa menjadi hambatan kerja. Hasil yang tidak mendukung dugaan awal tetap dicatat.

## 2. Apa yang sudah tersedia sebagai data numerik?

| Berkas dalam `data/processed/` | Cakupan | Kegunaan dan batas |
|---|---|---|
| `panel_gender_38_provinsi_3_periode.csv` | 117 baris: 38 provinsi dan Indonesia, Februari 2025, Agustus 2025, Februari 2026 | PUK, AK, bekerja, penganggur, BAK, TPAK, TPT, EPR dan upah menurut gender. Disalin dari panel riset lokal terdahulu, rasio dihitung ulang; bukan pengumpulan mikrodata baru. |
| `screening_perubahan_provinsi_feb2025_feb2026.csv` | 38 provinsi dan nasional | Penyaringan perubahan tahunan. Belum mengukur hambatan atau signifikansi survei. |
| `kemiskinan_514_kabupaten_kota_2025.csv` | 514 kabupaten/kota | P0, P1, P2, jumlah penduduk miskin dan garis kemiskinan; tidak khusus perempuan. Kode kabupaten belum dipadankan. |
| `kemiskinan_agregat_provinsi_2025.csv` | 38 provinsi | Agregat resmi dari tabel yang sama; tidak dihitung dengan merata-ratakan P0 kabupaten. |
| `internet_gender_desa_kota_provinsi_maret2025.csv` | 117 baris: 39 wilayah × 3 klasifikasi daerah | Internet menurut gender, penduduk umur 5+, Susenas Maret 2025. DKI perdesaan tidak tersedia dan tidak diubah menjadi nol. |
| `status_perkawinan_gender_15_49_provinsi_maret2025.csv` | 78 baris: 39 wilayah × 2 gender | Distribusi status perkawinan penduduk 15–49; bukan TPAK perempuan menikah. |
| `internet_gender_provinsi_2021_2024.csv` | 304 kombinasi wilayah, gender dan tahun | Seri lampiran telekomunikasi; sebagian Papua lama kosong. Penyebut berbeda dari tabel internet 5+; jangan digabung menjadi seri yang sama tanpa audit. |
| `panel_konteks_38_provinsi_2025.csv` | 38 provinsi, kode BPS provinsi | TPAK/EPR/TPT Agustus 2025, internet dan perkawinan Maret 2025, serta kemiskinan 2025. Hubungan wilayah, bukan hubungan individu. |
| `kamus_variabel_sakernas_agustus2025.csv` | 290 variabel pada katalog | Dokumentasi untuk merancang permintaan data; tidak memuat 290 variabel observasi individu. |

Sumber ketenagakerjaan: [BPS IPTK Februari 2026](https://www.bps.go.id/id/publication/2026/06/26/f00a5821056e518c20d1546e/indikator-pasar-tenaga-kerja-indonesia-februari-2026.html), lampiran 7, halaman PDF 169/cetak 141. Sumber pendukung: [Statistik Kesejahteraan Rakyat 2025](https://www.bps.go.id/id/publication/2025/10/10/b37dd4fb6b1727f8cf3c0271/statistik-kesejahteraan-rakyat-2025.html), tabel 2.7 dan 7.4, serta [Kemiskinan Kabupaten/Kota 2025](https://www.bps.go.id/id/publication/2025/11/28/f7534097ff9c717e794cd6e1/data-dan-informasi-kemiskinan-kabupaten-kota-tahun-2025.html), tabel 2.1.

### Temuan penyaringan awal

Perhitungan dari panel yang tersedia menunjukkan TPAK perempuan nasional **56,70% pada Februari 2025 menjadi 56,41% pada Februari 2026**, turun sekitar **0,29 poin persentase**. Dengan toleransi pembulatan 0,02 poin, **24 provinsi** mengalami penurunan TPAK perempuan; **16 provinsi** mengalami penurunan TPT dan TPAK perempuan bersamaan. Ini hitungan deskriptif, bukan jumlah wilayah yang sudah terbukti mengalami hambatan kerja atau perubahan signifikan.

Jambi berada di antara wilayah yang perlu ditelusuri, tetapi pemilihan studi kasus tidak ditetapkan hanya dari besar penurunan. Semua provinsi tetap masuk penyaringan agar riset tidak hanya mencari bukti untuk wilayah yang sudah dipilih.

### Batas kemutakhiran

[Statistik Kesejahteraan Rakyat 2026](https://www.bps.go.id/id/publication/2026/10/05/7e415878a8af3678e51f3e0a/statistik-kesejahteraan-rakyat-2026.html), berbasis Susenas Maret 2026, sudah ditemukan. Edisi ini dicatat sebagai pembaruan; nilai tabelnya belum dimasukkan ke panel olahan. Paket konteks awal memakai 2025 karena sejumlah sumber dapat disejajarkan pada tahun itu. Ini bukan klaim bahwa semua berkas 2025 adalah edisi terbaru.

## 3. Kelompok data dan aspek yang perlu diteliti

### A. Keinginan bekerja: bukti langsung yang paling penting

**Sumber utama:** [katalog mikrodata Sakernas Agustus 2025](https://silastik.bps.go.id/v3/index.php/mikrodata/view/ZmpnL2FkNDBLZkJqVTZmUERWbXFZdz09) dan [dokumentasi resmi](https://drive.bps.go.id/s/WE3A734gea2sa3d). Kuesioner lokal halaman 23 memuat `SRH_DES` (keinginan), `SRH_DWY` (alasan tidak mencari), `SRH_AVN/AVL` (kesiapan) dan `SRH_NAR` (alasan belum siap). `SRH_MAC` menanyakan kegiatan utama kepada kelompok yang menyatakan tidak menginginkan pekerjaan.

Kebutuhan analisis: jumlah dan persentase perempuan di luar angkatan kerja yang ingin bekerja; kesiapan; alasan pasar kerja, rumah tangga, pendidikan dan kesehatan. Sajikan dua penyebut: seluruh perempuan BAK, serta seluruh perempuan usia kerja. Penyebut pertama menunjukkan komposisi BAK, penyebut kedua menunjukkan besarnya kebutuhan dalam populasi.

**Status:** instrumen dan kamus sudah diperoleh; tabulasi nasional per wilayah dan mikrodata penuh belum diperoleh. Jangan menganggap pertanyaan keinginan ditanyakan kepada semua orang atau mengubah jawaban kosong karena alur lompat menjadi “tidak ingin”. Status BAK harus diturunkan dengan konsep BPS yang konsisten terlebih dahulu.

### B. Ekonomi dan kerentanan rumah tangga

Cari P0/P1/P2, pengeluaran per kapita, pangsa pengeluaran makanan, kelompok pengeluaran, bantuan sosial, jumlah tanggungan, dan jumlah pencari nafkah. Data kemiskinan kabupaten sudah diekstrak. Pengeluaran berasal Susenas modul KP, berbeda dari KOR. [Publikasi konsumsi Maret 2025](https://www.bps.go.id/id/publication/2025/10/10/755ea866289ba29e5104e58d/pengeluaran-untuk-konsumsi-penduduk-indonesia-maret-2025.html) merupakan rute tambahan.

**Pola yang dicari:** kebutuhan bekerja tinggi beriringan dengan kerentanan ekonomi tinggi. **Batas:** kemiskinan wilayah tidak membuktikan perempuan yang ingin bekerja berasal dari rumah tangga miskin. Sakernas dan Susenas tidak boleh dicocokkan seolah-olah respondennya sama. Untuk bukti individual, dibutuhkan satu sumber yang benar-benar mengukur kedua keadaan, tabulasi resmi yang sesuai, atau survei lanjutan.

### C. Status perkawinan dan riwayat keluarga

Sakernas memiliki `DEM_MRT`; Susenas menyediakan distribusi status perkawinan. Data Susenas 15–49 menurut gender sudah tersedia dalam paket ini. Analisis lanjutan sebaiknya membandingkan TPAK/EPR serta keinginan bekerja menurut status perkawinan pada kelompok umur dan pendidikan yang sebanding.

**Batas:** persentase menikah bukan tingkat perkawinan baru. Data satu waktu tidak menunjukkan urutan “kesulitan ekonomi → menikah → berhenti bekerja”. Untuk urutan tersebut diperlukan waktu perkawinan, waktu berhenti, keadaan ekonomi sebelum peristiwa, dan pengamatan individu yang sesuai. Status menikah tidak otomatis berarti mempunyai anak atau mengalami hambatan.

### D. Umur dan perubahan komposisi

Gunakan `DEM_AGE`, struktur perempuan usia kerja, status sekolah dan kelompok usia yang konsisten. Pisahkan 15–24, usia utama bekerja seperti 25–54, dan usia lebih tua; rinci lima tahunan bila sampel memadai. Periksa apakah perubahan TPAK total bertahan setelah struktur umur disamakan.

**Batas:** peningkatan jumlah pelajar atau penduduk usia lanjut dapat mengubah TPAK tanpa membuktikan akses kerja memburuk. Usia 25–54 tidak sama dengan 15–49 pada tabel perkawinan. Jangan mengganti penyebut hanya karena tabel yang tersedia berbeda.

### E. Pendidikan dan transisi sekolah–kerja

Cari partisipasi sekolah, pendidikan tertinggi, keikutsertaan pelatihan, pengalaman kerja dan kebutuhan bekerja menurut pendidikan. Rute utamanya Sakernas (`DEM_EDL`, `DEM_SKLH`), [Statistik Pendidikan 2025](https://www.bps.go.id/id/publication/2025/11/21/d048070f37740b0e04d99350/statistics-of-education-2025.html), serta Statistik Pemuda.

**Pola yang dicari:** partisipasi turun karena masih sekolah, atau lulusan yang sudah tidak sekolah ingin bekerja namun belum memperoleh pekerjaan. **Batas:** pendidikan rendah bukan bukti ketidakcakapan. NEET tidak identik dengan pengangguran; batas usia indikator juga harus diperiksa. Jangan menyatukan lulusan baru dan perempuan yang kembali bekerja menjadi sasaran program tanpa pemisahan kebutuhan.

### F. Pengasuhan dan tanggung jawab keluarga

Cari keberadaan/umur anak, anggota yang membutuhkan perawatan, pembagian pengasuhan, biaya, waktu, ketersediaan TPA, kapasitas dan jam layanan. Roster Susenas, Podes, direktori satuan PAUD/TPA dan survei khusus menjadi rute data. Sakernas memuat alasan rumah tangga, tetapi alasan tersebut belum mengukur seluruh beban pengasuhan.

[Laporan Bank Dunia tentang ekonomi perawatan](https://openknowledge.worldbank.org/bitstreams/def01f54-3416-4d85-b57a-4746be7a988d/download) memakai survei 2023 terhadap 3.000 rumah tangga beranak usia 0–6 di 52 kabupaten. Laporan itu mendukung relevansi keterjangkauan dan dukungan pengasuhan terhadap pekerjaan. **Batas:** bukan data tahunan setiap kabupaten atau seluruh perempuan. PAUD tidak otomatis layanan penitipan seharian; jumlah peserta bukan kapasitas yang masih tersedia.

### G. Akses digital

Bedakan penggunaan internet individu, penggunaan perangkat, literasi, dan konektivitas desa. Internet gender 5+ Maret 2025 sudah tersedia. Sakernas juga memiliki `TIK_A/B/C/D`; Podes memiliki `R1005C/D` untuk sinyal.

**Pola yang dicari:** kebutuhan bekerja belum terpenuhi dan akses informasi/layanan daring terbatas. **Batas:** akses internet tidak membuktikan kemampuan melamar atau bekerja daring. Sinyal desa tidak menjamin kepemilikan perangkat, kuota, penggunaan perempuan atau mutu koneksi. Data digital mendukung desain layanan daring/luring, bukan otomatis membuktikan penyebab penurunan TPAK.

### H. Transportasi dan keterjangkauan lokasi kerja

Podes mencakup keberadaan, operasional dan jam angkutan umum (`R1001C1/C2/C3`); ukuran akses dari kantor desa terdapat pada kelompok `R1002`. Sakernas modul MJU memuat perjalanan dan lokasi kerja pada kelompok yang bekerja.

**Pola yang dicari:** kebutuhan bekerja tinggi pada wilayah dengan layanan transportasi terbatas. **Batas:** perjalanan pekerja tidak mewakili perempuan yang tidak bekerja. Jarak kantor desa-ke-kecamatan bukan jarak rumah-ke-lowongan. Data jalan tidak langsung mengukur tarif, keamanan atau kesesuaian jadwal perjalanan. Untuk mekanisme tersebut dibutuhkan lokasi fasilitas/pekerjaan serta survei perjalanan yang relevan.

### I. Akses pekerjaan dan permintaan tenaga kerja

[Pasker ID](https://paskerid.kemnaker.go.id/informasi-pasar-kerja) menampilkan lowongan, kebutuhan tenaga kerja, jabatan dan wilayah. Katalog Satu Data Kemnaker juga mengidentifikasi berkas Karirhub. Cari persyaratan pendidikan/pengalaman, upah, lokasi, jam dan mekanisme seleksi bila tersedia.

**Batas:** posting lowongan, kuota orang dan posisi terisi berbeda. Data administratif tidak mencakup semua kesempatan kerja dan dapat condong ke wilayah/perusahaan yang aktif daring. Belum ada ekspor nasional lowongan dalam paket ini. Jumlah pendaftar layanan tidak sama dengan jumlah penganggur atau seluruh kebutuhan bekerja.

### J. Struktur ekonomi dan kualitas pekerjaan

Cari sektor menurut gender, status pekerjaan, pekerja keluarga/tidak dibayar, formalitas, jam, setengah pengangguran, upah buruh, perlindungan sosial dan kontrak. Bandingkan wilayah dengan struktur ekonomi yang mirip, lalu periksa perbedaannya.

**Batas:** TPAK tinggi dapat berjalan bersama pekerjaan yang belum memadai. Informalitas sendiri bukan vonis kesejahteraan. Upah buruh tidak mewakili seluruh pekerja. Perubahan KBLI dan konsep formalitas harus diperiksa sebelum menggabungkan tahun. Jangan membuat skor “wilayah terburuk” dari indikator berbeda tanpa dasar pembobotan dan validasi.

### K. Riwayat berhenti dan kembali bekerja

Kuesioner Sakernas halaman 24 memuat `MPK_PERNAH`, `MPK_HENTI`, waktu berhenti dan `MPK_ALSN`. Ini lebih tepat untuk menelusuri sasaran kembali bekerja daripada menganggap seluruh perempuan BAK pernah bekerja.

[Working paper Cameron dkk. (2023)](https://docs.iza.org/dp16136.pdf) memakai riwayat lebih dari 9.000 perempuan dalam IFLS untuk meneliti perkawinan, kelahiran dan pekerjaan. **Batas:** penelitian historis dengan cakupan IFLS; bukan bukti sebab perubahan provinsi 2026. Riwayat berhenti dalam satu tahun pada Sakernas tetap perlu dibedakan dari panel individu penuh.

### L. Kesehatan, disabilitas dan kebutuhan perawatan

Gunakan kesulitan fungsional Sakernas, kondisi kesehatan/akses layanan Susenas, dan keberadaan anggota rumah tangga yang membutuhkan perawatan. Aspek ini dapat menjelaskan keterbatasan kesiapan bekerja atau kebutuhan akomodasi.

**Batas:** jangan menganggap semua orang dengan disabilitas tidak mampu atau tidak ingin bekerja. Kesulitan responden sendiri berbeda dari tanggung jawab merawat anggota keluarga. Hasil perlu diurai, bukan digabung menjadi kategori “tidak produktif”.

### M. Norma sosial, izin keluarga dan keamanan

Norma tentang peran rumah tangga dan kondisi kerja dapat ditelusuri melalui survei khusus atau wawancara; laporan ekonomi perawatan memberi dasar pertanyaannya. Sakernas juga memiliki label kondisi keselamatan/ancaman di tempat kerja dalam katalog.

**Status:** belum ditemukan tabel publik tahunan lengkap 514 kabupaten untuk norma dan izin keluarga. Tidak tersedia dalam panel awal. Jangan menebak norma dari agama, etnis, persentase menikah atau rendahnya TPAK. Data kekerasan tercatat pun perlu memperhitungkan perbedaan pelaporan dan akses layanan.

### N. Geometri, kode wilayah dan mutu estimasi

Data spasial membutuhkan polygon, kode wilayah, tahun batas, serta daftar wilayah yang cocok dengan data statistik. [SIG BPS](https://sig.bps.go.id/bridging-kode/index) menyediakan relasi kode dan histori. Layanan BIG membedakan layer garis dan area: layer 9 bertipe garis, sedangkan layer 13 diidentifikasi sebagai area kabupaten/kota pada daftar layanan.

**Status:** polygon belum berhasil diperoleh karena query layanan mengalami timeout. Resource ZIP alternatif dari SDI/Kemendagri berhasil diunduh, tetapi audit header menunjukkan **Polyline dengan 1.298 segmen**, sehingga tidak digunakan sebagai polygon kabupaten. Kode kabupaten pada tabel kemiskinan belum dipadankan. Data siap untuk penyiapan join, belum merupakan paket GIS yang sudah lengkap. Kode kecamatan/desa Sakernas 2025 tercantum dalam daftar variabel yang tidak didiseminasikan, sehingga hasil survei tidak boleh dipaksakan menjadi peta desa.

## 4. Apa yang sudah mendukung urgensi, dan apa yang belum?

**Bukti langsung yang penting:** laporan ekonomi perawatan Bank Dunia, halaman cetak 60/PDF 84, menyebut bahwa dari **1.706 ibu yang tidak bekerja atau tidak mencari pekerjaan**, **32% menyatakan ingin bekerja purna waktu jika pengasuhan anak tersedia**. Ini menunjukkan adanya kebutuhan bekerja yang bergantung pada dukungan pengasuhan dalam populasi studi. Angka tersebut bukan persentase seluruh perempuan Indonesia atau seluruh perempuan BAK; tidak menunjukkan berapa orang pada setiap kabupaten dan tidak membuktikan penyebab penurunan TPAK Februari 2025–2026. Penjelasan cakupan survei berada pada halaman PDF 34 dan 53. [Laporan dan sumber angka](https://openknowledge.worldbank.org/bitstreams/def01f54-3416-4d85-b57a-4746be7a988d/download).

| Bukti | Kesimpulan yang dapat dibuat | Yang belum dapat dinyatakan |
|---|---|---|
| TPAK perempuan turun pada sejumlah provinsi | Ada perubahan partisipasi yang perlu ditelusuri | Perempuan dipaksa berhenti atau lowongan pasti menyusut |
| Instrumen Sakernas memuat keinginan dan hambatan | Ada rute data untuk menguji kebutuhan yang belum terpenuhi | Besarnya kebutuhan per wilayah sebelum mikrodata/tabulasi diperoleh |
| Penelitian Indonesia mendokumentasikan hubungan pekerjaan dan pengasuhan | Hambatan pengasuhan layak diuji | Pengasuhan menyebabkan seluruh penurunan 2025–2026 |
| Kemiskinan dan partisipasi tersedia menurut wilayah | Daerah dengan dua keadaan tersebut dapat diprioritaskan untuk pendalaman | Orang yang sama mengalami keduanya |
| Status perkawinan tersedia | Komposisi dan perbandingan antarkelompok dapat diteliti | Kesulitan ekonomi menyebabkan menikah lalu keluar angkatan kerja |

**Kesimpulan riset saat ini:** sumber yang relevan untuk membangun pembuktian sudah teridentifikasi, beberapa data nasional sudah diolah, dan mekanisme hambatan didukung penelitian Indonesia. Namun, data terpenting untuk menghitung kebutuhan bekerja yang belum terpenuhi per wilayah masih membutuhkan mikrodata penuh atau tabulasi BPS. Tidak ada klaim bahwa seluruh penurunan TPAK otomatis merupakan urgensi.

## 5. Urutan kerja yang direkomendasikan

1. Gunakan panel 38 provinsi sebagai penyaringan tanpa mengunci Jambi sebagai satu-satunya sasaran.
2. Peroleh tabulasi keinginan, kesiapan dan alasan menurut gender. Dahulukan estimasi provinsi yang layak; turunkan ke kabupaten hanya ketika sampel memadai.
3. Gunakan panel konteks 2025 untuk menentukan daerah pendalaman; perbedaan bulan dan penyebut tetap dinyatakan.
4. Periksa usia, sekolah, pendidikan dan struktur ekonomi sebagai penjelasan alternatif.
5. Hubungkan kelompok yang membutuhkan dukungan dengan mekanisme hambatannya. Penempatan kerja, pengasuhan, transportasi dan penyegaran keterampilan memerlukan bukti kebutuhan yang berbeda.

Rincian sumber berada pada `02_katalog_sumber_per_aspek.md`; rancangan analisis dan permintaan tabulasi tersedia dalam berkas 04 dan 05. Catatan akses dan audit tersedia pada berkas 06.
