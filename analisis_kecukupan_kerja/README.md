# TPT Rendah, Apakah Pekerjaannya Sudah Cukup?

Riset dan notebook analisis berbasis BPS Sakernas untuk 38 provinsi. Tanggal riset: 15 Oktober 2026.

## Mulai membaca

- `Analisis_TPT_Rendah_Kecukupan_Pekerjaan.ipynb`: notebook lengkap dengan hasil eksekusi dan visualisasi tertanam.
- `Analisis_TPT_Rendah_Kecukupan_Pekerjaan.html`: versi baca tanpa menjalankan Python.
- `outputs/hasil_riset_dan_insight.md`: hasil dan daftar insight, masing-masing disertai batas interpretasi.
- `outputs/daftar_insight.csv`: daftar insight untuk diseleksi kembali.
- `outputs/figures/`: grafik PNG dan SVG yang dapat dipakai ulang.
- `sources.csv`: sumber, tautan, periode, status penggunaan, konflik sumber, serta sidik berkas.
- `data/processed/kamus_data.csv`: pengertian, satuan, penyebut, dan halaman sumber variabel.

## Cakupan

Panel utama berisi 117 baris: 38 provinsi dan satu agregat Indonesia pada Februari 2025, Agustus 2025, dan Februari 2026. Ada 65 kolom termasuk identitas, indikator sumber, dan variabel turunan. Indonesia dipisahkan saat analisis antarprovinsi.

Perbandingan tahunan utama memakai Februari 2025–Februari 2026. Agustus 2025 ditampilkan sebagai konteks musim. Data sektor hanya dibandingkan antarwilayah pada Februari 2026 karena perubahan KBLI 2020 menjadi KBLI 2025.

Sumber angka utama: publikasi BPS nasional dan rilis BPS Sulawesi Barat, dengan PDF disertakan. Katalog Satu Data Indonesia ditemukan, tetapi berkas numerik terkini yang dapat diverifikasi tidak berhasil diperoleh. Angka 2026 tidak diklaim berasal dari unduhan Satu Data. Rilis nasional Mei 2026 dicatat sebagai batas kemutakhiran, tidak dicampurkan ke panel Februari.

## Batas penting

- TPT rendah bukan ukuran lengkap mutu pekerjaan.
- Perubahan stok bekerja bukan jumlah lowongan atau jumlah perekrutan.
- Setengah pengangguran provinsi sebagian dihitung dari persentase 1–34 jam dikurangi paruh waktu. Galat pembulatan sekitar 0,01 persen poin; status angka dicatat pada setiap baris.
- Angka resmi nasional dan Sulbar yang terverifikasi dipertahankan meskipun berbeda tipis dari hasil pengurangan persentase.
- Upah hanya mencakup buruh/karyawan/pegawai; perubahan upah masih nominal.
- Informalitas dan pekerja keluarga bukan bukti otomatis kemiskinan atau pekerjaan tidak layak.
- Hubungan antarprovinsi tidak membuktikan sebab-akibat atau pola pada individu.
- Belum tersedia bukti langsung mengenai kompetensi lulusan, jurusan, diskriminasi lowongan, seluruh pendapatan pekerja, atau perlindungan sosial yang sebanding.

## Menjalankan ulang

Gunakan Python 3.11 atau versi yang kompatibel dan pasang dependensi dalam `requirements.txt`. Buka notebook melalui Jupyter, lalu jalankan seluruh sel. Notebook tidak memerlukan koneksi internet karena data dan sumber utama disertakan.

Untuk membangun ulang dari sumber PDF dan menjalankan pemeriksaan otomatis:

```text
python scripts/prepare_data.py
python scripts/build_notebook.py
python scripts/execute_validate.py
```

Pembangunan ulang menimpa notebook dan keluaran analisis di folder proyek ini. Cadangkan perubahan pribadi sebelum menjalankannya. Skrip eksekusi memakai kernel sementara dan menghapus registrasinya setelah selesai.

`prepare_data.py` menjaga jumlah orang resmi sebagai bilangan bulat, memeriksa kelengkapan 38 provinsi, mencocokkan jumlah provinsi dengan Indonesia, dan menyimpan halaman ekstraksi sebagai bukti. Transkripsi tabel tambahan tertera dalam skrip serta berkas CSV mentah. Transkripsi angka tabel web disimpan sebagai snapshot; kunjungan ulang diperlukan untuk mengecek revisi situs.

Ringkasan pemeriksaan ada dalam `outputs/notebook_validation.json` dan `outputs/ringkasan_validasi_data.json`. Pemeriksaan eksekusi tidak berarti seluruh hipotesis terbukti atau semua informasi sumber tanpa keterbatasan.
