from pathlib import Path
import textwrap
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
cells=[]
def md(s): cells.append(nbf.v4.new_markdown_cell(textwrap.dedent(s).strip()))
def code(s): cells.append(nbf.v4.new_code_cell(textwrap.dedent(s).strip()))

md('''
# TPT Rendah, Apakah Pekerjaannya Sudah Cukup?
## Riset eksploratif 38 provinsi: jumlah pekerjaan, kecukupan jam kerja, dan batas kualitas pekerjaan

**Tujuan:** menguji apakah rendahnya pengangguran terbuka cukup untuk menggambarkan kesempatan kerja yang memadai, kemudian menemukan wilayah dan kelompok yang perlu diteliti lebih lanjut.

**Basis utama:** BPS, Sakernas Februari 2025, Agustus 2025, dan Februari 2026. Panel berisi **38 provinsi dan satu agregat Indonesia**, masing-masing tiga periode. Angka nasional dipisahkan dari observasi provinsi. Perbandingan tahunan utama: **Februari 2025–Februari 2026**. Tanggal penelusuran: **15 Oktober 2026**.

**Status riset:** analisis deskriptif dan eksploratif berbasis tabel agregat. Temuan tidak membuktikan penyebab, perpindahan individu, jumlah lowongan, atau mutu setiap pekerjaan. Rilis nasional Mei 2026 sudah ada; Februari 2026 dipilih sebagai periode bersama untuk banyak indikator provinsi, sehingga notebook ini **bukan klaim memakai setiap data paling baru**.

Jalankan semua sel dari atas ke bawah. Data pendamping tersedia di folder `data`; gambar dan daftar insight diperbarui di `outputs`. Ekstraksi dari PDF dapat diulang dengan `scripts/prepare_data.py`, yang memerlukan `pdfplumber`; analisis notebook hanya memerlukan pandas, numpy, matplotlib, dan scipy.
''')
md('''
### Kerangka analisis sebelum membaca hasil

1. **Apakah jumlah bekerja mengimbangi pertambahan angkatan kerja?** Bandingkan perubahan stok bekerja dan angkatan kerja, bukan menyamakannya dengan lowongan baru.
2. **Apakah jam kerjanya sudah cukup?** Pisahkan setengah penganggur dari pekerja paruh waktu. Bekerja singkat tidak selalu berarti ingin menambah pekerjaan.
3. **Bagaimana struktur pekerjaannya?** Status informal, pekerja keluarga, dan jam kerja panjang adalah dimensi tambahan; masing-masing tidak otomatis membuktikan pekerjaan tidak layak.
4. **Siapa dan di mana yang berbeda?** Telusuri provinsi, gender, pendidikan, dan wilayah perkotaan/perdesaan sesuai ketersediaan data.
5. **Seberapa kuat kesimpulannya?** Periksa penyebut, pembulatan, ketidakpastian survei, musim, dan sensitivitas pembagian kelompok.

**Hipotesis awal pengguna:** kekurangan pekerjaan dapat membuat pengangguran meningkat. Hipotesis alternatif: jumlah orang bekerja bertambah, tetapi kecukupan jam kerja, akses kelompok tertentu, atau mutu pekerjaan masih bermasalah. Kedua kemungkinan diperiksa terpisah.
''')
code('''
from pathlib import Path
import json
import platform
import warnings
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from scipy.stats import spearmanr
from IPython.display import display, Markdown, HTML

ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents, Path.cwd()/'analisis_kecukupan_kerja']
            if (p/'data/processed/panel_38_provinsi_3_periode.csv').exists())
DATA = ROOT/'data/processed'
OUT = ROOT/'outputs'
FIG = OUT/'figures'
FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'figure.dpi':110, 'savefig.dpi':180, 'font.size':10,
                     'axes.spines.top':False,'axes.spines.right':False,
                     'axes.titleweight':'bold','axes.titlesize':13,
                     'axes.facecolor':'#fafbfd','figure.facecolor':'white',
                     'axes.prop_cycle':matplotlib.cycler(color=['#136f85','#e58e26','#b84c65','#509b73','#7554a3'])})
C = {'teal':'#136f85','orange':'#e58e26','red':'#b84c65','green':'#509b73','gray':'#8795a5'}
P0, PM, P1 = '2025-02', '2025-08', '2026-02'
LABEL = {P0:'Feb 2025',PM:'Agu 2025',P1:'Feb 2026'}
panel = pd.read_csv(DATA/'panel_38_provinsi_3_periode.csv')
sources = pd.read_csv(ROOT/'sources.csv').fillna('')
kamus = pd.read_csv(DATA/'kamus_data.csv').fillna('')
nat = panel.query("provinsi == 'Indonesia'").set_index('periode').sort_index()
prov = panel.query("wilayah == 'Provinsi'").copy()
now = prov.query('periode == @P1').set_index('provinsi')
before = prov.query('periode == @P0').set_index('provinsi').reindex(now.index)
n, n0 = nat.loc[P1], nat.loc[P0]
insights, figures = [], []

def fmt(x, digit=2):
    return f'{x:,.{digit}f}'.replace(',', 'X').replace('.', ',').replace('X','.')

def view(df, n=50):
    display(HTML(df.head(n).to_html(index=True, float_format=lambda x:fmt(x))))

def insight(section, text, kind='Temuan deskriptif', limit='Tidak menyatakan sebab-akibat.'):
    item = {'id':f'I{len(insights)+1:03d}','bagian':section,'jenis':kind,'insight':text,'batas_interpretasi':limit}
    insights.append(item)
    display(Markdown(f"**{item['id']} · {kind}.** {text}  \\n*Batas:* {limit}"))

def finish(fig, name, title, unit='Persen', source='BPS IPTK Februari 2026; Sakernas', period='Februari 2026'):
    fig.suptitle(title, x=.02, ha='left', y=.995, fontsize=15, weight='bold', wrap=True)
    fig.tight_layout(rect=(0,.065,1,.94))
    foot=f'{unit} | {period}\\nSumber: {source}. Perhitungan penulis bila merupakan variabel turunan.'
    fig.text(.02,.013,foot,fontsize=8,color='#536474',va='bottom')
    for ext in ['png','svg']:
        fig.savefig(FIG/f'{name}.{ext}',bbox_inches='tight',facecolor='white')
    figures.append({'gambar':name,'judul':title,'satuan':unit,'periode':period,'sumber':source})
    plt.show()
    plt.close(fig)

def ranked(field, title, unit='Persen', ref=None, data=None, name=None):
    d = now if data is None else data
    s = d[field].sort_values()
    fig,ax=plt.subplots(figsize=(10,11))
    ax.barh(s.index,s.values,color=[C['orange'] if p=='Sulawesi Barat' else C['teal'] for p in s.index])
    if ref is not None:
        ax.axvline(ref,color=C['red'],ls='--',label=f'Indonesia: {fmt(ref)}')
        ax.legend(loc='lower right')
    for y,v in enumerate(s): ax.text(v+.025,y,fmt(v),va='center',fontsize=8)
    ax.set_xlim(min(0,s.min()*1.1),s.max()*1.15)
    ax.set_xlabel(unit)
    finish(fig,name or field,title,unit)

print('Python', platform.python_version(), '| pandas',pd.__version__, '| matplotlib',matplotlib.__version__)
print(f'{len(panel)} baris, {panel.shape[1]} kolom; {prov.provinsi.nunique()} provinsi; {prov.periode.nunique()} periode.')
''')
md('''
### 1. Sumber, keterjangkauan data, dan keputusan penggabungan

Sumber numerik utama adalah **publikasi nasional BPS** dan **rilis resmi BPS Sulawesi Barat**. Tabel web BPS dipakai sebagai validasi silang. Penelusuran Satu Data menemukan katalog relevan, tetapi berkas numerik terkini yang dapat diverifikasi tidak berhasil diperoleh. Karena itu, notebook **tidak mengatasnamakan angka 2026 sebagai hasil unduhan SDI**. Metadata katalog disimpan sebagai jejak penelusuran.

Lihat `sources.csv` untuk tautan, status penggunaan, periode, catatan konflik sumber, dan sidik berkas. Rincian variabel dan nomor halaman PDF ada di `data/processed/kamus_data.csv`. Berkas PDF disertakan untuk pemeriksaan ulang.
''')
code('''
view(sources[['id','produsen','cakupan','status','url']])
display(Markdown('**Peta sumber variabel:** angka orang: PDF 161–171 dan 189; TPAK/EPR/TPT: 169/172/185; status pekerjaan: 173–174; jam kerja: 180–183; formalitas: 184; pendidikan: 186–188/191; upah: 192; ketidakpastian TPT: 211; setengah pengangguran nasional: 106/108. Nomor tersebut adalah **halaman PDF**, bukan halaman cetak.'))
''')
md('''
### 2. Definisi operasional dan batas pertanyaan “cukup”

| Indikator | Penyebut / pengertian | Yang tidak dapat disimpulkan langsung |
|---|---|---|
| TPT | Penganggur / angkatan kerja × 100 | Banyaknya lowongan, mutu pekerjaan, seluruh penduduk tidak bekerja |
| EPR | Bekerja / penduduk usia kerja × 100 | Kelayakan pendapatan dan jam kerja |
| TPAK | Angkatan kerja / penduduk usia kerja × 100 | Semua yang bukan angkatan kerja ingin bekerja |
| Setengah pengangguran | Pekerja <35 jam yang masih mencari atau bersedia menerima pekerjaan lain / bekerja | Semua pekerja <35 jam kekurangan pekerjaan |
| Paruh waktu | Pekerja <35 jam yang tidak mencari dan tidak bersedia menerima pekerjaan lain / bekerja | Semua pekerja paruh waktu miskin atau terpaksa |
| Informal | Status pekerjaan selain buruh/karyawan/pegawai dan pengusaha dibantu buruh tetap | Setiap pekerjaan informal tidak layak atau berupah rendah |
| Upah | Rata-rata upah/gaji bersih sebulan buruh/karyawan/pegawai | Pendapatan semua pekerja, upah per jam, upah riil, kepatuhan terhadap UMP |
| ≥49 jam | Pangsa pekerja dengan jam kerja panjang | Pelanggaran hukum atau tidak adanya kompensasi lembur |

**Penting:** dalam konsep Sakernas, bekerja mencakup kegiatan ekonomi paling sedikit satu jam secara terus-menerus selama seminggu yang lalu serta yang sementara tidak bekerja. Pekerja keluarga/tidak dibayar masuk kelompok bekerja. Karena itu, “bekerja” dan “sudah memiliki pekerjaan yang mencukupi” adalah pertanyaan berbeda. Notebook menilai dimensi terukur, bukan menetapkan satu indeks mutu pekerjaan.
''')
code('''
checks = pd.read_csv(DATA/'audit_rekonsiliasi.csv')
assert len(panel)==117 and len(now)==38
assert not panel.duplicated(['provinsi','periode']).any()
assert (panel['ak']-panel['bekerja']==panel['penganggur']).all()
assert (panel['puk']==panel['ak']+panel['bak']).all()
assert (checks.hasil=='LULUS').all()
for t,g in prov.groupby('periode'):
    for f in ['puk','ak','bekerja','bak','penganggur','paruh_orang']:
        assert g[f].sum()==nat.loc[t,f]
audit = panel.loc[(panel.under-panel.under_turunan).abs()>.005,
                  ['provinsi','periode','under_turunan','under','status_under']]
view(audit)
print(f'{len(checks)} pemeriksaan rekonsiliasi tersimpan; seluruh identitas stok lulus.')
annual = pd.read_csv(ROOT/'data/raw/BPS_tabel_under_tahun_2025.csv').set_index('provinsi')
aug = panel.query('periode == @PM').set_index('provinsi')
cross = annual[['under_tabel']].join(aug[['under_turunan']])
cross['selisih_pp'] = (cross.under_tabel-cross.under_turunan).round(2)
assert cross.selisih_pp.abs().max() <= .011
cross.to_csv(DATA/'validasi_tabel_web_agustus2025.csv',encoding='utf-8-sig')
print('Validasi tabel web tahun 2025 terhadap Agustus 2025: deviasi maksimum',fmt(cross.selisih_pp.abs().max()),'pp.')
''')
md('''
Untuk provinsi selain Sulawesi Barat pada Februari, tingkat setengah pengangguran dihitung dari **persentase bekerja 1–34 jam dikurangi tingkat paruh waktu**. Dua komponen telah dibulatkan sehingga angka turunan memiliki galat pembulatan sekitar ±0,01 persen poin. Angka resmi nasional dan Sulawesi Barat dipertahankan meskipun berbeda 0,01 pp dari pengurangan komponen.

Seluruh jumlah orang resmi dijaga sebagai bilangan bulat. Jumlah informal atau setengah penganggur yang dihitung dari persen × jumlah bekerja adalah **estimasi dari tabel dibulatkan**, bukan hitungan resmi baru. Angka yang tidak tersedia tetap kosong; tidak diganti nol.
''')
md('### 3. Gambaran nasional: jumlah bekerja bertambah, pertanyaan kecukupan tetap terbuka')
code('''
fields=['ak','bekerja','penganggur','tpak','tpt','epr','under','paruh','informal','upah']
overview=nat[fields].copy()
overview.index=overview.index.map(LABEL)
view(overview)
fig,axes=plt.subplots(1,3,figsize=(15,4.8))
for ax, fs, title in zip(axes,[['ak','bekerja'],['tpt','under'],['informal']],
                        ['Angkatan kerja dan bekerja','TPT dan setengah pengangguran','Pekerja informal']):
    for f in fs: ax.plot(range(3),nat[f]/(1e6 if f in ['ak','bekerja'] else 1),'o-',label=f)
    ax.set_xticks(range(3),[LABEL[t] for t in nat.index]); ax.legend(); ax.set_title(title,fontsize=11)
    ax.set_ylabel('Juta orang' if 'ak' in fs else 'Persen'); ax.grid(axis='y',alpha=.2)
finish(fig,'01_nasional_3_periode','Gambaran nasional: jumlah bekerja dan kecukupan jam kerja','Juta orang / persen',period='Feb 2025, Agu 2025, Feb 2026')
da, de, du = n.ak-n0.ak, n.bekerja-n0.bekerja, n.penganggur-n0.penganggur
insight('Nasional',f'Jumlah bekerja bertambah {fmt(de,0)} orang, melebihi pertambahan angkatan kerja {fmt(da,0)} orang. Jumlah penganggur berkurang {fmt(-du,0)} orang.',limit='Selisih stok tahunan, bukan jumlah perekrutan atau lowongan baru; tidak membuktikan peluang cukup untuk setiap pencari kerja.')
insight('Nasional',f'TPT turun dari {fmt(n0.tpt)}% menjadi {fmt(n.tpt)}%, hanya {fmt(n0.tpt-n.tpt)} pp. Dalam saat yang sama, setengah pengangguran turun {fmt(n0.under-n.under)} pp menjadi {fmt(n.under)}%.',limit='Perubahan deskriptif; signifikansi perubahan belum diuji dengan varians selisih survei.')
insight('Nasional',f'Pada Februari 2026 masih ada {fmt(n.penganggur/1e6)} juta penganggur dan 10,73 juta setengah penganggur menurut angka resmi BPS.',limit='Penganggur dan setengah penganggur berbeda status; kedua kelompok disajikan terpisah sebelum penyebutnya disamakan.')
insight('Nasional',f'TPAK berubah {fmt(n.tpak-n0.tpak)} pp, sedangkan EPR berubah {fmt(n.epr-n0.epr)} pp.',limit='TPAK yang turun tidak otomatis berarti penduduk putus asa mencari pekerjaan; alasan keluar angkatan kerja tidak tersedia dalam panel.')
insight('Nasional',f'Pangsa informal berubah dari {fmt(n0.informal)}% menjadi {fmt(n.informal)}%. Perbaikan TPT tidak disertai penurunan pangsa informal nasional.',limit='Informalitas adalah klasifikasi status, bukan vonis mutu pekerjaan.')
''')
md('### 4. Pertambahan angkatan kerja dan bekerja: seluruh provinsi')
code('''
delta=now[['ak','bekerja','penganggur','tpak','tpt','epr','informal','under','paruh','pekerja_keluarga','jam49plus','upah']]-before[['ak','bekerja','penganggur','tpak','tpt','epr','informal','under','paruh','pekerja_keluarga','jam49plus','upah']]
delta=delta.add_prefix('d_')
delta['selisih_stok']=delta.d_bekerja-delta.d_ak
delta['selisih_per_1000ak']=1000*delta.selisih_stok/before.ak
delta['upah_growth_nominal']=100*(now.upah/before.upah-1)
def pola(r):
    if r.d_ak>0 and r.d_bekerja>0: return 'AK & bekerja naik; U '+('turun' if r.d_penganggur<0 else 'naik')
    if r.d_ak<0 and r.d_bekerja<0: return 'AK & bekerja turun; U '+('turun' if r.d_penganggur<0 else 'naik')
    return 'Pola lainnya'
delta['pola']=delta.apply(pola,axis=1)
assert np.allclose(delta.selisih_stok,-delta.d_penganggur)
fig,ax=plt.subplots(figsize=(10,7))
for label,g in delta.groupby('pola'):
    ax.scatter(g.d_ak/1000,g.d_bekerja/1000,s=55,label=f'{label} ({len(g)})',alpha=.8)
lims=[min(delta[['d_ak','d_bekerja']].min())/1000-40,max(delta[['d_ak','d_bekerja']].max())/1000+40]
ax.plot(lims,lims,'--',color=C['gray'],label='Δ bekerja = Δ AK'); ax.axhline(0,color='gray',lw=.7); ax.axvline(0,color='gray',lw=.7)
for p in ['Aceh','Papua Selatan','Sulawesi Barat','Jawa Tengah','Jawa Barat','Jawa Timur']:
    ax.annotate(p,(delta.loc[p,'d_ak']/1000,delta.loc[p,'d_bekerja']/1000),xytext=(5,5),textcoords='offset points',fontsize=8)
ax.set(xlabel='Perubahan angkatan kerja (ribu orang)',ylabel='Perubahan bekerja (ribu orang)'); ax.legend(fontsize=8)
finish(fig,'02_dinamika_stok','Dinamika stok tenaga kerja di 38 provinsi','Ribu orang',period='Perubahan Feb 2025–Feb 2026')
view(delta[['d_ak','d_bekerja','d_penganggur','selisih_per_1000ak','pola']].sort_values('d_penganggur',ascending=False))
insight('Dinamika provinsi',f'Jumlah penganggur meningkat di {int((delta.d_penganggur>0).sum())} provinsi, meskipun secara nasional berkurang.',limit='Agregat nasional tidak mewakili arah perubahan seluruh provinsi.')
for label,count in delta.pola.value_counts().items():
    insight('Dinamika provinsi',f'{count} provinsi berada pada pola: {label}.',limit='Pola perubahan stok; tidak mengidentifikasi apakah orang yang sama berganti status.')
paradox=delta.query('d_penganggur > 0 and d_tpt < 0')
insight('Penyebut',f'Terdapat {len(paradox)} provinsi dengan jumlah penganggur naik tetapi TPT turun: '+', '.join(paradox.index)+'.',limit='TPT adalah rasio; penyebut angkatan kerja dapat tumbuh lebih cepat daripada jumlah penganggur.')
''')
code('''
fig,ax=plt.subplots(figsize=(10,11))
s=delta.selisih_per_1000ak.sort_values()
ax.barh(s.index,s,color=np.where(s>=0,C['teal'],C['red']));ax.axvline(0,color='black',lw=.8)
ax.set_xlabel('Δ bekerja − Δ AK per 1.000 angkatan kerja Februari 2025')
finish(fig,'03_selisih_stok_ternormalisasi','Perubahan jumlah penganggur setelah ukuran provinsi disetarakan','Orang per 1.000 AK awal',period='Perubahan Feb 2025–Feb 2026')
insight('Ukuran wilayah',f'Pengurangan penganggur relatif terhadap AK awal terbesar terdapat di {s.idxmax()} ({fmt(s.max())} per 1.000 AK); kenaikan relatif terbesar di {s.idxmin()} ({fmt(-s.min())} per 1.000 AK).',limit='Indikator ini identitas aljabar −Δ penganggur/AK awal; bukan ukuran independen efektivitas kebijakan.')
contrib=delta.d_bekerja.sort_values(ascending=False)
insight('Ukuran wilayah',f'{contrib.index[0]} memberi pertambahan bekerja absolut terbesar: {fmt(contrib.iloc[0],0)} orang atau {fmt(contrib.iloc[0]/de*100)}% pertambahan bersih nasional.',limit='Kontribusi terhadap perubahan bersih dapat melebihi 100% secara gabungan karena sebagian provinsi mengalami penurunan.')
''')
md('### 5. TPT, ketidakpastian, dan definisi “rendah”')
code('''
ranked('tpt','TPT seluruh provinsi: rendah dalam ukuran apa?',ref=n.tpt,name='04_tpt_38_provinsi')
fig,ax=plt.subplots(figsize=(10,11))
d=now.sort_values('tpt')
ax.errorbar(d.tpt,range(len(d)),xerr=np.vstack([(d.tpt-d.tpt_ci_lower).clip(lower=0),(d.tpt_ci_upper-d.tpt).clip(lower=0)]),fmt='o',color=C['teal'],ecolor=C['gray'],capsize=2)
ax.set_yticks(range(len(d)),d.index);ax.axvspan(n.tpt_ci_lower,n.tpt_ci_upper,color=C['orange'],alpha=.25,label='Selang nasional')
ax.set_xlabel('TPT (%) dan selang kepercayaan publikasi BPS');ax.legend()
finish(fig,'05_tpt_selang_kepercayaan','Peringkat estimasi titik tidak selalu berarti perbedaan yang pasti','Persen')
low = now.tpt < n.tpt
insight('TPT',f'{int(low.sum())} provinsi memiliki TPT di bawah {fmt(n.tpt)}%, dengan nilai terendah {fmt(now.tpt.min())}% di {now.tpt.idxmin()}.',limit='“Rendah” berarti di bawah angka Indonesia, bukan ambang resmi BPS dan bukan bukti kesejahteraan tinggi.')
insight('Ketidakpastian',f'RSE TPT terbesar di {now.tpt_rse.idxmax()} sebesar {fmt(now.tpt_rse.max())}%. Selang kepercayaan disertakan untuk menghindari kepastian semu pada peringkat.',limit='Tumpang tindih selang bukan uji formal kesamaan dua provinsi; kovarians tidak tersedia.')
print('Selang TPT nasional:',n.tpt_ci_lower,'–',n.tpt_ci_upper)
''')
md('### 6. Kecukupan jam kerja: setengah pengangguran dan paruh waktu')
code('''
ranked('under','Setengah pengangguran: kebutuhan kerja tambahan yang masih tersisa',ref=n.under,name='06_under_38_provinsi')
fig,ax=plt.subplots(figsize=(11,12))
d=now.sort_values('jam1_34')
ax.barh(d.index,d.under,label='Setengah pengangguran: resmi/turunan',color=C['red'])
ax.barh(d.index,d.paruh,left=d.under,label='Paruh waktu',color=C['teal'])
ax.set_xlabel('Persen penduduk bekerja');ax.legend(loc='lower right')
finish(fig,'07_jam_pendek_terurai','Jam kerja singkat memiliki dua makna yang perlu dibedakan','Persen penduduk bekerja')
insight('Jam kerja',f'{now.under.idxmax()} memiliki estimasi titik setengah pengangguran tertinggi, {fmt(now.under.max())}%, sedangkan Indonesia {fmt(n.under)}%.',limit='Sebagian nilai provinsi adalah turunan; peringkat tidak diuji secara statistik.')
insight('Jam kerja',f'Pangsa bekerja 1–34 jam paling tinggi terdapat di {now.jam1_34.idxmax()}, {fmt(now.jam1_34.max())}%.',limit='Pangsa jam singkat mencakup pekerja paruh waktu yang tidak ingin menerima pekerjaan lain.')
insight('Jam kerja',f'Nasional: {fmt(n.jam1_34)}% bekerja 1–34 jam, terdiri dari sekitar {fmt(n.under)}% setengah penganggur dan {fmt(n.paruh)}% paruh waktu.',limit='Komponen berbeda 0,01 pp dari jumlah akibat pembulatan; tidak semua 33,23% perlu tambahan jam.')
''')
md('### 7. Pertemuan dua masalah: TPT rendah dan setengah pengangguran tinggi')
code('''
now['kelompok_jam']=np.select([low & (now.under>n.under),low & (now.under<=n.under),~low & (now.under>n.under)],
                             ['TPT rendah · under tinggi','TPT rendah · under rendah','TPT tinggi · under tinggi'],default='TPT tinggi · under rendah')
fig,ax=plt.subplots(figsize=(12,8))
for label,g in now.groupby('kelompok_jam'):
    ax.scatter(g.tpt,g.under,s=45+g.bekerja/1e6*12,alpha=.75,label=f'{label} ({len(g)})')
ax.axvline(n.tpt,ls='--',color='gray');ax.axhline(n.under,ls='--',color='gray')
for p in now.index:
    ax.annotate(p,(now.loc[p,'tpt'],now.loc[p,'under']),xytext=(4,3),textcoords='offset points',fontsize=7)
ax.set(xlabel='TPT (% angkatan kerja)',ylabel='Setengah pengangguran (% bekerja)');ax.legend(fontsize=8)
finish(fig,'08_kuadran_tpt_under','TPT rendah dapat berdampingan dengan kebutuhan kerja tambahan','Persen; ukuran titik = jumlah bekerja')
candidates=now.loc[low & (now.under>n.under)].sort_values('under',ascending=False)
view(candidates[['tpt','under','informal','paruh','pekerja_keluarga','tpak','status_under']])
insight('Kuadran',f'{len(candidates)} provinsi berada pada kelompok TPT di bawah Indonesia tetapi setengah pengangguran di atas Indonesia: '+', '.join(candidates.index)+'.',limit='Ini pembagian eksploratif berdasarkan acuan nasional; bukan klasifikasi resmi atau diagnosis penyebab.')
insight('Kuadran',f'Di antara provinsi dalam kelompok tersebut, total bekerja mencapai {fmt(candidates.bekerja.sum()/1e6)} juta orang.',limit='Jumlah seluruh pekerja dalam provinsi kelompok tersebut, bukan jumlah pekerja yang mengalami dua masalah sekaligus.')
''')
md('### 8. Struktur pekerjaan: informalitas dan pekerja keluarga')
code('''
fig,axes=plt.subplots(1,2,figsize=(14,6))
for ax,f,ylabel in zip(axes,['informal','pekerja_keluarga'],['Informal (% bekerja)','Pekerja keluarga (% bekerja)']):
    ax.scatter(now.tpt,now[f],s=50,color=C['teal'],alpha=.8)
    ax.axvline(n.tpt,color='gray',ls='--');ax.axhline(n[f],color='gray',ls='--')
    for p in ['Sulawesi Barat','Nusa Tenggara Timur','Papua Pegunungan','Bali','DKI Jakarta']:
        ax.annotate(p,(now.loc[p,'tpt'],now.loc[p,f]),xytext=(4,4),textcoords='offset points',fontsize=8)
    ax.set(xlabel='TPT (% angkatan kerja)',ylabel=ylabel)
finish(fig,'09_tpt_status_pekerjaan','Status pekerjaan melengkapi pembacaan TPT','Persen')
ranked('pekerja_keluarga','Pekerja keluarga/tidak dibayar tetap dihitung sebagai bekerja',ref=n.pekerja_keluarga,name='10_pekerja_keluarga')
insight('Status pekerjaan',f'{int((low & (now.informal>n.informal)).sum())} provinsi memiliki TPT di bawah nasional dan informalitas di atas nasional.',limit='Keanggotaan kelompok ini tidak otomatis sama dengan kelompok TPT rendah–under tinggi.')
insight('Status pekerjaan',f'Pangsa pekerja keluarga tertinggi terdapat di {now.pekerja_keluarga.idxmax()}, {fmt(now.pekerja_keluarga.max())}%.',limit='Pekerja keluarga tidak menerima upah langsung menurut status pekerjaan; pendapatan rumah tangga dan kesejahteraannya belum terukur.')
insight('Status pekerjaan',f'Secara nasional, sekitar {fmt(n.bekerja*n.pekerja_keluarga/100/1e6)} juta pekerja adalah pekerja keluarga/tidak dibayar berdasarkan estimasi persen × jumlah bekerja.',limit='Estimasi dari persentase dibulatkan; bukan jumlah resmi tersendiri.')
''')
code('''
statuses=['buruh','berusaha_tetap','berusaha_tidak_tetap','berusaha_sendiri','pekerja_bebas','pekerja_keluarga']
labels=['Buruh/karyawan','Pengusaha + buruh tetap','Dibantu tidak tetap','Berusaha sendiri','Pekerja bebas','Keluarga/tidak dibayar']
chosen=['Indonesia','Sulawesi Barat','Nusa Tenggara Timur','Bali','DKI Jakarta','Papua Pegunungan']
comp=panel.query('periode == @P1').set_index('provinsi').loc[chosen,statuses]
fig,ax=plt.subplots(figsize=(12,5))
left=np.zeros(len(comp))
for f,lab,color in zip(statuses,labels,['#136f85','#62a8ac','#d0bb6d','#e58e26','#aa829e','#b84c65']):
    ax.barh(comp.index,comp[f],left=left,label=lab,color=color);left+=comp[f].values
ax.set_xlim(0,100);ax.set_xlabel('Persen bekerja');ax.legend(ncol=3,loc='upper center',bbox_to_anchor=(.5,-.15),fontsize=8)
finish(fig,'11_komposisi_status','Provinsi dengan TPT rendah dapat memiliki struktur pekerjaan yang berbeda','Persen penduduk bekerja')
insight('Status pekerjaan',f'Bali memiliki TPT {fmt(now.loc["Bali","tpt"])}%, informalitas {fmt(now.loc["Bali","informal"])}%, dan setengah pengangguran {fmt(now.loc["Bali","under"])}%.',limit='Bali memberi pembanding agar TPT rendah tidak selalu digambarkan sebagai masalah yang sama di semua wilayah.')
''')
md('### 9. Dua sisi jam kerja: kekurangan dan jam panjang')
code('''
ranked('jam49plus','Bekerja minimal 49 jam: dimensi berbeda dari kekurangan jam',ref=n.jam49plus,name='12_jam_panjang')
fig,ax=plt.subplots(figsize=(10,7))
ax.scatter(now.under,now.jam49plus,s=50,color=C['teal'])
for p in ['Sulawesi Barat','DKI Jakarta','Nusa Tenggara Timur','Bali']:
    ax.annotate(p,(now.loc[p,'under'],now.loc[p,'jam49plus']),xytext=(4,4),textcoords='offset points',fontsize=8)
ax.axvline(n.under,color='gray',ls='--');ax.axhline(n.jam49plus,color='gray',ls='--')
ax.set(xlabel='Setengah pengangguran (% bekerja)',ylabel='Bekerja ≥49 jam (% bekerja)')
finish(fig,'13_under_dan_jam_panjang','Kekurangan jam dan jam panjang dapat hadir dalam provinsi yang sama','Persen penduduk bekerja')
insight('Jam panjang',f'Nasional: {fmt(n.jam49plus)}% pekerja bekerja minimal 49 jam, naik {fmt(n.jam49plus-n0.jam49plus)} pp dari Februari 2025.',limit='Bukan bukti pelanggaran jam kerja; tidak ada rincian kontrak, upah lembur, atau preferensi jam kerja.')
insight('Jam panjang',f'Pangsa ≥49 jam tertinggi di {now.jam49plus.idxmax()}, {fmt(now.jam49plus.max())}%.',limit='Angka provinsi tidak menunjukkan bahwa individu setengah penganggur juga bekerja panjang; kedua kelompok saling berbeda.')
''')
md('### 10. Upah: bukti tambahan dengan cakupan yang lebih sempit')
code('''
fig,axes=plt.subplots(1,2,figsize=(14,6))
for ax,x,xlab in zip(axes,['informal','under'],['Informal (% bekerja)','Setengah pengangguran (% bekerja)']):
    ax.scatter(now[x],now.upah/1e6,s=50,color=C['teal'])
    for p in ['Sulawesi Barat','DKI Jakarta','Papua Tengah','Nusa Tenggara Timur']:
        ax.annotate(p,(now.loc[p,x],now.loc[p,'upah']/1e6),xytext=(4,4),textcoords='offset points',fontsize=8)
    ax.set(xlabel=xlab,ylabel='Rata-rata upah buruh (juta Rp/bulan)')
finish(fig,'14_upah_dan_struktur','Upah buruh tidak mewakili pendapatan semua pekerja','Persen / juta rupiah per bulan')
fig,ax=plt.subplots(figsize=(10,11))
s=delta.upah_growth_nominal.sort_values()
ax.barh(s.index,s,color=np.where(s>=0,C['teal'],C['red']));ax.axvline(0,color='gray')
ax.set_xlabel('Perubahan upah buruh nominal (%)')
finish(fig,'15_perubahan_upah_nominal','Kenaikan upah nominal perlu dibedakan dari daya beli','Persen',period='Feb 2025–Feb 2026')
insight('Upah',f'Rata-rata upah buruh nasional {fmt(n.upah,0)} rupiah/bulan; perubahan nominal tahunan {fmt(100*(n.upah/n0.upah-1))}%.',limit='Belum dikoreksi inflasi, perubahan komposisi pekerja, jam kerja, dan perbedaan biaya hidup.')
insight('Upah',f'Upah nominal buruh menurun di {int((delta.upah_growth_nominal<0).sum())} provinsi.',limit='Tidak membuktikan upah individu turun karena sampel lintas periode bukan panel pekerja yang sama.')
insight('Upah',f'Pangsa buruh/karyawan/pegawai nasional hanya {fmt(n.buruh)}% dari seluruh bekerja. Angka upah tidak meliputi mayoritas status pekerjaan lainnya.',limit='Informalitas tidak dapat dijelaskan hanya dengan rata-rata upah yang mencakup kelompok buruh formal.')
''')
md('### 11. Gender: rendahnya TPT tidak selalu berarti akses yang setara')
code('''
ranked('gap_tpak_gender','Kesenjangan partisipasi laki-laki dan perempuan',unit='Persen poin',ref=n.gap_tpak_gender,name='16_gap_tpak_gender')
fig,axes=plt.subplots(1,2,figsize=(14,6))
for ax,fl,fm,lab in zip(axes,['tpt_perempuan','upah_perempuan'],['tpt_laki','upah_laki'],['TPT (%)','Upah buruh (juta Rp/bulan)']):
    divisor=1e6 if 'upah' in fl else 1
    ax.scatter(now[fm]/divisor,now[fl]/divisor,s=45,color=C['teal'])
    top=max(now[fm].max(),now[fl].max())/divisor*1.05
    ax.plot([0,top],[0,top],'--',color='gray');ax.set(xlabel='Laki-laki · '+lab,ylabel='Perempuan · '+lab)
    ax.set_xlim(0,top);ax.set_ylim(0,top)
finish(fig,'17_gender_tpt_upah','Partisipasi, pengangguran, dan upah mengukur kesenjangan yang berbeda','Persen / juta rupiah per bulan')
insight('Gender',f'TPAK laki-laki nasional {fmt(n.tpak_laki)}%, perempuan {fmt(n.tpak_perempuan)}%; selisih {fmt(n.gap_tpak_gender)} pp.',limit='Alasan partisipasi berbeda tidak diidentifikasi; kegiatan sekolah, pengasuhan, dan pilihan pribadi perlu data tambahan.')
insight('Gender',f'Gap TPAK terbesar di {now.gap_tpak_gender.idxmax()} sebesar {fmt(now.gap_tpak_gender.max())} pp.',limit='Besar gap bukan ukuran diskriminasi yang terisolasi dari faktor sosial dan demografi.')
insight('Gender',f'TPT perempuan lebih tinggi daripada laki-laki di {int((now.tpt_perempuan>now.tpt_laki).sum())} provinsi.',limit='Penyebut masing-masing adalah angkatan kerja menurut gender; partisipasi rendah dapat menyaring komposisi yang masuk angkatan kerja.')
insight('Gender',f'Gap kasar rata-rata upah buruh nasional {fmt(n.gap_upah_gender_persen)}% dari rata-rata upah laki-laki.',limit='Bukan estimasi diskriminasi upah; belum disesuaikan pekerjaan, jam, pendidikan, masa kerja, atau karakteristik lain.')
''')
md('### 12. Pendidikan: risiko dalam kelompok dan komposisi penganggur berbeda')
code('''
edu=['dasar','menengah','tinggi']
fig,axes=plt.subplots(1,2,figsize=(14,5))
axes[0].bar(edu,[n['tpt_edu_'+e] for e in edu],color=C['teal']);axes[0].set_ylabel('Penganggur / AK kelompok (%)');axes[0].set_title('TPT dalam kelompok pendidikan')
x=np.arange(3)
axes[1].bar(x-.18,[n['share_ak_edu_'+e] for e in edu],width=.36,label='Komposisi AK',color=C['teal'])
axes[1].bar(x+.18,[n['share_u_edu_'+e] for e in edu],width=.36,label='Komposisi penganggur',color=C['orange'])
axes[1].set_xticks(x,edu);axes[1].set_ylabel('Persen masing-masing populasi');axes[1].legend();axes[1].set_title('Komposisi: penyebut berbeda')
finish(fig,'18_pendidikan_risiko_komposisi','Kelompok terbesar di antara penganggur belum tentu berisiko tertinggi','Persen')
heat=now[['tpt_edu_'+e for e in edu]].sort_values('tpt_edu_tinggi',ascending=False)
fig,ax=plt.subplots(figsize=(8,12));im=ax.imshow(heat.values,aspect='auto',cmap='YlOrRd',vmin=0,vmax=heat.max().max())
ax.set_yticks(range(len(heat)),heat.index);ax.set_xticks(range(3),['Dasar ke bawah','Menengah','Tinggi'])
for i in range(len(heat)):
    for j in range(3): ax.text(j,i,fmt(heat.iloc[i,j]),ha='center',va='center',fontsize=8,color='white' if heat.iloc[i,j]>8 else 'black')
fig.colorbar(im,ax=ax,label='TPT dalam kelompok (%)')
finish(fig,'19_tpt_pendidikan_38_provinsi','Tingkat pendidikan tidak menghasilkan pola TPT yang seragam','Persen AK kelompok pendidikan')
highest=now[['tpt_edu_'+e for e in edu]].idxmax(axis=1).str.replace('tpt_edu_','',regex=False)
insight('Pendidikan',f'Nasional: TPT pendidikan dasar {fmt(n.tpt_edu_dasar)}%, menengah {fmt(n.tpt_edu_menengah)}%, dan tinggi {fmt(n.tpt_edu_tinggi)}%.',limit='Hubungan pendidikan dan pengangguran tidak mengukur kecakapan individu atau kesesuaian jurusan.')
insight('Pendidikan',f'Pendidikan tinggi memiliki TPT tertinggi di antara tiga kelompok pendidikan pada {int((highest=="tinggi").sum())} provinsi; pendidikan menengah pada {int((highest=="menengah").sum())} provinsi.',limit='Perbedaan komposisi usia, lokasi, preferensi pekerjaan, dan sampel belum dikendalikan.')
insight('Pendidikan',f'{fmt(n.share_under_edu_dasar)}% setengah penganggur nasional berpendidikan dasar ke bawah.',limit='Ini komposisi di antara setengah penganggur, bukan berarti persentase tersebut dari seluruh pekerja berpendidikan dasar kekurangan pekerjaan.')
''')
md('### 13. Konteks nasional perkotaan–perdesaan dan gender pada kecukupan jam')
code('''
context=pd.read_csv(ROOT/'data/raw/transkripsi_under_nasional.csv')
cn=context.query('periode == @P1').set_index('kelompok')
fig,axes=plt.subplots(1,2,figsize=(12,5))
for ax,groups in zip(axes,[['Laki-laki','Perempuan'],['Perkotaan','Perdesaan']]):
    for g in groups:
        d=context.query('kelompok == @g').set_index('periode').loc[[P0,PM,P1]]
        ax.plot([LABEL[t] for t in d.index],d.tingkat_under,'o-',label=g)
    ax.set_ylabel('Setengah pengangguran (% bekerja kelompok)');ax.legend()
finish(fig,'20_under_gender_desa_kota','Kebutuhan kerja tambahan lebih tinggi di perdesaan secara nasional','Persen penduduk bekerja kelompok',period='Feb 2025, Agu 2025, Feb 2026')
insight('Desa-kota',f'Setengah pengangguran perdesaan nasional {fmt(cn.loc["Perdesaan","tingkat_under"])}%, perkotaan {fmt(cn.loc["Perkotaan","tingkat_under"])}%; selisih {fmt(cn.loc["Perdesaan","tingkat_under"]-cn.loc["Perkotaan","tingkat_under"])} pp.',limit='Perbandingan nasional; pola ini belum tentu berlaku di setiap provinsi.')
insight('Gender dan jam',f'Setengah pengangguran laki-laki nasional {fmt(cn.loc["Laki-laki","tingkat_under"])}%, perempuan {fmt(cn.loc["Perempuan","tingkat_under"])}%.',limit='Tidak berarti perempuan secara keseluruhan memiliki akses kerja lebih baik; TPAK dan struktur pekerjaan berbeda.')
''')
md('### 14. Perubahan dua dimensi sekaligus: membaik pada TPT belum tentu pada jam')
code('''
fig,ax=plt.subplots(figsize=(11,8))
ax.scatter(delta.d_tpt,delta.d_under,s=55,color=C['teal'])
ax.axvline(0,color='gray');ax.axhline(0,color='gray')
for p in now.index:ax.annotate(p,(delta.loc[p,'d_tpt'],delta.loc[p,'d_under']),xytext=(3,3),textcoords='offset points',fontsize=7)
ax.set(xlabel='Perubahan TPT (pp)',ylabel='Perubahan setengah pengangguran (pp)')
finish(fig,'21_perubahan_tpt_under','Perubahan TPT dan kecukupan jam tidak selalu searah','Persen poin',period='Feb 2025–Feb 2026')
mixed=delta.query('d_tpt < 0 and d_under > 0.02')
insight('Perubahan jam',f'{len(mixed)} provinsi mengalami TPT turun tetapi estimasi setengah pengangguran naik lebih dari 0,02 pp: '+(', '.join(mixed.index) if len(mixed) else 'tidak ada')+'.',limit='Batas 0,02 pp menghindari pembacaan perubahan sekecil galat pembulatan dua periode; bukan ambang signifikansi survei.')
improve=delta.query('d_tpt < 0 and d_under < -0.02')
insight('Perubahan jam',f'{len(improve)} provinsi mengalami penurunan TPT dan setengah pengangguran sekaligus.',limit='Perbaikan deskriptif dua indikator belum cukup untuk menyimpulkan kesejahteraan rumah tangga membaik.')
''')
md('''
### 15. Menggabungkan pengangguran dan kekurangan jam dengan penyebut yang sama

TPT berpenyebut angkatan kerja, sedangkan tingkat setengah pengangguran berpenyebut bekerja. Menjumlahkan langsung kedua persentase menghasilkan ukuran yang keliru. Di bawah ini dihitung **proksi beban pengangguran dan setengah pengangguran terhadap angkatan kerja**:

\[
100\frac{U+\widehat{SP}}{AK}=TPT+\left(1-\frac{TPT}{100}\right)\times tingkat\;SP.
\]

Ini proksi turunan dari angka tampilan. Walaupun komponennya sejalan dengan konsep pemanfaatan tenaga kerja, **tidak diberi label LU2 resmi**. Kelompok di luar angkatan kerja yang masih berpotensi bekerja belum tercakup.
''')
code('''
ranked('beban_u_under_persen_ak','Proksi pengangguran + setengah pengangguran dengan penyebut seragam',ref=n.beban_u_under_persen_ak,name='22_proksi_beban_ak')
insight('Penyebut seragam',f'Proksi nasional pengangguran + setengah pengangguran mencapai {fmt(n.beban_u_under_persen_ak)}% angkatan kerja, dibanding TPT {fmt(n.tpt)}%.',limit='Proksi hasil perhitungan; bukan angka LU2 resmi dan tidak mencakup potensi angkatan kerja.')
insight('Penyebut seragam',f'Proksi tertinggi di {now.beban_u_under_persen_ak.idxmax()} sebesar {fmt(now.beban_u_under_persen_ak.max())}%.',limit='Peringkat indikator turunan tidak diartikan sebagai peringkat kualitas pekerjaan secara keseluruhan.')
''')
md('''
### 16. Asosiasi eksploratif dan sensitivitas

Korelasi Spearman dipakai untuk membaca hubungan peringkat pada **38 unit provinsi**, tanpa baris Indonesia. Korelasi bukan kausalitas dan tidak membenarkan kesimpulan pada individu. P-value tidak digunakan untuk memilih cerita dari banyak pasangan variabel. Seluruh pasangan yang direncanakan ditampilkan, termasuk hubungan yang lemah.
''')
code('''
corr_fields=['tpt','under','informal','pekerja_keluarga','jam49plus','tpak','upah','gap_tpak_gender']
cor=now[corr_fields].corr(method='spearman')
fig,ax=plt.subplots(figsize=(10,8))
im=ax.imshow(cor,vmin=-1,vmax=1,cmap='RdBu_r')
ax.set_xticks(range(len(cor)),cor.columns,rotation=45,ha='right');ax.set_yticks(range(len(cor)),cor.index)
for i in range(len(cor)):
    for j in range(len(cor)):ax.text(j,i,f'{cor.iloc[i,j]:.2f}',ha='center',va='center',color='white' if abs(cor.iloc[i,j])>.65 else 'black',fontsize=9)
fig.colorbar(im,ax=ax,label='Korelasi peringkat Spearman')
finish(fig,'23_korelasi_eksploratif','Hubungan lintas provinsi untuk eksplorasi, bukan sebab-akibat','Koefisien −1 sampai 1')
cor.to_csv(DATA/'korelasi_spearman.csv',encoding='utf-8-sig')
for a,b in [('tpt','under'),('under','informal'),('under','upah'),('tpt','informal')]:
    leave=[]
    for p in now.index:
        sub=now.drop(index=p)
        leave.append(spearmanr(sub[a],sub[b]).statistic)
    insight('Asosiasi',f'Spearman {a}–{b}: {fmt(cor.loc[a,b])}; rentang saat satu provinsi dikeluarkan bergiliran {fmt(min(leave))} sampai {fmt(max(leave))}.',kind='Asosiasi eksploratif',limit='Bukan efek sebab-akibat; pengaruh komposisi ekonomi dan faktor perancu belum dikendalikan.')

sensitivity=[]
for label,tx,ty in [('Acuan Indonesia',n.tpt,n.under),('Median 38 provinsi',now.tpt.median(),now.under.median()),('Acuan nasional: margin pembulatan under +0,01',n.tpt,n.under+.01)]:
    group=now.index[(now.tpt<tx)&(now.under>ty)]
    sensitivity.append({'aturan':label,'ambang_tpt':tx,'ambang_under':ty,'jumlah':len(group),'provinsi':'; '.join(group)})
sens=pd.DataFrame(sensitivity)
view(sens)
sens.to_csv(DATA/'sensitivitas_kuadran.csv',index=False,encoding='utf-8-sig')
insight('Sensitivitas',f'Jumlah provinsi dalam kuadran TPT rendah–under tinggi berubah dari {int(sens.iloc[0]["jumlah"])} dengan acuan nasional menjadi {int(sens.iloc[1]["jumlah"])} dengan median provinsi.',limit='Median memperlakukan provinsi sama berat; angka nasional dibobot oleh populasi terkait. Pembagian kuadran bergantung pertanyaan, bukan kebenaran tunggal.')
''')
md('### 17. Memilih studi wilayah secara transparan')
code('''
shortlist=now.loc[[p for p in ['Sulawesi Barat','Nusa Tenggara Timur','Nusa Tenggara Barat','Bali','Papua Pegunungan'] if p in now.index],['tpt','under','informal','pekerja_keluarga','paruh','jam49plus','upah','tpt_rse']]
view(shortlist)
insight('Pemilihan wilayah','Sulawesi Barat dipilih untuk pendalaman karena memiliki TPT di bawah nasional, estimasi titik setengah pengangguran tinggi, dan rilis BPS yang menyediakan angka resmi serta rincian kelompok.',kind='Keputusan analitis',limit='Pemilihan berbasis pertanyaan riset dan ketersediaan bukti; bukan penetapan provinsi dengan pekerjaan terburuk.')
insight('Pemilihan wilayah','NTT memberi pembanding struktur informal/pekerja keluarga; Bali memberi pembanding TPT rendah dengan kecukupan jam berbeda; Papua Pegunungan menguji kekeliruan menyamakan TPT paling rendah dengan pekerjaan memadai.',kind='Usulan pendalaman',limit='Pembanding dipilih untuk kontras deskriptif; belum merupakan evaluasi kebijakan antarwilayah.')
''')
md('### 18. Sulawesi Barat: perbaikan agregat dan kebutuhan kerja tambahan')
code('''
sb=panel.query("provinsi == 'Sulawesi Barat'").set_index('periode')
sb1,sb0=sb.loc[P1],sb.loc[P0]
fig,axes=plt.subplots(1,3,figsize=(15,5))
for ax,fs in zip(axes,[['tpt','under'],['informal','pekerja_keluarga'],['jam1_34','paruh']]):
    for f in fs:ax.plot([LABEL[t] for t in [P0,PM,P1]],sb.loc[[P0,PM,P1],f],'o-',label=f)
    ax.set_ylabel('Persen');ax.legend(fontsize=8);ax.grid(axis='y',alpha=.2)
finish(fig,'24_sulbar_tiga_dimensi','Sulawesi Barat: TPT turun, kebutuhan kerja tambahan tetap besar','Persen',source='BPS IPTK; BPS Sulbar BRS 5 Mei 2026',period='Feb 2025, Agu 2025, Feb 2026')
insight('Sulbar',f'TPT Sulawesi Barat {fmt(sb1.tpt)}%, sedangkan setengah pengangguran resmi {fmt(sb1.under)}% atau sekitar {fmt(sb1.under/n.under)} kali tingkat nasional.',limit='Penyebut TPT dan setengah pengangguran berbeda; perbandingan rasio hanya untuk tingkat under terhadap nasional.')
insight('Sulbar',f'Bekerja bertambah {fmt(sb1.bekerja-sb0.bekerja,0)} orang dan angkatan kerja {fmt(sb1.ak-sb0.ak,0)} orang; penganggur turun {fmt(sb0.penganggur-sb1.penganggur,0)} orang.',limit='Menunjukkan jumlah bekerja mengimbangi pertambahan AK dalam stok tahunan; tidak membuktikan semua kebutuhan pekerjaan tercukupi.')
insight('Sulbar',f'Angka resmi setengah penganggur Sulbar Februari 2026 sekitar 107,01 ribu orang dan paruh waktu 282,90 ribu orang; pangsanya masing-masing {fmt(sb1.under)}% dan {fmt(sb1.paruh)}%.',limit='Jumlah resmi dari lampiran BRS dalam ribu orang, sudah dibulatkan; kedua kelompok tidak boleh disamakan.')
insight('Sulbar',f'Informalitas Sulbar {fmt(sb1.informal)}% dan pekerja keluarga {fmt(sb1.pekerja_keluarga)}%. Pangsa keluarga turun {fmt(sb0.pekerja_keluarga-sb1.pekerja_keluarga)} pp dari Februari 2025.',limit='Ada perbaikan struktur tertentu sekaligus tingkat informal tinggi; narasi tidak boleh hanya menonjolkan indikator buruk.')
insight('Sulbar',f'Under Sulbar turun {fmt(sb0.under-sb1.under)} pp berdasarkan selisih angka tabel resmi; narasi BRS menulis penurunan 0,80 pp.',limit='Selisih 0,01 pp antarpenyajian sumber disimpan dalam catatan; notebook tidak memaksakan kesamaan angka yang telah dibulatkan.')
''')
md('### 19. Sulawesi Barat: agregat menutupi perbedaan kelompok')
code('''
detail=pd.read_csv(ROOT/'data/raw/transkripsi_sulbar_rincian.csv')
fig,axes=plt.subplots(1,3,figsize=(15,5))
for ax,ind,groups in zip(axes,['TPT','Setengah pengangguran','Paruh waktu'],[['Laki-laki','Perempuan'],['Laki-laki','Perempuan'],['Laki-laki','Perempuan']]):
    for g in groups:
        s=detail.query('indikator == @ind and kelompok == @g').set_index('periode').loc[[P0,P1]]
        ax.plot(['Feb 2025','Feb 2026'],s.nilai,'o-',label=g)
    ax.set_title(ind,fontsize=11);ax.set_ylabel('Persen kelompok');ax.legend(fontsize=8)
finish(fig,'25_sulbar_gender','Sulawesi Barat: perbaikan total tidak dialami setiap kelompok','Persen kelompok terkait',source='BPS Sulbar BRS 5 Mei 2026 PDF 8–10',period='Feb 2025–Feb 2026')
insight('Sulbar gender','TPT laki-laki naik dari 2,15% menjadi 2,92%, sedangkan perempuan turun dari 4,73% menjadi 2,95%. Penurunan TPT total menyembunyikan arah perubahan yang berlawanan.',limit='Tidak ada data panel individu dan varians perubahan kelompok; tidak menyimpulkan penyebab.')
insight('Sulbar gender','Setengah pengangguran laki-laki naik 14,26% → 15,11%, sedangkan perempuan turun 13,99% → 10,80%.',limit='Perbaikan agregat tidak seragam; perbedaan juga dapat dipengaruhi perubahan komposisi pekerja.')
insight('Sulbar desa-kota','TPT perkotaan Sulbar turun 5,74% → 4,12%, sedangkan perdesaan naik 2,39% → 2,51%.',limit='Perubahan dihitung dari angka tabel tampilan; narasi BRS menyebut kenaikan perdesaan 0,11 pp, sementara selisih tabel 0,12 pp.')
insight('Sulbar usia','TPT usia 15–24 tahun Sulbar 16,36%, jauh di atas TPT total 2,93%.',limit='Penyebut kelompok usia berbeda; RSE kelompok usia belum tersedia dalam ekstrak sehingga tidak membuat klaim peringkat pasti.')
edu_sb=detail.query("indikator == 'TPT pendidikan'").pivot(index='kelompok',columns='periode',values='nilai')
view(edu_sb)
insight('Sulbar pendidikan','TPT Diploma IV/S1/S2/S3 Sulbar naik 3,74% → 4,60%. Estimasi Diploma I/II/III Februari 2026 tidak ditampilkan BPS karena sampel tidak mencukupi.',limit='Tidak membuktikan keterampilan lulusan buruk, jurusan tertentu tidak dibutuhkan, atau pendidikan tinggi menyebabkan pengangguran.')
''')
md('### 20. Struktur sektor: konteks, bukan bukti ketidakcocokan jurusan')
code('''
sector=pd.read_csv(ROOT/'data/raw/transkripsi_sektor_2026.csv')
sector['indonesia_persen']=sector.indonesia_orang/n.bekerja*100
d=sector.sort_values('sulbar_persen')
fig,ax=plt.subplots(figsize=(12,8))
y=np.arange(len(d))
ax.barh(y-.18,d.indonesia_persen,height=.36,label='Indonesia',color=C['teal'])
ax.barh(y+.18,d.sulbar_persen,height=.36,label='Sulawesi Barat',color=C['orange'])
ax.set_yticks(y,d.sektor);ax.set_xlabel('Persen penduduk bekerja');ax.legend()
finish(fig,'26_sektor_sulbar_nasional','Sulawesi Barat lebih terkonsentrasi pada pertanian','Persen bekerja; KBLI 2025',source='BPS IPTK PDF 177–178; BPS Sulbar PDF 15')
ag=sector.query("kode == 'A'").iloc[0]
insight('Sektor',f'Pertanian menyerap {fmt(ag.sulbar_persen)}% pekerja Sulbar, dibanding {fmt(ag.indonesia_persen)}% nasional.',limit='Konsentrasi sektor tidak membuktikan setengah pengangguran berasal dari pertanian; diperlukan tabulasi silang sektor × jam × preferensi bekerja.')
insight('Sektor','Perbandingan sektoral lintas tahun tidak dihitung karena Februari 2025 memakai KBLI 2020 dan Februari 2026 memakai KBLI 2025.',kind='Keputusan metodologis',limit='Nama atau kode sektor serupa belum menjamin cakupan yang identik; perlu tabel korespondensi sebelum menghitung pertumbuhan sektor.')
''')
md('''
### 21. Bukti yang tersedia, hipotesis yang belum terbukti, dan rencana validasi

| Pernyataan | Status setelah analisis | Validasi berikutnya |
|---|---|---|
| Jumlah bekerja nasional tidak mengimbangi pertambahan AK | Tidak didukung oleh perubahan stok Feb 2025–Feb 2026 | Perpanjang seri bulan yang sama; periksa komponen arus masuk–keluar jika tersedia |
| TPT rendah berarti semua pekerjaan sudah cukup | Tidak memadai sebagai kesimpulan; kebutuhan kerja tambahan masih terukur | Dalami setengah pengangguran, pendapatan, jaminan sosial, dan preferensi jam |
| Semua pekerja informal memiliki pekerjaan buruk | Tidak dapat disimpulkan | Tabulasi penghasilan, jam, perlindungan sosial, dan status pekerjaan |
| Sulbar menunjukkan kekurangan jam pada semua kelompok | Terlalu luas; perubahan gender berbeda | Varians estimasi kelompok dan data lebih rinci |
| Lulusan kurang skill / jurusan tertentu tidak dibutuhkan | Belum teruji oleh panel ini | Data jurusan–pekerjaan, kompetensi, durasi mencari kerja, dan permintaan pekerjaan |
| Syarat lowongan dan upah tidak manusiawi menjadi penyebab | Belum teruji | Data lowongan representatif, jam, kontrak, upah per jam, dan survei pencari kerja |
| Pertanian menyebabkan under Sulbar tinggi | Hipotesis yang masuk akal untuk diteliti, belum terbukti | Tabulasi silang sektor × under × musim × gender; hindari simpulan ekologis |

**Prioritas pengayaan data yang belum dimasukkan:** pendapatan seluruh pekerja, upah per jam dan penyesuaian inflasi, kepesertaan jaminan sosial ketenagakerjaan dengan penyebut yang sebanding, pekerja miskin berbasis data individu/rumah tangga, TPT pemuda dan NEET seluruh provinsi pada periode sama, serta lowongan aktual dengan cakupan representatif. Ketiadaan data tersebut tidak diisi dengan proksi yang seolah-olah setara.

**Langkah validasi sebelum memakai angka dalam infografis:** (1) utamakan angka resmi under dari rilis masing-masing provinsi bila akan ditonjolkan; (2) periksa catatan RSE dan sampel rincian; (3) gunakan perbandingan bulan sama; (4) konfirmasi arah cerita dengan lebih dari satu indikator; (5) pisahkan fakta, penafsiran, dan usulan tindakan.

**Arah tindakan sebagai hipotesis kebijakan:** wilayah dengan kekurangan jam perlu penelusuran kesempatan kerja tambahan dan pola musim; wilayah dengan jam panjang perlu penelusuran upah per jam dan perlindungan; kesenjangan partisipasi memerlukan pemeriksaan hambatan akses. Efektivitas tindakan-tindakan tersebut belum dievaluasi oleh notebook ini.
''')
md('### 22. Daftar lengkap insight dan keluaran untuk dipakai ulang')
code('''
insight('Kesimpulan riset','TPT rendah hanya menjawab sebagian pertanyaan. Bukti jumlah bekerja, kecukupan jam, struktur pekerjaan, akses kelompok, dan upah perlu dibaca bersama tanpa menyamakan satu indikator dengan seluruh mutu pekerjaan.',kind='Interpretasi terpadu',limit='Kecukupan penghasilan dan kelayakan kerja belum terukur lengkap; rekomendasi masih perlu validasi.')
insight_df=pd.DataFrame(insights)
insight_df.to_csv(OUT/'daftar_insight.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(figures).to_csv(OUT/'daftar_visualisasi.csv',index=False,encoding='utf-8-sig')
now.join(delta).to_csv(DATA/'analisis_38_provinsi_feb2026_dan_perubahan.csv',encoding='utf-8-sig')
candidate_export=candidates[['tpt','under','informal','pekerja_keluarga','paruh','tpak','upah','status_under']]
candidate_export.to_csv(DATA/'kandidat_tpt_rendah_under_tinggi.csv',encoding='utf-8-sig')
text=['# Hasil riset: TPT Rendah, Apakah Pekerjaannya Sudah Cukup?',
      '', 'Basis: BPS Sakernas; periode utama Februari 2026, perubahan terhadap Februari 2025. Riset 15 Oktober 2026.',
      '', '**Batas:** deskriptif; bukan identifikasi sebab-akibat atau penilaian menyeluruh kelayakan kerja. Sebagian angka setengah pengangguran provinsi merupakan turunan, lihat status angka dalam data.', '']
for section,g in insight_df.groupby('bagian',sort=False):
    text+=['## '+section,'']
    for _,r in g.iterrows():text += [f"- **{r.id} [{r.jenis}]** {r.insight} Batas: {r.batas_interpretasi}"]
    text += ['']
text += ['## Sumber dan akses','', 'Satu Data menyediakan katalog relevan, tetapi angka terkini yang dapat diverifikasi tidak berhasil diperoleh. Sumber numerik utama: PDF BPS nasional dan BPS Sulbar.','']
for _,s in sources.iterrows():text += [f"- [{s['id']}: {s['judul']}]({s['url']}) — {s['status']}."]
(OUT/'hasil_riset_dan_insight.md').write_text('\\n'.join(text),encoding='utf-8')
report={'baris_panel':len(panel),'provinsi':len(now),'periode':3,'kolom_panel':panel.shape[1],
        'jumlah_insight':len(insights),'jumlah_visualisasi':len(figures),'rekonsiliasi_lulus':len(checks),
        'sumber_numerik_utama':['BPS_IPTK_2026','BPS_SULBAR_2026'],
        'angka_sdi_terkini_dipakai':False,'periode_utama':P1}
(OUT/'ringkasan_validasi_data.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
view(insight_df[['id','bagian','jenis','insight']])
print(f'Selesai: {len(insights)} insight, {len(figures)} visualisasi; setiap visual tersedia sebagai PNG dan SVG.')
print('Sumber, kamus data, audit, data analisis, daftar insight, dan gambar tersimpan bersama notebook.')
''')

nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'},'title':'TPT Rendah, Apakah Pekerjaannya Sudah Cukup?'})
path=ROOT/'Analisis_TPT_Rendah_Kecukupan_Pekerjaan.ipynb'
nbf.write(nb,path)
print(path)
print(len(cells),'cells')
