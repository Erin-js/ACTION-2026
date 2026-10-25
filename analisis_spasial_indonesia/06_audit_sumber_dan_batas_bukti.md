# Audit sumber, akses, dan batas pembuktian

## 1. Status yang tidak boleh tertukar

| Status | Arti |
|---|---|
| Dataset numerik tersedia | Ada CSV nilai observasi wilayah yang diolah dan diperiksa dalam `data/processed/` |
| PDF publikasi tersedia | Dokumen penuh disimpan; belum tentu semua tabel diekstrak |
| Kamus/kuesioner tersedia | Variabel dan alur dapat diperiksa; bukan mikrodata penduduk penuh |
| Katalog/dasbor tersedia | Sumber teridentifikasi; file numerik atau ekspor nasional belum tentu diperoleh |
| Gagal akses | Tidak membuktikan data tidak ada; batas akses dijelaskan |

`data/access_log.json`, `download_log.json`, `evidence_access_log.json` dan `additional_access_log.json` menyimpan hasil akses langsung. `data/manifest_unduhan.csv` menyimpan ukuran dan SHA-256. Jejak asal panel lama berada dalam `data/local_provenance.json`.

## 2. Pemeriksaan yang sudah dilakukan

- Panel kerja: 117 baris, 39 wilayah per periode, 38 provinsi; rasio dihitung dari jumlah. Tabel TPAK BPS PDF 169 diperiksa visual, termasuk nasional 56,70% dan 56,41%.
- Kemiskinan: 514 baris kabupaten/kota, 38 agregat provinsi; kunci nama provinsi-wilayah-tahun unik. P0 berada pada rentang 0–100. Angka tidak dipisahkan menurut gender.
- Internet 2025: 117 baris wilayah-klasifikasi; tidak mengubah DKI perdesaan yang tidak berlaku menjadi nol. Tabel 7.4 PDF 240/cetak 196 diperiksa visual.
- Perkawinan: 78 baris wilayah-gender umur 15–49; komponen menjumlah sekitar 100% sesuai pembulatan. Tabel 2.7 PDF 68/cetak 24 diperiksa visual.
- Internet 2021–2024: 304 baris kombinasi; tahun lama beberapa provinsi Papua tetap kosong. Pemeriksaan nama tidak menghapus nama sumber asli.
- Panel konteks: join satu-ke-satu menghasilkan 38 provinsi tanpa nilai inti yang hilang; definisi umur dan periode tetap dicantumkan. Kode provinsi bersumber pada tabel berkode BPS, bukan ditebak dari kode Kemendagri.
- Kamus Sakernas: 290 variabel pada katalog berhasil disalin sebagai dokumentasi. Ini bukan jumlah kolom data mikro penuh yang telah dibeli.
- Temuan penelitian 32% diperiksa pada laporan Bank Dunia PDF 84/cetak 60; cakupan sampel dijelaskan terpisah.

Gambar halaman yang diperiksa tersedia di `data/qa/`. Ini pemeriksaan beberapa tabel kunci, bukan klaim pemeriksaan visual setiap halaman seluruh publikasi.

## 3. Kesalahan label yang ditemukan pada sumber resmi

