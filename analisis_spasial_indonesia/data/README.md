# Panduan data dan penggabungan

## Pemisahan bahan

- `raw/`: dokumen dan halaman sumber asli, dokumentasi serta salinan panel nasional dari riset lokal.
- `extracted/`: teks PDF untuk pencarian; font tertentu dapat menghasilkan judul yang rusak. Baca render sumber saat judul/kolom menentukan interpretasi.
- `processed/`: CSV olahan, kamus variabel dan hasil validasi.
- `qa/`: halaman sumber yang dirender dan diperiksa. Bukan peta hasil analisis.

## Tabel yang sudah berisi angka

| Berkas | Baris | Kunci | Satuan dan periode |
|---|---:|---|---|
| panel_gender_38_provinsi_3_periode.csv | 117 | provinsi, periode | Orang; persen; upah nominal rupiah buruh. Feb 2025, Agu 2025, Feb 2026 |
| screening_perubahan_provinsi_feb2025_feb2026.csv | 39 | provinsi | Selisih rasio dalam poin persentase; selisih jumlah dalam orang |
| panel_konteks_38_provinsi_2025.csv | 38 | kode_prov_bps | Ketenagakerjaan Agustus; konteks Susenas/kemiskinan Maret 2025 |
| kemiskinan_514_kabupaten_kota_2025.csv | 514 | provinsi_sumber, kabupaten_kota_sumber, tahun | Jumlah miskin dalam ribu orang; P0 persen; P1/P2 indeks; garis kemiskinan Rp/kapita/bulan |
| kemiskinan_agregat_provinsi_2025.csv | 38 | provinsi_sumber, tahun | Agregat provinsi resmi; tidak dihitung dari rata-rata P0 kabupaten |
| internet_gender_desa_kota_provinsi_maret2025.csv | 117 | provinsi_sumber, klasifikasi_daerah, tahun | Persen; penyebut penduduk umur 5+ menurut gender dan daerah |
| status_perkawinan_gender_15_49_provinsi_maret2025.csv | 78 | provinsi_sumber, jenis_kelamin, tahun | Persen; penyebut penduduk umur 15–49 menurut gender |
| internet_gender_provinsi_2021_2024.csv | 304 | kode_prov_bps, jenis_kelamin, tahun | Persen; penyebut sesuai catatan lampiran, bukan khusus umur 15+; beberapa nilai lama Papua tidak tersedia |

Nilai Indonesia pada tabel 39 wilayah merupakan agregat nasional, bukan provinsi ke-39. Keluarkan saat analisis antardaerah. Data kemiskinan memakai nama wilayah sumber dan belum memiliki kode kabupaten BPS; kolom `kode_bps` kosong secara sengaja dan `status_join` menjelaskannya. Jangan memakai nomor urut di dalam provinsi sebagai kode kabupaten.

Kode provinsi dalam panel konteks disalin dari tabel berkode BPS yang diperiksa. Kode Kemendagri tidak selalu sama, khususnya provinsi baru Papua. Polygon belum disertakan, sehingga join GIS akhir belum diverifikasi.

## Nilai yang belum ada

Tidak ada angka estimasi keinginan bekerja, alasan tidak mencari, biaya pengasuhan, atau kesiapan per wilayah dalam paket ini. Kamus Sakernas 290 variabel, kuesioner, layout dan contoh DBF dalam ZIP merupakan dokumentasi. Contoh DBF tidak digunakan untuk membuat angka populasi.

Sel kosong bukan nol. Pertanyaan yang tidak ditanyakan karena alur instrumen berbeda dari jawaban “tidak”. Penyebut, kelas umur, periode survei dan konsep status harus disamakan sebelum membuat indikator baru.

## Memperbarui dengan sumber yang sudah tersimpan

Pengolahan memakai Python dengan pandas, pypdf dan pypdfium2. Skrip lokal mempertahankan nama sumber, mencatat koreksi label kode 53, dan memeriksa kunci serta jumlah wilayah. Jalankan `build_baseline.py` sebelum `process_auxiliary.py`; katalog dibangun oleh `build_catalogue.py`. Pengunduhan hanya diperlukan jika sumber baru ingin diambil. Tautan unduh langsung dapat kedaluwarsa; gunakan laman publikasi pada katalog untuk memperbaruinya.

`baseline_summary.json`, `auxiliary_validation.json`, dan `validasi_paket.json` mencatat pemeriksaan hasil. Catatan audit pada folder utama menjelaskan batas pemeriksaan tersebut.
