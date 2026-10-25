# Riset data analisis spasial partisipasi kerja perempuan Indonesia

Tanggal penelusuran: 24 Oktober 2026 (Asia/Jakarta).

Folder ini memisahkan sumber yang telah diakses, data numerik yang sudah tersedia, bukti penelitian, serta kebutuhan tabulasi yang belum diperoleh. Penurunan TPAK bukan otomatis bukti hambatan atau kerugian: tujuan riset adalah menguji keadaan tersebut.

## Mulai membaca

1. **[Hasil deep research](01_hasil_deep_research.md)** — temuan utama, data yang sudah diolah, bukti urgensi, dan kebutuhan data menurut aspek.
2. **[Katalog sumber per aspek](02_katalog_sumber_per_aspek.md)** — 38 entri sumber/dokumentasi dalam 17 kelompok aspek, dengan tautan, periode, resolusi wilayah, peran dan keterbatasan akses. Sejumlah entri adalah dokumentasi dari dataset yang sama, bukan penelitian independen.
3. **[Kamus indikator](03_kamus_indikator.md)** — 55 indikator dan status kesiapan; versi dengan pembilang, penyebut dan ID sumber ada di [CSV](kamus_indikator.csv).
4. **[Rancangan analisis spasial](04_rancangan_analisis_spasial.md)** — urutan analisis provinsi/kabupaten, definisi hasil, perbandingan periode dan batas model.
5. **[Spesifikasi tabulasi BPS](05_spesifikasi_permintaan_tabulasi_BPS.md)** — daftar yang dapat dibawa untuk konsultasi; belum dikirim.
6. **[Audit sumber dan batas bukti](06_audit_sumber_dan_batas_bukti.md)** — hasil pemeriksaan, salah label sumber, kegagalan akses, dan hal yang belum dibuktikan.

Katalog yang dapat difilter: [katalog_sumber.csv](katalog_sumber.csv), juga tersedia dalam JSON.

## Data yang sudah bisa digunakan

- [Panel konteks 38 provinsi 2025](data/processed/panel_konteks_38_provinsi_2025.csv): kerja, internet, perkawinan dan kemiskinan, dengan periode dan penyebut berbeda yang dinyatakan.
- [Panel ketenagakerjaan 38 provinsi, tiga periode](data/processed/panel_gender_38_provinsi_3_periode.csv) serta [penyaringan perubahan Februari 2025–2026](data/processed/screening_perubahan_provinsi_feb2025_feb2026.csv).
- [Kemiskinan 514 kabupaten/kota 2025](data/processed/kemiskinan_514_kabupaten_kota_2025.csv).
- [Internet menurut gender dan desa/kota Maret 2025](data/processed/internet_gender_desa_kota_provinsi_maret2025.csv).
- [Perkawinan menurut gender usia 15–49 Maret 2025](data/processed/status_perkawinan_gender_15_49_provinsi_maret2025.csv).

Data dasar lain dan dokumentasi tersedia dalam `data/processed/`. Lihat [panduan data](data/README.md) sebelum menggabungkan tabel. Pemisah CSV adalah koma; desimal titik; UTF-8 dengan BOM untuk kemudahan dibuka di Excel.

## Temuan penting

Penurunan TPAK bukan otomatis hambatan. Bukti Indonesia yang lebih langsung ditemukan pada laporan Bank Dunia: subkelompok ibu yang tidak bekerja/tidak mencari mempunyai minat bekerja yang bersyarat pada ketersediaan pengasuhan. Detail angka, populasi studi dan halaman bukti ada dalam laporan utama. Ini menjadi dasar menguji mekanisme, bukan bukti penyebab seluruh perubahan TPAK daerah.

**Yang belum tersedia:** mikrodata penuh dan tabulasi keinginan bekerja per wilayah; polygon yang telah berhasil diunduh dan dipadankan; estimasi presisi kelompok rinci. Belum ada peta urgensi final, Moran/LISA, regresi atau klaim kausal. Data yang hilang tidak diisi dengan dugaan atau contoh data.

## Struktur folder

```text
analisis_spasial_indonesia/
  01_...md sampai 06_...md   Laporan, katalog, metode dan audit
  katalog_sumber.csv/json   Inventaris sumber yang bisa difilter
  kamus_indikator.csv       Definisi dan kesiapan indikator
  data/raw/                PDF resmi, dokumentasi, snapshot laman
  data/extracted/          Ekstraksi teks sumber yang diperiksa
  data/processed/          Tabel numerik, indeks halaman, validasi
  data/qa/                 Render halaman sumber yang diperiksa
  scripts/                 Pengunduhan dan pengolahan yang dapat ditinjau
```

Folder analisis Jambi yang lama dipertahankan. Panel nasional awal disalin darinya dan asalnya dicatat. Pembelian mikrodata atau pengiriman permintaan kepada pihak luar tidak dilakukan.
