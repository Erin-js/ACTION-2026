from pathlib import Path
import re,csv,json
ROOT=Path(__file__).resolve().parents[1]; TEXT=ROOT/'data/extracted';OUT=ROOT/'data/processed'
targets={
'SUSENAS2025_PUB_PDF':{'perkawinan_15_49':r'2\.7\s+Persentase Penduduk','perkawinan_10plus':r'2\.4\s+Persentase Penduduk','pendidikan':r'3\.\d+\s+Persentase Penduduk','internet_5plus':r'7\.[1234]\s+Persentase Penduduk','paud':r'PAUD|Pendidikan Anak Usia Dini'},
'SAK2025_KUESIONER':{'keinginan':r'SRH_DES','alasan_tidak_mencari':r'SRH_DWY','alasan_tidak_ingin':r'SRH_DNW|SRH_WHY','riwayat_berhenti':r'MPK_ALSN','perkawinan':r'DEM_MRT','digital':r'TIK_A','perjalanan_kerja':r'MJU_TR|MJU_TIME|MJU_KAB'},
'SAK2025_NON_DISEMINASI':{'batas_diseminasi':r'kode_kec|kode_desa|SRH_|MPK_|penimbang'},
'BPS_IPTK_Feb2026':{'komparabilitas_ICLS':r'ICLS-13|ICLS ke-19','tpak_prov_gender':r'Indonesia 84,34 56,70','tpak_umur':r'Perempuan 56,70 56,63 56,41'},
'PODES2024_METADATA':{'transportasi':r'R1001C1|R1002AK5','digital':r'R1005C|R1005D','paud':r'R701AK2|R701AK3'},
'SUSENAS2025_METADATA':{'internet':r'INTERNET|TELEPON SELULER','perkawinan':r'STATUS PERKAWINAN','pendidikan':r'PENDIDIKAN TERTINGGI|PARTISIPASI SEKOLAH'},
'WB_CARE_REPORT_ID':{'metode':r'3\.000|3,000|52 kabupaten|52 district','kebutuhan':r'ingin bekerja|ingin mencari|berminat|menginginkan','hambatan_layanan':r'keterjangkauan|jam operasional|jam layanan'},
'IZA_CHILD':{'metode':r'Indonesia Family Life Survey|IFLS|event study|event-study'},
'DIGITAL2024_PDF':{'internet_gender':r'Persentase Penduduk Perempuan yang Mengakses Internet','internet_pria':r'Persentase Penduduk Laki-laki yang Mengakses Internet'},
'POVERTY2025_PDF':{'kemiskinan_kab':r'Tabel 2\.1|Lanjutan Tabel 2\.1'},
}
rows=[]
for stem,patterns in targets.items():
    file=TEXT/(stem+'.txt')
    if not file.exists():continue
    parts=re.split(r'===== PDF PAGE (\d+) =====',file.read_text(encoding='utf-8').replace('\r',''))
    for i in range(1,len(parts),2):
        pn=int(parts[i]);t=parts[i+1]
        for aspect,pattern in patterns.items():
            match=re.search(pattern,t,re.I)
            if match:
                excerpt=' '.join(t[max(0,match.start()-70):match.end()+160].split())
                rows.append({'source_file':stem+'.pdf','aspek':aspect,'halaman_pdf':pn,'petunjuk_lokasi':excerpt,'status':'Penunjuk lokasi; baca halaman lengkap sebelum mengutip'})
with (OUT/'indeks_halaman_bukti.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print(json.dumps([r for r in rows if r['source_file'] in ['SAK2025_KUESIONER.pdf','BPS_IPTK_Feb2026.pdf']],ensure_ascii=True,indent=2))
