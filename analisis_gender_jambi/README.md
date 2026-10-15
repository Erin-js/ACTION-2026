# Pengangguran Turun, Pekerjaan Perempuan Menyusut: Jambi

Riset 15 Oktober 2026. Makna judul adalah penyusutan **estimasi jumlah perempuan yang bekerja**, bukan jumlah posisi pekerjaan atau PHK.

## Berkas utama

- `Analisis_Gender_Jambi_Pengangguran_dan_Pekerjaan.ipynb`: notebook dengan hasil eksekusi dan grafik tertanam.
- `Analisis_Gender_Jambi_Pengangguran_dan_Pekerjaan.html`: versi baca tanpa Python.
- `outputs/hasil_riset_dan_insight.md`: seluruh insight dan batas interpretasinya.
- `outputs/daftar_insight.csv` dan `outputs/daftar_visualisasi.csv`: daftar keluaran yang dapat diseleksi kembali.
- `outputs/figures/`: gambar PNG serta SVG untuk penyuntingan lebih lanjut.
- `sources.csv`: tautan publikasi, produsen, periode, status pemakaian, batas bukti, dan SHA-256 berkas.

## Data dan cakupan

1. **Panel gender 38 provinsi dan Indonesia:** Februari 2025, Agustus 2025, Februari 2026, ditambah dua baris Jambi Februari 2024. Total 236 baris. Sumber: BPS nasional dan BPS Jambi.
2. **Rincian Jambi Februari 2024–2025:** 40 baris umur, 24 baris pendidikan yang telah disamakan kategorinya, 240 baris status pekerjaan × umur, dan 680 baris sektor × umur. Masing-masing membedakan gender.
3. **Konteks Agustus 2024–2025:** partisipasi menurut umur, EPR 11 kabupaten/kota, jam kerja, dan status pekerjaan; struktur sektor lengkap Agustus 2025. Bersumber dari dua publikasi Analisis Gender BPS Jambi.
4. **Satu Data/Open Data Jambi:** 264 baris pencari kerja terdaftar menurut 11 kabupaten/kota, bulan, dan gender pada 2023. Sumber administratif Disnakertrans, disajikan terpisah dari Sakernas.

Data mentah, PDF BPS, hasil ekstraksi halaman, dan transkripsi grafik berada di `data/raw`. Data yang siap dianalisis beserta audit dan kamus variabel berada di `data/processed`. Nomor halaman sumber adalah halaman PDF; halaman cetak bisa berbeda.

## Pertanyaan yang terjawab dan batasnya

Perubahan Februari 2025–2026 mendukung bahwa jumlah perempuan bekerja menyusut sementara laki-laki bertambah. Kontribusi penurunan jumlah penganggur lebih besar pada laki-laki. Kenaikan BAK perempuan juga diketahui, tetapi perpindahan individu dan alasannya belum dapat ditentukan.

Kestabilan diperiksa dengan tiga titik Februari. Rincian umur, sektor, dan kegiatan BAK menurut gender untuk 2026 belum diperoleh dalam riset ini. Karena itu, rincian 2024–2025 dipakai untuk konteks serta menyusun pertanyaan validasi, bukan untuk menetapkan penyebab perubahan 2026.

Notebook memisahkan Februari dari Agustus, jumlah dari rasio, TKK dari EPR, data survei dari data administratif, serta pekerja keluarga dari kegiatan BAK mengurus rumah tangga. Dekomposisi Shapley adalah uraian identitas matematis, bukan estimasi sebab-akibat. Tidak ada pengujian signifikansi perubahan karena varians selisih dan kovarians survei yang sesuai belum diperoleh.

`audit_kritik_sumber.csv` mencatat konflik angka grafik/narasi dan perubahan komponen indikator antar-edisi. Narasi normatif tentang pembagian peran gender dalam sumber tidak diadopsi sebagai instruksi atau fakta kausal.

## Menjalankan ulang

Gunakan Python 3.11 atau versi yang kompatibel, dengan dependensi pada `requirements.txt`. Buka notebook melalui Jupyter dan jalankan seluruh sel. Data lokal disertakan sehingga analisis tidak memerlukan internet.

Untuk membangun ulang dari PDF:

```text
python scripts/prepare_data.py
python scripts/build_notebook.py
python scripts/execute_validate.py
```

Pembangunan ulang menimpa notebook dan keluaran di proyek ini; cadangkan perubahan pribadi. Registrasi kernel sementara dihapus setelah eksekusi. Tautan unduh langsung dalam skrip penelitian dapat kedaluwarsa; tautan halaman publikasi yang stabil tersedia di `sources.csv`.

Pemeriksaan mencakup identitas PUK/AK/BAK, jumlah menurut kelompok umur, pendidikan, sektor, dan status, kecocokan publikasi Jambi dengan tabel nasional, serta kelengkapan struktur data administratif. Hasil ada pada `outputs/notebook_validation.json`, `outputs/ringkasan_validasi_data.json`, dan `data/processed/audit_rekonsiliasi.csv`.
