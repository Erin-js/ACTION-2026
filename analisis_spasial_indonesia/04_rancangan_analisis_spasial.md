# Rancangan analisis spasial yang sesuai dengan pertanyaan riset

## 1. Pertanyaan dan unit analisis

Pertanyaan utama: **di wilayah mana kebutuhan bekerja perempuan belum terpenuhi, hambatan apa yang berkaitan dengannya, dan bagaimana keadaan ekonominya?** Penurunan TPAK merupakan indikator penyaringan, bukan variabel tunggal yang mendefinisikan masalah.

Gunakan dua tingkat yang terpisah:

- **Indonesia, 38 provinsi:** awal yang dapat dijalankan dari panel lokal. Cocok untuk pola besar, perbandingan konteks dan pemilihan daerah pendalaman.
- **Kabupaten/kota:** tahap lanjutan menggunakan Sakernas Agustus dan tabulasi yang layak. Data kemiskinan 514 kabupaten sudah ada, tetapi TPAK gender serta keinginan bekerja seluruh kabupaten belum menjadi satu dataset dalam paket ini.

Jangan menyalin nilai provinsi ke seluruh kabupatennya lalu memperlakukannya sebagai 514 pengamatan independen. Ketersediaan 514 nilai kemiskinan tidak membuat semua aspek lain otomatis tersedia pada tingkat tersebut.

## 2. Pilihan periode

1. **Perubahan utama:** Februari 2025 → Februari 2026 pada provinsi. Indikator berasal edisi BPS yang sama; periksa catatan konsep dan jangan mencampurkan status ICLS-13 dengan indikator ICLS-19 tanpa harmonisasi.
2. **Konteks lintas wilayah:** Agustus 2025 untuk kerja, Maret 2025 untuk Susenas dan kemiskinan. Keduanya tahun sama tetapi bukan bulan atau responden sama. Catat sebagai keadaan pada dua titik waktu, bukan urutan sebab-akibat.
3. **Pembaruan:** Susenas Maret 2026 tersedia sebagai publikasi dalam folder raw; tabelnya belum diolah. Bisa dipakai setelah audit definisi untuk konteks yang lebih dekat dengan Februari 2026.
4. **Kabupaten:** utamakan rangkaian Agustus beberapa tahun. Jangan menghitung perubahan Agustus 2025 → Februari 2026 sebagai perubahan tahunan kabupaten. Jika beberapa gelombang digabung untuk meningkatkan sampel, estimand berubah menjadi periode gabungan dan desain/pembobotannya perlu ditetapkan.

## 3. Variabel hasil utama

| Hasil | Definisi yang diusulkan | Status |
|---|---|---|
| Partisipasi | TPAK perempuan dan perubahannya | Tersedia pada provinsi |
| Keterlibatan bekerja | EPR perempuan dan jumlah bekerja | Tersedia pada provinsi |
| Kebutuhan di luar AK | Perempuan BAK ingin bekerja / perempuan BAK | Belum dihitung; perlu tabulasi |
| Besaran kebutuhan populasi | Perempuan BAK ingin bekerja / perempuan 15+ | Belum dihitung |
| Hambatan khusus | Proporsi alasan yang relevan pada penerima pertanyaan valid | Belum dihitung |

Gunakan bobot survei untuk jumlah dan proporsi. Jangan membangun kelompok BAK hanya dari pertanyaan tidak mencari pekerjaan. Rekonstruksi status menurut algoritme resmi, kemudian terapkan alur keinginan/kesiapan dan tandai yang tidak ditanya. Definisi kebutuhan buatan diberi nama operasional, bukan label indikator resmi ILO.

## 4. Tahap analisis

### Tahap A — Audit sebelum pemetaan

- Cocokkan periode, konsep kerja, umur, jenis kelamin, unit, sumber dan penyebut.
- Pisahkan nol, tidak berlaku, tidak ditanyakan, disupresi, dan tidak tersedia.
- Periksa duplikasi kode, wilayah hilang, pemekaran Papua, dan perubahan batas.
- Minta jumlah sampel tanpa bobot, estimasi berbobot, SE/RSE dan tanda kelayakan publikasi untuk setiap sel yang dipakai.
- Rasio nasional dihitung dari pembilang/penyebut nasional atau jumlah berbobot yang benar, bukan rata-rata sederhana provinsi.

### Tahap B — Eksplorasi yang sudah dapat dimulai

Gunakan `panel_konteks_38_provinsi_2025.csv` untuk tabel dan grafik perbandingan TPAK/EPR, penggunaan internet, perkawinan dan kemiskinan. Tambahkan geometri resmi yang telah diverifikasi sebelum membuat peta.

Empat tampilan awal yang berguna:

1. TPAK/EPR perempuan menurut wilayah.
2. Perubahan tahunan dengan skala warna yang sama dan ketidakpastian bila tersedia.
3. Peta berdampingan kebutuhan bekerja dan kerentanan ekonomi, setelah variabel kebutuhan diperoleh.
4. Diagram pencar yang menampilkan arah hubungan serta semua provinsi, bukan hanya contoh yang mendukung dugaan.