Lampiran internet menurut gender dalam Statistik Telekomunikasi Indonesia 2024 mencetak **kode 53 dengan nama Nusa Tenggara Barat**, sementara kode 52 juga memakai nama itu. Baris kode 53 diperiksa visual pada halaman PDF 112/cetak 82. Kode BPS 53 adalah Nusa Tenggara Timur; konfirmasi dapat dilihat pada [referensi kode BPS](https://sirusa.bps.go.id/webadmin/doc/MFD_2010_Buku_3.pdf).

Dalam CSV:

- `provinsi_sumber` mempertahankan tulisan asli.
- `provinsi_baku` menamai kode 53 sebagai Nusa Tenggara Timur.
- `catatan_audit` menjelaskan koreksinya.

Nilai angkanya tidak diubah. Referensi kode historis hanya dipakai untuk mengonfirmasi kode 53, bukan sebagai daftar 38 provinsi Indonesia terkini.

## 4. Ekstraksi tabel bukan salinan layout sempurna

Enam nama kabupaten pada tabel kemiskinan terpotong lintas baris saat ekstraksi teks. Penggabungan label dilakukan sebelum parsing, termasuk nama panjang Ogan Komering Ulu Selatan, Penukal Abab Lematang Ilir, beberapa Bolaang Mongondow, serta Pangkajene dan Kepulauan. Data numerik tetap dibaca dari baris sumber. Jumlah akhir 514 diperiksa; berkas diagnostik `poverty_extraction_unparsed.json` menunjukkan tidak ada baris kabupaten berawalan nomor yang tersisa tanpa parsing.

Beberapa font publikasi Susenas menghasilkan teks judul yang rusak. Definisi tabel internet dan perkawinan diperiksa melalui render halaman, bukan ditebak dari teks ekstraksi. Tidak ada OCR atau imputasi angka yang tidak terbaca.

## 5. Pembatasan akses dan cakupan

- **Mikro Sakernas/Susenas/Podes penuh belum diperoleh.** Dokumentasi publik dan PDF kamus berhasil diperoleh. Tidak ada pembelian, permintaan eksternal atau login yang dilakukan.
- **ZIP Sakernas memuat contoh DBF.** Contoh tidak digunakan untuk menghitung populasi. Hanya kuesioner, layout dan daftar non-diseminasi yang dipisahkan sebagai dokumentasi.
- **Kode kecamatan/desa Sakernas tidak didiseminasikan** menurut dokumen resmi yang diunduh. Resolusi peta tidak boleh melebihi akses dan kelayakan estimasi.
- **Kemnaker Satu Data:** respons langsung berupa shell aplikasi; file XLSX yang ditawarkan belum diperoleh. Dasbor Pasker dibaca sebagai sumber administratif; belum diekspor menjadi dataset nasional.
- **Profil Perempuan Indonesia 2025:** indeks pencarian ditemukan, tetapi URL PDF resmi menghasilkan 404 pada pemeriksaan langsung. Tidak digunakan sebagai sumber angka paket ini.
- **BIG:** daftar layer utama dan informasi layer garis dapat dibaca melalui penelusuran, tetapi query polygon dan akses langsung mengalami timeout. Tidak ada geometri yang diklaim sudah tersimpan.
- **SDI/Kemendagri geometri:** resource shapefile ZIP berhasil diunduh. Pemeriksaan header SHP menunjukkan tipe 3 (Polyline); DBF berisi 1.298 segmen, bukan 514 polygon kabupaten. Berkas dipertahankan sebagai sumber yang diaudit dan tidak digunakan untuk choropleth atau ketetanggaan polygon. Nama berkas mengandung revisi 2023 walau metadata diunggah Oktober 2026; tanggal unggah tidak dianggap versi batas terbaru. Hasil ada pada `audit_geometri_sdi.json`.
- **IFLS:** halaman penyedia dapat dibaca melalui web; akses langsung otomatis menghasilkan 403. Tidak ada mikrodata IFLS yang diunduh atau klaim cakupan nasional terkini.
- Beberapa halaman BPS gagal melalui pembaca web, tetapi halaman dan unduhan publik resminya berhasil melalui akses HTTP biasa. Tidak ada penggunaan kunci API, pembelian, akun, atau akses yang melewati autentikasi.

## 6. Komparabilitas yang harus dijaga

1. BPS IPTK Februari 2026, PDF 33, menjelaskan adopsi instrumen ICLS-19/20/21 dengan pemeliharaan seri ICLS-13. Bedakan konsep pembentuk status sebelum memakai variabel keinginan dan kesiapan sebagai perluasan analisis.
2. Penyebut TPAK 15+, internet Susenas 5+, dan perkawinan 15–49 berbeda. Panel konteks memuat indikator agregat dengan definisi masing-masing, bukan satu populasi individu identik.
3. Susenas Maret dan Sakernas Agustus adalah sumber/waktu berbeda. Jangan menggabungkan rumah tangga secara individual melalui nama wilayah.
4. Papua lintas pemekaran memerlukan harmonisasi batas. Nilai kosong sebelum provinsi terbentuk bukan nol.
5. Jangan memakai IKG sebagai bukti independen bahwa TPAK berkaitan dengan ketimpangan tanpa memeriksa komponen: indikator komposit yang memasukkan TPAK akan menciptakan hubungan mekanis. Pilih komponen yang tidak tumpang tindih untuk penjelasan alternatif.
6. RSE/SE gender-kelompok dan varians selisih belum tersedia pada panel awal. Tidak ada klaim peringkat pasti atau signifikansi tahunan.

## 7. Bukti urgensi yang sudah ada dan batas transfernya

| Jenis | Hasil/verifikasi | Batas penggunaan |
|---|---|---|
| Survei ekonomi perawatan Indonesia | Subkelompok 1.706 ibu yang tidak bekerja/tidak mencari: 32% menyatakan minat bekerja penuh jika dukungan pengasuhan tersedia; laporan PDF 84 | Bukti kebutuhan bersyarat pada populasi studi; bukan 32% seluruh perempuan, bukan estimasi tiap kabupaten dan bukan efek program yang telah diuji |
| Penelitian riwayat kerja IFLS | Working paper IZA 2023 meneliti lebih dari 9.000 perempuan dan riwayat perkawinan/kelahiran/kerja | Mendukung relevansi riwayat individu; cakupan historis IFLS berbeda dari seluruh Indonesia terkini |
| Desain statistik ILO | Jobs gap memperluas perhatian pada orang yang ingin bekerja tetapi tidak termasuk pengangguran konvensional | Konsep tidak boleh dilabeli sebagai hasil resmi Indonesia sebelum dihitung dengan aturan dan data sesuai |
| Data nasional dan wilayah yang diolah | Penurunan partisipasi dan perbedaan konteks dapat ditelusuri | Belum mengidentifikasi individu yang terhambat atau penyebab perubahan |

Kesimpulan harus mengikuti tingkat bukti. Paket ini mendukung penyusunan analisis dan argumentasi awal; belum merupakan pembuktian kausal penurunan TPAK atau evaluasi efektivitas solusi.