Jumlah orang dan tingkat perlu ditampilkan bersama. Wilayah kecil dengan tingkat tinggi dan wilayah besar dengan kebutuhan banyak dapat sama-sama relevan, dengan implikasi layanan yang berbeda.

### Tahap C — Penjelasan alternatif

Bandingkan pola menurut umur, sekolah, pendidikan, perkawinan, kota/desa dan struktur sektor. Lakukan standardisasi umur jika tabulasi mendukung. Untuk perkawinan, utamakan TPAK menurut status pada kelompok umur sama; persentase perempuan kawin dalam populasi hanya konteks.

Jika partisipasi turun tetapi sekolah meningkat dan kebutuhan bekerja rendah, hasilnya tidak mendukung program penempatan massal. Jika kebutuhan bekerja tinggi dan alasan rumah tangga dominan, telusuri bentuk dukungan keluarga/pengasuhan. Jika alasan terkait pasar kerja dominan, telusuri akses dan kecocokan lowongan.

### Tahap D — Pola spasial eksploratif

**Moran's I global** dapat menguji apakah wilayah berdekatan cenderung memiliki nilai serupa. Definisikan tetangga secara substantif: persinggungan polygon, jarak, atau k tetangga terdekat. Indonesia memiliki kepulauan, sehingga tetangga polygon saja dapat menyisakan wilayah tanpa tetangga. Laporkan pilihan, penanganan wilayah terisolasi, dan periksa apakah hasil berubah pada alternatif bobot yang masuk akal.

Gunakan uji permutasi dengan seed serta jumlah pengacakan yang dicatat. Bila menghitung LISA, laporkan pengujian berulang, koreksi seperti FDR jika digunakan, dan statusnya sebagai analisis eksploratif. Tidak ada cluster signifikan bukan berarti tidak ada kebutuhan; kebutuhan bisa tersebar. Peta kuadran berdasarkan median/nasional tidak otomatis merupakan cluster spasial signifikan.

Rujukan metode: [PySAL, Global Spatial Autocorrelation](https://pysal.org/esda/stable/user-guide/global_morans_i.html), [GeoDa, glossary](https://geodacenter.github.io/glossary/). Pilihan jarak wajib mempertimbangkan proyeksi yang sesuai atau jarak geodesik; derajat lintang-bujur tidak diperlakukan sebagai kilometer.

### Tahap E — Hubungan antaraspek dan pendalaman

Mulai dari korelasi eksploratif dan perbandingan kelompok; laporkan arah serta kekuatan hubungan tanpa menyebut pengaruh kausal. Untuk 38 provinsi, jangan memasukkan puluhan prediktor atau langsung menggunakan GWR. Model yang terlalu rinci tidak menyelesaikan keterbatasan jumlah wilayah atau kesalahan pengukuran.

Jika regresi digunakan kemudian, tetapkan model ringkas berdasarkan mekanisme, audit keterkaitan antarprediktor, periksa residual spasial dan kepekaan hasil. Panel kabupaten beberapa tahun dapat memperluas informasi tetapi pengamatan berulang tetap saling berkaitan; banyak baris tidak otomatis berarti sampel independen besar.

Pilih daerah pendalaman berdasarkan kombinasi kebutuhan, besaran populasi, kondisi ekonomi, hambatan, kualitas data dan kemungkinan layanan. Hasil akhir sebaiknya berupa profil kebutuhan daerah, bukan peringkat tunggal yang menyembunyikan perbedaan masalah.

## 5. Bukti yang diperlukan untuk klaim yang lebih kuat

| Klaim | Bukti minimum yang relevan |
|---|---|
| Ada kebutuhan bekerja yang belum terpenuhi | Keinginan bekerja pada orang tidak bekerja, status dan alur pertanyaan valid, besaran berbobot dan presisi |
| Pengasuhan berkaitan dengan keterbatasan bekerja | Keinginan dan alasan/kesiapan pada orang yang sama, informasi pengasuhan; bukan status menikah saja |
| Keadaan tersebut berisiko secara ekonomi | Data kondisi ekonomi pada rumah tangga yang sama, atau pernyataan terbatas sebagai hubungan wilayah |
| Ekonomi sulit membuat perempuan menikah lalu berhenti | Urutan peristiwa dan kondisi sebelum kejadian pada individu; strategi identifikasi diperlukan untuk klaim sebab-akibat |
| Layanan tertentu efektif meningkatkan pekerjaan | Evaluasi program dengan pembanding/desain yang sesuai; hubungan spasial sebelum program tidak cukup |

## 6. Yang belum dilakukan dalam paket ini

Belum ada Moran/LISA, regresi, standardisasi umur, peta urgensi final atau estimasi jumlah perempuan terhambat. Polygon yang sesuai belum diperoleh; ZIP geometri alternatif sudah diunduh tetapi ternyata berupa garis dan tidak digunakan sebagai polygon. Dataset lengkap mikro Sakernas/Susenas/Podes belum diperoleh; contoh data Sakernas tidak dianalisis. Rancangan ini menyatakan jalur analisis yang dapat dipertanggungjawabkan, bukan hasil model yang sudah dijalankan.
