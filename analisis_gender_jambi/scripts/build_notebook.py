from pathlib import Path
import textwrap
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
cells=[]
def md(s):cells.append(nbf.v4.new_markdown_cell(textwrap.dedent(s).strip()))
def code(s):cells.append(nbf.v4.new_code_cell(textwrap.dedent(s).strip()))

md('''
# Pengangguran Turun, Pekerjaan Perempuan Menyusut
## Jambi: apakah perkembangan pekerjaan sama bagi laki-laki dan perempuan?

**Makna judul:** yang diamati adalah **estimasi jumlah perempuan yang bekerja**, bukan jumlah posisi lowongan, jumlah PHK, atau orang yang sama kehilangan pekerjaan.

**Riset 15 Oktober 2026.** Perbandingan utama: **Februari 2025–Februari 2026**. Kestabilan pola diperiksa memakai Februari 2024–2026. Agustus 2024–2025 menjadi jalur konteks tersendiri. Data administratif Satu Data Jambi 2023 dipisahkan dari estimasi Sakernas.

**Struktur argumen:** periksa konteks nasional dan provinsi → verifikasi perubahan Jambi → pisahkan gender → telusuri partisipasi dan penduduk usia kerja → periksa kelompok umur, pendidikan, sektor, status, dan kegiatan BAK pada periode yang tersedia → nilai batas bukti dan rencana validasi.

Notebook memuat analisis deskriptif, dekomposisi matematis, dan hipotesis pendalaman. Tidak ada klaim sebab-akibat, arus perpindahan individu, atau signifikansi statistik tanpa varians yang sesuai. Semua data dan PDF utama disertakan sehingga analisis dapat dijalankan tanpa internet.
''')
code('''
from pathlib import Path
from itertools import permutations
import json
import platform
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from IPython.display import display, Markdown, HTML

ROOT=next(p for p in [Path.cwd(),*Path.cwd().parents,Path.cwd()/'analisis_gender_jambi'] if (p/'data/processed/panel_gender_38_provinsi.csv').exists())
D=ROOT/'data/processed'; RAW=ROOT/'data/raw'; OUT=ROOT/'outputs'; FIG=OUT/'figures'
FIG.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'figure.dpi':110,'savefig.dpi':180,'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.titleweight':'bold','axes.titlesize':12,'axes.facecolor':'#f9fbfc','figure.facecolor':'white'})
SEX=['Laki-laki','Perempuan']; COL={'Laki-laki':'#176b83','Perempuan':'#db8d28'}
P0,P1='2025-02','2026-02'; YEARS=['2024-02',P0,P1]
LAB={'2024-02':'Feb 2024',P0:'Feb 2025',P1:'Feb 2026','2024-08':'Agu 2024','2025-08':'Agu 2025'}
AGE=['15-19','20-24','25-29','30-34','35-39','40-44','45-49','50-54','55-59','60+']
EDU=['SD ke bawah','SMP','SMA','SMK','Diploma I/II/III','Universitas']
hist=pd.read_csv(D/'panel_gender_38_provinsi.csv')
panel=pd.read_csv(RAW/'panel_nasional_38_provinsi.csv')
age=pd.read_csv(D/'aktivitas_umur_feb2024_2025.csv')
edu=pd.read_csv(D/'aktivitas_pendidikan_feb2024_2025.csv')
status=pd.read_csv(D/'status_umur_feb2024_2025.csv')
sector=pd.read_csv(D/'sektor_umur_feb2024_2025.csv')
activity=pd.read_csv(D/'aktivitas_total_feb2024_2025.csv')
admin=pd.read_csv(D/'pencari_kerja_terdaftar_2023.csv')
context24=pd.read_csv(RAW/'transkripsi_konteks_gender_agustus2024.csv')
context25=pd.read_csv(RAW/'transkripsi_konteks_gender_agustus2025.csv')
reg25=pd.read_csv(RAW/'transkripsi_epr_kabupaten_agustus2025.csv')
ageaug=pd.read_csv(RAW/'transkripsi_tpak_umur_agustus2024_2025.csv')
secaug=pd.read_csv(RAW/'transkripsi_sektor_agustus2025.csv')
sources=pd.read_csv(ROOT/'sources.csv').fillna('')
audits=pd.read_csv(D/'audit_rekonsiliasi.csv')
j=hist.query("provinsi=='Jambi'").set_index(['periode','jenis_kelamin']).sort_index()
b=j.loc[P0].reindex(SEX); a=j.loc[P1].reindex(SEX)
change=a[['puk','ak','bekerja','penganggur','bak','tpak','epr','tpt','tkk','upah']]-b[['puk','ak','bekerja','penganggur','bak','tpak','epr','tpt','tkk','upah']]
insights=[];figures=[]

def fmt(x,n=2):return f'{x:,.{n}f}'.replace(',','X').replace('.',',').replace('X','.')
def view(df,n=60):display(HTML(df.head(n).to_html(float_format=lambda x:fmt(x))))
def note(section,text,kind='Temuan deskriptif',limit='Tidak menunjukkan sebab-akibat atau perpindahan individu.'):
    item=dict(id=f'J{len(insights)+1:03d}',bagian=section,jenis=kind,insight=text,batas=limit)
    insights.append(item)
    display(Markdown(f"**{item['id']} · {kind}.** {text}  \\n*Batas:* {limit}"))
def finish(fig,name,title,unit,period='Februari 2025–Februari 2026',source='BPS, Sakernas; lihat sources.csv'):
    fig.suptitle(title,x=.02,y=.995,ha='left',fontsize=15,weight='bold')
    fig.tight_layout(rect=(0,.075,1,.94))
    fig.text(.02,.012,f'{unit} | {period}\\nSumber: {source}. Pengolahan penulis; konteks periode tertera pada grafik.',fontsize=8,color='#536373')
    for ext in ['png','svg']:fig.savefig(FIG/f'{name}.{ext}',bbox_inches='tight',facecolor='white')
    figures.append(dict(berkas=name,judul=title,satuan=unit,periode=period,sumber=source))
    plt.show();plt.close(fig)
def bars_pair(ax,frame,xlabel='',annotate=False):
    y=np.arange(len(frame));
    for off,sex in [(-.18,'Laki-laki'),(.18,'Perempuan')]:
        ax.barh(y+off,frame[sex],height=.35,label=sex,color=COL[sex])
        if annotate:
            for iy,v in enumerate(frame[sex]):ax.text(v,iy+off,' '+fmt(v),va='center',fontsize=8)
    ax.set_yticks(y,frame.index);ax.set_xlabel(xlabel);ax.legend(fontsize=9)
def dumbbell(ax,frame,xlabel='Persen'):
    y=np.arange(len(frame));ax.hlines(y,frame[SEX].min(axis=1),frame[SEX].max(axis=1),color='#bac5cc')
    for sex in SEX:ax.scatter(frame[sex],y,color=COL[sex],label=sex,s=40)
    ax.set_yticks(y,frame.index);ax.set_xlabel(xlabel);ax.legend(fontsize=8)
def rank_plot(series,title,name,unit,reference=None):
    s=series.sort_values();fig,ax=plt.subplots(figsize=(10,11))
    ax.barh(s.index,s,color=['#db8d28' if p=='Jambi' else '#176b83' for p in s.index]);ax.set_xlabel(unit)
    if reference is not None:ax.axvline(reference,color='#b14960',ls='--',label='Indonesia');ax.legend()
    finish(fig,name,title,unit,period='Februari 2026' if 'perubahan' not in name else 'Perubahan Feb 2025–Feb 2026')

assert len(hist)==236 and not hist.duplicated(['provinsi','periode','jenis_kelamin']).any()
assert (hist.ak==hist.bekerja+hist.penganggur).all()
assert (hist.puk==hist.ak+hist.bak).all()
assert (audits.hasil=='LULUS').all()
assert int(change.loc['Perempuan','bekerja'])==-24796
assert int(change.loc['Laki-laki','bekerja'])==21715
print('Python',platform.python_version(),'| pandas',pd.__version__,'| matplotlib',matplotlib.__version__)
print('Data: 236 baris panel gender; 40 baris umur; 24 baris pendidikan; 240 status×umur; 680 sektor×umur; 264 catatan SDI.')
print(len(audits),'audit rekonsiliasi lulus.')
''')
md('''
### 1. Sumber dan batas ketersediaan

| Pertanyaan | Data yang dipakai | Batas |
|---|---|---|
| Apakah jumlah perempuan bekerja menyusut? | BPS nasional, gender × provinsi, Feb 2025/2026 | Stok estimasi survei, bukan PHK atau pelacakan individu |
| Apakah pola sudah berlangsung lama? | Jambi Feb 2024/2025/2026 | Tiga titik tahunan; tidak cukup untuk klaim tren jangka panjang |
| Umur, pendidikan, sektor, dan status mana yang berbeda? | Tabel Jambi Feb 2024/2025; konteks Agu 2024/2025 | Rincian perubahan gender tahun 2026 belum diperoleh |
| Apa yang dilakukan perempuan di luar AK? | Kegiatan utama BAK Feb 2024/2025; jumlah BAK sampai Feb 2026 | Kegiatan utama bukan bukti alasan keluar pasar kerja |
| Bagaimana variasi kabupaten/kota? | EPR gender Agu 2024/2025 dari publikasi Analisis Gender | Tidak menjadi peta perubahan Februari 2026 |
| Bagaimana layanan pencari kerja? | CSV Open Data Jambi Jan–Des 2023, 11 daerah, 2 gender | Data administrasi; jumlah pendaftaran bukan seluruh penganggur |

Riset ini memakai **BPS sebagai sumber utama**, **CSV Satu Data/Open Data Jambi sebagai konteks layanan**, serta Bank Indonesia dan World Bank sebagai pendukung. Publikasi gender 2025 yang dirilis Juli 2026 telah diperiksa. Data yang lebih lama tidak disamarkan sebagai data 2026. Rilis nasional yang lebih baru dari Februari 2026 tidak digabung bila rincian yang sebanding belum diperoleh.
''')
code('''
view(sources[['id','produsen','periode','status','url']])
view(pd.read_csv(D/'audit_kritik_sumber.csv'))
note('Audit sumber','Tabel status dalam Analisis Gender 2024 mencakup pekerja bebas pada total yang disebut rentan, sedangkan tabel tiga status pada edisi 2025 tidak mencakupnya. Komponen disamakan sebelum dibandingkan.',kind='Keputusan metodologis',limit='Perubahan definisi tidak boleh dibaca sebagai penurunan kerentanan yang sebenarnya.')
note('Audit sumber','Untuk setengah pengangguran laki-laki Agustus 2025, angka grafik 9,87% dipakai. Angka ini sesuai 31,88% jam pendek dikurangi 22,01% paruh waktu; narasi 8,52% tidak dipakai.',kind='Keputusan metodologis',limit='Konflik dalam sumber resmi tetap dicatat, bukan disembunyikan.')
''')
md('''
### 2. Definisi yang menentukan arah cerita

**AK = bekerja + penganggur. PUK = AK + bukan angkatan kerja (BAK).** TPT memakai penyebut AK, sedangkan TPAK dan EPR memakai penyebut PUK. TKK = bekerja/AK = 100 − TPT; TKK bukan persentase seluruh penduduk usia kerja yang bekerja.

Karena itu, TPT perempuan dapat rendah sekalipun proporsi perempuan usia kerja yang bekerja juga rendah. Penduduk BAK meliputi sekolah, mengurus rumah tangga, dan kegiatan lainnya. Mereka tidak otomatis ingin bekerja, putus asa, atau baru saja keluar dari pekerjaan.

Jumlah dalam Sakernas merupakan estimasi tertimbang. Perbedaan jumlah antara dua survei tidak melacak orang yang sama. Kalimat “jumlah perempuan bekerja berkurang” didukung; kalimat “24.796 perempuan mengalami PHK” belum didukung.

Rasio panel dihitung ulang dari jumlah orang dan disimpan dengan presisi penuh. Selisihnya dapat berbeda 0,01 pp dari pengurangan dua angka yang telah dibulatkan dalam tampilan. Untuk transkripsi persentase grafik, ketelitian mengikuti angka sumber.
''')
md('### 3. Konteks nasional dan empat pola perkembangan gender')
code('''
nat=hist.query("provinsi=='Indonesia'").set_index(['periode','jenis_kelamin'])
nd=nat.loc[P1][['ak','bekerja','penganggur']]-nat.loc[P0][['ak','bekerja','penganggur']]
fig,ax=plt.subplots(figsize=(10,5));bars_pair(ax,nd.T.rename(index={'ak':'Angkatan kerja','bekerja':'Bekerja','penganggur':'Penganggur'})/1000,'Perubahan (ribu orang)');ax.axvline(0,color='gray')
finish(fig,'01_nasional_perubahan_gender','Nasional: perbaikan jumlah bekerja perlu dibaca menurut gender','Ribu orang')
pn=hist.query("provinsi!='Indonesia' and periode == @P1").pivot(index='provinsi',columns='jenis_kelamin',values=['bekerja','tpak','epr','ak','penganggur','puk','bak'])
pb=hist.query("provinsi!='Indonesia' and periode == @P0").pivot(index='provinsi',columns='jenis_kelamin',values=['bekerja','tpak','epr','ak','penganggur','puk','bak'])
dx=pn-pb
gd=pd.DataFrame({'laki':dx[('bekerja','Laki-laki')],'perempuan':dx[('bekerja','Perempuan')]})
gd['pola']=np.select([(gd.laki>=0)&(gd.perempuan>=0),(gd.laki>=0)&(gd.perempuan<0),(gd.laki<0)&(gd.perempuan>=0)],['Keduanya naik','Laki-laki naik; perempuan turun','Laki-laki turun; perempuan naik'],default='Keduanya turun')
fig,ax=plt.subplots(figsize=(11,7))
for label,g in gd.groupby('pola'):ax.scatter(g.laki/1000,g.perempuan/1000,s=50,alpha=.75,label=f'{label} ({len(g)})')
ax.scatter(gd.loc['Jambi','laki']/1000,gd.loc['Jambi','perempuan']/1000,s=150,facecolors='none',edgecolors='black',lw=1.5)
for p in ['Jambi','Aceh','Jawa Barat','Jawa Tengah','Jawa Timur']:ax.annotate(p,(gd.loc[p,'laki']/1000,gd.loc[p,'perempuan']/1000),xytext=(4,5),textcoords='offset points',fontsize=8)
ax.axvline(0,color='gray');ax.axhline(0,color='gray');ax.set(xlabel='Δ laki-laki bekerja (ribu orang)',ylabel='Δ perempuan bekerja (ribu orang)');ax.legend(fontsize=8)
finish(fig,'02_empat_pola_provinsi','Empat pola: Jambi berada dalam kelompok perkembangan yang berlawanan','Ribu orang')
fig,ax=plt.subplots(figsize=(10,4.5));gd.pola.value_counts().sort_values().plot.barh(ax=ax,color='#176b83');ax.set_xlabel('Jumlah provinsi')
finish(fig,'03_jumlah_provinsi_empat_pola','Pola gender tidak seragam di 38 provinsi','Provinsi')
note('Nasional',f'Jumlah bekerja nasional bertambah {fmt(nd.bekerja.sum(),0)} orang: laki-laki {fmt(nd.loc["Laki-laki","bekerja"],0)}, perempuan {fmt(nd.loc["Perempuan","bekerja"],0)}.')
note('Antarprovinsi',f'Jumlah perempuan bekerja turun di {int((gd.perempuan<0).sum())} provinsi; jumlah laki-laki bekerja turun di {int((gd.laki<0).sum())} provinsi.',limit='Jumlah provinsi memperlakukan semua wilayah setara; tidak sama dengan kontribusi jumlah orang.')
opposite=gd.query('laki > 0 and perempuan < 0')
note('Antarprovinsi',f'Jambi merupakan satu dari {len(opposite)} provinsi dengan laki-laki bekerja bertambah dan perempuan bekerja berkurang.',limit='Pola Jambi bukan kejadian tunggal nasional; pemilihan wilayah tidak boleh disebut paling buruk tanpa kriteria lain.')
view(gd.sort_values('perempuan'))
''')
md('### 4. Verifikasi Jambi: penurunan penganggur dan jumlah bekerja terjadi bersamaan')
code('''
view(pd.concat({'Feb 2025':b,'Feb 2026':a,'Perubahan':change},axis=1)[[(q,f) for q in ['Feb 2025','Feb 2026','Perubahan'] for f in ['ak','bekerja','penganggur','bak','tpak','epr','tpt']]])
fig,ax=plt.subplots(figsize=(11,6));bars_pair(ax,change[['ak','bekerja','penganggur','bak']].T.rename(index={'ak':'Angkatan kerja','bekerja':'Bekerja','penganggur':'Penganggur','bak':'Di luar angkatan kerja'})/1000,'Perubahan (ribu orang)');ax.axvline(0,color='gray')
finish(fig,'04_jambi_perubahan_gender','Jambi: jumlah bekerja laki-laki naik, perempuan turun','Ribu orang')
tot=change[['ak','bekerja','penganggur','bak','puk']].sum()
fig,ax=plt.subplots(figsize=(10,5))
vals=[change.loc['Laki-laki','bekerja'],change.loc['Perempuan','bekerja'],tot.bekerja]
starts=[0,vals[0],0]
ax.bar(['Laki-laki bekerja','Perempuan bekerja','Bekerja total'],np.array(vals)/1000,bottom=np.array(starts)/1000,color=['#176b83','#b24f69','#66798b'])
for i,v in enumerate(vals):ax.text(i,(starts[i]+v)/1000,fmt(v,0),ha='center',va='bottom' if v>=0 else 'top')
ax.axhline(0,color='gray');ax.set_ylabel('Perubahan (ribu orang)')
finish(fig,'05_jambi_jembatan_perubahan_bekerja','Tambahan laki-laki bekerja belum menutup penyusutan perempuan bekerja','Ribu orang')
note('Jambi inti',f'Jumlah perempuan bekerja turun {fmt(-change.loc["Perempuan","bekerja"],0)} orang ({fmt(100*change.loc["Perempuan","bekerja"]/b.loc["Perempuan","bekerja"])}%), sedangkan laki-laki bertambah {fmt(change.loc["Laki-laki","bekerja"],0)} orang ({fmt(100*change.loc["Laki-laki","bekerja"]/b.loc["Laki-laki","bekerja"])}%).')
note('Jambi inti',f'Jumlah bekerja total turun {fmt(-tot.bekerja,0)} orang, penganggur turun {fmt(-tot.penganggur,0)} orang, dan AK turun {fmt(-tot.ak,0)} orang. Identitas ΔAK = Δbekerja + Δpenganggur terpenuhi.')
note('Jambi inti',f'{fmt(100*(-change.loc["Laki-laki","penganggur"])/(-tot.penganggur))}% penurunan jumlah penganggur berasal dari selisih jumlah pada laki-laki.',limit='Ini kontribusi aritmetis perubahan stok, bukan bukti perempuan keluar AK menyebabkan penurunan pengangguran.')
note('Jambi inti',f'Jumlah penganggur perempuan turun {fmt(-change.loc["Perempuan","penganggur"],0)} orang, jauh lebih kecil daripada penyusutan jumlah perempuan bekerja.',limit='Dua selisih tidak menunjukkan ke mana orang yang sama berpindah.')
fig,ax=plt.subplots(figsize=(10,4.5));frame=pd.DataFrame({LAB[p]:j.loc[p].reindex(SEX).bekerja for p in [P0,P1]}).T
bottom=np.zeros(2)
for sex in SEX:
    shares=frame[sex]/frame.sum(axis=1)*100
    ax.barh(frame.index,shares,left=bottom,color=COL[sex],label=sex)
    for i,v in enumerate(shares):ax.text(bottom[i]+v/2,i,fmt(v)+'%',ha='center',va='center',color='white',weight='bold')
    bottom+=shares.values
ax.set_xlim(0,100);ax.set_xlabel('Komposisi seluruh bekerja (%)');ax.legend(loc='lower right')
finish(fig,'06_komposisi_gender_bekerja','Porsi perempuan di antara penduduk bekerja ikut berkurang','Persen seluruh penduduk bekerja')
note('Komposisi',f'Porsi perempuan di antara seluruh penduduk bekerja berubah dari {fmt(100*b.loc["Perempuan","bekerja"]/b.bekerja.sum())}% menjadi {fmt(100*a.loc["Perempuan","bekerja"]/a.bekerja.sum())}%.',limit='Komposisi pekerja berbeda dari tingkat partisipasi perempuan, yang berpenyebut PUK perempuan.')
''')
md('### 5. Kestabilan pola: bandingkan Februari dengan Februari')
code('''
fig,axes=plt.subplots(1,3,figsize=(15,5))
for ax,f,title in zip(axes,['bekerja','tpak','tpt'],['Jumlah bekerja','TPAK','TPT']):
    for sex in SEX:
        y=[j.loc[(p,sex),f]/(1000 if f=='bekerja' else 1) for p in YEARS]
        ax.plot([LAB[p] for p in YEARS],y,'o-',label=sex,color=COL[sex])
    ax.set_title(title);ax.set_ylabel('Ribu orang' if f=='bekerja' else 'Persen');ax.legend(fontsize=8);ax.grid(axis='y',alpha=.2)
finish(fig,'07_februari_tiga_tahun','Penyusutan perempuan bekerja pada 2026 membalik kenaikan pada 2025','Ribu orang / persen',period='Februari 2024, 2025, 2026')
f24=j.loc[('2024-02','Perempuan')];f25=b.loc['Perempuan'];f26=a.loc['Perempuan']
note('Kestabilan',f'Perempuan bekerja naik {fmt(f25.bekerja-f24.bekerja,0)} orang pada Feb 2024–2025, kemudian turun {fmt(f25.bekerja-f26.bekerja,0)} orang pada Feb 2025–2026.',limit='Tiga titik tahunan tidak mendukung klaim bahwa pekerjaan perempuan terus menyusut setiap tahun.')
note('Kestabilan',f'Dibanding Februari 2024, jumlah perempuan bekerja Februari 2026 lebih rendah {fmt(f24.bekerja-f26.bekerja,0)} orang, sementara PUK perempuan lebih banyak {fmt(f26.puk-f24.puk,0)} orang.')
note('Partisipasi',f'TPAK perempuan turun dari {fmt(f25.tpak)}% ke {fmt(f26.tpak)}% ({fmt(f26.tpak-f25.tpak)} pp), sedangkan laki-laki berubah {fmt(change.loc["Laki-laki","tpak"])} pp.')
gap0=b.loc['Laki-laki','tpak']-b.loc['Perempuan','tpak'];gap1=a.loc['Laki-laki','tpak']-a.loc['Perempuan','tpak']
note('Partisipasi',f'Kesenjangan TPAK melebar dari {fmt(gap0)} menjadi {fmt(gap1)} pp, atau {fmt(gap1-gap0)} pp.',limit='Gap partisipasi tidak sendirinya mengisolasi diskriminasi, preferensi, maupun beban pengasuhan.')
note('Penyebut',f'EPR perempuan turun dari {fmt(f25.epr)}% ke {fmt(f26.epr)}%, sementara TKK perempuan tetap sekitar {fmt(f26.tkk)}%.',limit='TKK hanya melihat perempuan yang masuk AK; EPR melihat seluruh PUK perempuan.')
note('Penyebut',f'TPT perempuan Februari 2026 {fmt(f26.tpt)}%, lebih rendah dari laki-laki {fmt(a.loc["Laki-laki","tpt"])}%, tetapi EPR perempuan hanya {fmt(f26.epr)}% dibanding laki-laki {fmt(a.loc["Laki-laki","epr"])}%.',limit='TPT yang rendah tidak membuktikan akses bekerja yang setara.')
''')
md('### 6. PUK, angkatan kerja, dan bukan angkatan kerja: apa yang benar-benar terukur?')
code('''
fig,axes=plt.subplots(1,2,figsize=(12,5))
for ax,sex in zip(axes,SEX):
    vals=change.loc[sex,['puk','ak','bak']]/1000
    ax.bar(['Δ PUK','Δ AK','Δ BAK'],vals,color=['#66798b',COL[sex],'#8aa4af']);ax.axhline(0,color='gray');ax.set_title(sex);ax.set_ylabel('Ribu orang');ax.set_ylim(-32,55)
    for i,v in enumerate(vals):ax.text(i,v,fmt(v),ha='center',va='bottom' if v>=0 else 'top')
finish(fig,'08_neraca_puk_ak_bak','Jumlah perempuan di luar angkatan kerja meningkat','Ribu orang')
note('BAK',f'PUK perempuan bertambah {fmt(change.loc["Perempuan","puk"],0)} orang, AK berkurang {fmt(-change.loc["Perempuan","ak"],0)} orang, sehingga BAK perempuan bertambah {fmt(change.loc["Perempuan","bak"],0)} orang.')
note('BAK',f'Perempuan menyumbang {fmt(100*change.loc["Perempuan","bak"]/tot.bak)}% dari kenaikan BAK total Jambi.',limit='Tidak sama dengan proporsi orang yang keluar dari AK; penuaan, migrasi, dan perubahan status tidak dipisahkan.')
note('BAK',f'Pada Februari 2026, {fmt(100*f26.bak/f26.puk)}% PUK perempuan berada di luar AK, dibanding {fmt(100*a.loc["Laki-laki","bak"]/a.loc["Laki-laki","puk"])}% laki-laki.',limit='BAK bukan seluruhnya pencari kerja potensial dan bukan ukuran pengangguran tersembunyi yang terverifikasi.')
''')
md(r'''
### 7. Dekomposisi matematis: pertumbuhan PUK, partisipasi, dan proporsi bekerja di dalam AK

Identitas yang dipakai:
\[
E=P\times(AK/P)\times(E/AK).
\]

Perubahan E diuraikan dengan **Shapley tiga faktor**: rata-rata kontribusi setiap faktor dalam enam urutan pergantian nilai awal ke akhir. Rasio dihitung dari jumlah orang agar tidak menimbulkan residu pembulatan. Komponen **tidak ditafsirkan sebagai efek kausal**. Faktor partisipasi merangkum perubahan AK/PUK, tanpa menjelaskan alasan atau orang yang berpindah.
''')
code('''
def shapley_product(x0,x1):
    out=np.zeros(len(x0))
    for order in permutations(range(len(x0))):
        x=np.array(x0,dtype=float)
        for k in order:
            initial=np.prod(x);x[k]=x1[k];out[k]+=np.prod(x)-initial
    return out/6
decomp=[]
for sex in SEX:
    r0,r1=b.loc[sex],a.loc[sex]
    x0=[r0.puk,r0.ak/r0.puk,r0.bekerja/r0.ak];x1=[r1.puk,r1.ak/r1.puk,r1.bekerja/r1.ak]
    vals=shapley_product(x0,x1)
    assert abs(vals.sum()-(r1.bekerja-r0.bekerja))<1e-6
    for lab,v in zip(['Pertumbuhan PUK','Perubahan partisipasi','Perubahan E/AK'],vals):decomp.append(dict(jenis_kelamin=sex,komponen=lab,orang=v))
dc=pd.DataFrame(decomp).pivot(index='komponen',columns='jenis_kelamin',values='orang')
fig,ax=plt.subplots(figsize=(11,5));bars_pair(ax,dc/1000,'Kontribusi matematis (ribu orang)');ax.axvline(0,color='gray')
finish(fig,'09_dekomposisi_shapley','Perubahan partisipasi paling besar dalam uraian matematis perempuan','Ribu orang; dekomposisi identitas')
view(dc)
note('Dekomposisi',f'Untuk perempuan, komponen PUK bernilai {fmt(dc.loc["Pertumbuhan PUK","Perempuan"],0)} orang, partisipasi {fmt(dc.loc["Perubahan partisipasi","Perempuan"],0)} orang, dan E/AK {fmt(dc.loc["Perubahan E/AK","Perempuan"],0)} orang.',kind='Dekomposisi matematis',limit='Kontribusi menjumlah tepat ke Δ bekerja; bukan bukti sebab-akibat atau estimasi jumlah perempuan yang keluar karena faktor tertentu.')
note('Dekomposisi','Penyusutan jumlah perempuan bekerja tidak dapat dijelaskan dengan menyusutnya PUK perempuan, karena jumlah PUK justru bertambah.',kind='Interpretasi identitas',limit='Tidak membuktikan komposisi umur tetap; perubahan komposisi belum tersedia untuk 2026.')
''')
md('### 8. Posisi Jambi dalam 38 provinsi: level dan perubahan harus dipisahkan')
code('''
hf=hist.query("provinsi!='Indonesia' and periode==@P1 and jenis_kelamin=='Perempuan'").set_index('provinsi')
hm=hist.query("provinsi!='Indonesia' and periode==@P1 and jenis_kelamin=='Laki-laki'").set_index('provinsi')
nf=nat.loc[(P1,'Perempuan')]
rank_plot(hf.tpak,'TPAK perempuan: posisi Jambi terhadap 38 provinsi','10_tpak_perempuan_38_provinsi','Persen PUK perempuan',nf.tpak)
gap=hm.tpak-hf.tpak
rank_plot(gap,'Kesenjangan TPAK laki-laki–perempuan','11_gap_tpak_38_provinsi','Persen poin',nat.loc[(P1,'Laki-laki'),'tpak']-nf.tpak)
rank_plot(hf.epr,'Proporsi PUK perempuan yang bekerja','12_epr_perempuan_38_provinsi','Persen PUK perempuan',nf.epr)
rank_plot(dx[('epr','Perempuan')],'Perubahan EPR perempuan pada 38 provinsi','13_perubahan_epr_perempuan','Persen poin')
note('Pembanding',f'TPAK perempuan Jambi {fmt(f26.tpak)}%, di bawah angka Indonesia {fmt(nf.tpak)}% sebesar {fmt(nf.tpak-f26.tpak)} pp.')
note('Pembanding',f'Kesenjangan TPAK Jambi {fmt(gap.loc["Jambi"])} pp; estimasi titik tertinggi di antara 38 provinsi.',limit='Peringkat deskriptif tanpa uji beda antarprovinsi; belum membuktikan diskriminasi paling tinggi.')
note('Pembanding',f'EPR perempuan Jambi {fmt(f26.epr)}%, sedangkan Indonesia {fmt(nf.epr)}%.',limit='Perbandingan belum disesuaikan struktur umur, urbanisasi, pendidikan, dan komposisi sektor.')
rankchange=int(dx[('epr','Perempuan')].rank(method='min').loc['Jambi'])
note('Pembanding',f'Perubahan EPR perempuan Jambi {fmt(change.loc["Perempuan","epr"])} pp, urutan ke-{rankchange} bila perubahan 38 provinsi diurutkan dari paling negatif.',limit='Urutan perubahan tidak menyatakan signifikansi statistik dan bukan peringkat seluruh mutu pekerjaan.')
''')
md('''
### 9. Kegiatan BAK: bukti sebelum 2026, bukan penjelasan otomatis untuk 2026

Bagian ini sengaja memakai **Februari 2024 dan Februari 2025**. Jumlah BAK Februari 2026 diketahui, tetapi pembagian kegiatan utama BAK menurut gender tahun 2026 belum diperoleh. Karena itu, kenaikan BAK tahun 2026 **tidak langsung disebut akibat pengasuhan, sekolah, ataupun putus asa**.
''')
code('''
act=activity.copy();fig,axes=plt.subplots(1,2,figsize=(12,5))
for ax,sex in zip(axes,SEX):
    s=act.query('jenis_kelamin==@sex').set_index('periode').loc[['2024-02',P0]]
    bottom=np.zeros(2)
    for f,label,color in [('sekolah','Sekolah','#176b83'),('mengurus_rt','Mengurus rumah tangga','#db8d28'),('lainnya','Lainnya','#8e9ba8')]:
        val=s[f]/s.puk*100;ax.bar([LAB[p] for p in s.index],val,bottom=bottom,label=label,color=color);bottom+=val.values
    ax.set_title(sex);ax.set_ylabel('Persen PUK kelompok');ax.set_ylim(0,75);ax.legend(fontsize=8,loc='upper right')
finish(fig,'14_aktivitas_bak_feb2024_2025','Mengurus rumah tangga mendominasi kegiatan BAK perempuan pada 2025','Persen PUK gender',period='Februari 2024–Februari 2025',source='BPS Jambi, tabel 1.1.2–1.1.3')
f_act=act.query("jenis_kelamin=='Perempuan'").set_index('periode');m_act=act.query("jenis_kelamin=='Laki-laki'").set_index('periode')
note('Kegiatan BAK',f'Pada Februari 2025, {fmt(100*f_act.loc[P0,"mengurus_rt"]/f_act.loc[P0,"bak"])}% perempuan di luar AK tercatat berkegiatan utama mengurus rumah tangga; setara {fmt(100*f_act.loc[P0,"mengurus_rt"]/f_act.loc[P0,"puk"])}% PUK perempuan.',limit='Penyebut harus dinyatakan; kegiatan utama BAK tidak mengukur seluruh jam pengasuhan atau seluruh perempuan yang melakukan kerja domestik.')
for f,label in [('sekolah','sekolah'),('mengurus_rt','mengurus rumah tangga'),('lainnya','kegiatan lainnya')]:
    note('Kegiatan BAK',f'Jumlah perempuan BAK pada kategori {label} berubah {fmt(f_act.loc[P0,f]-f_act.loc["2024-02",f],0)} orang pada Feb 2024–2025.',limit='Perubahan sebelum periode utama; tidak boleh dipakai untuk menjelaskan penyusutan pekerja perempuan Feb 2025–2026.')
note('Kegiatan BAK',f'Pada Februari 2025, jumlah laki-laki BAK berkegiatan utama mengurus rumah tangga {fmt(m_act.loc[P0,"mengurus_rt"],0)} orang, perempuan {fmt(f_act.loc[P0,"mengurus_rt"],0)} orang.',limit='Perbedaan dapat memberi arah penelitian pembagian tanggung jawab, tetapi tidak mengidentifikasi hambatan setiap orang.')
''')
md('### 10. Umur: perubahan 2024–2025 dan struktur sebelum penyusutan 2026')
code('''
fig,axes=plt.subplots(1,2,figsize=(14,5))
for ax,sex in zip(axes,SEX):
    for p,col in [('2024-02','#879ba8'),(P0,COL[sex])]:
        g=age.query('jenis_kelamin==@sex and periode==@p').set_index('umur').loc[AGE]
        ax.plot(AGE,g.tpak,'o-',color=col,label=LAB[p])
    ax.set_title(sex);ax.set_ylabel('TPAK (%)');ax.set_ylim(0,100);ax.tick_params(axis='x',rotation=45);ax.legend()
finish(fig,'15_tpak_umur_feb2024_2025','Pola umur berbeda menurut gender sebelum Februari 2026','Persen PUK kelompok umur dan gender',period='Februari 2024–Februari 2025')
af25=age.query("periode==@P0 and jenis_kelamin=='Perempuan'").set_index('umur').loc[AGE]
af24=age.query("periode=='2024-02' and jenis_kelamin=='Perempuan'").set_index('umur').loc[AGE]
age_diff=af25.bekerja-af24.bekerja
fig,ax=plt.subplots(figsize=(10,5));ax.bar(AGE,age_diff/1000,color=np.where(age_diff>=0,'#176b83','#b24f69'));ax.axhline(0,color='gray');ax.set_ylabel('Perubahan perempuan bekerja (ribu orang)')
finish(fig,'16_perubahan_perempuan_bekerja_umur_2024_2025','Kenaikan total pada 2025 juga tidak merata antarumur','Ribu orang',period='Februari 2024–Februari 2025')
fig,ax=plt.subplots(figsize=(11,5));bottom=np.zeros(10)
for f,label,col in [('bekerja','Bekerja','#176b83'),('penganggur','Penganggur','#b24f69'),('sekolah','Sekolah','#9bb5bf'),('mengurus_rt','Mengurus rumah tangga','#db8d28'),('lainnya','Lainnya','#aab1b8')]:
    v=100*af25[f]/af25.puk;ax.bar(AGE,v,bottom=bottom,label=label,color=col);bottom+=v.values
ax.set_ylabel('Persen PUK perempuan pada setiap umur');ax.legend(ncol=3,fontsize=8,loc='upper center',bbox_to_anchor=(.5,1.16))
finish(fig,'17_aktivitas_perempuan_menurut_umur_2025','Aktivitas perempuan berbeda sepanjang kelompok umur','Persen PUK kelompok umur',period='Februari 2025')
note('Umur',f'Pada Februari 2025, TPAK perempuan tertinggi di umur {af25.tpak.idxmax()} ({fmt(af25.tpak.max())}%) dan terendah di umur {af25.tpak.idxmin()} ({fmt(af25.tpak.min())}%).',limit='Pola lintas umur bukan perjalanan perempuan yang sama sepanjang hidup.')
note('Umur',f'Kenaikan perempuan bekerja Feb 2024–2025 terbesar pada umur {age_diff.idxmax()} ({fmt(age_diff.max(),0)} orang); penurunan terbesar pada umur {age_diff.idxmin()} ({fmt(age_diff.min(),0)} orang).',limit='Kelompok yang turun pada 2024–2025 belum tentu kelompok yang turun pada 2025–2026.')
share_youth=100*af25.loc[['15-19','20-24'],'penganggur'].sum()/af25.penganggur.sum()
note('Umur',f'Usia 15–24 menyumbang {fmt(share_youth)}% penganggur perempuan Februari 2025.',limit='Komposisi penganggur bukan tingkat pengangguran usia muda; keduanya memiliki penyebut berbeda.')
prime=af25.loc[['25-29','30-34','35-39','40-44','45-49','50-54']]
note('Umur',f'Pada umur 25–54, {fmt(prime.mengurus_rt.sum(),0)} perempuan berkegiatan utama mengurus rumah tangga di luar AK, sekitar {fmt(100*prime.mengurus_rt.sum()/prime.puk.sum())}% PUK perempuan pada umur tersebut.',limit='Jumlah ini tidak otomatis menyatakan keinginan atau kesiapan bekerja; bukan ukuran cadangan tenaga kerja yang langsung bisa diserap.')
''')
md('### 11. Pendidikan: akses bekerja dan risiko pengangguran perlu dibaca bersama')
code('''
ed25=edu.query('periode==@P0').pivot(index='pendidikan',columns='jenis_kelamin',values='epr').reindex(EDU)
fig,ax=plt.subplots(figsize=(10,5));dumbbell(ax,ed25,'EPR (% PUK pendidikan dan gender)')
finish(fig,'18_epr_pendidikan_gender','Pendidikan tinggi tidak menghapus seluruh kesenjangan akses bekerja','Persen PUK kelompok',period='Februari 2025')
ef=edu.query("jenis_kelamin=='Perempuan'").pivot(index='pendidikan',columns='periode',values='bekerja').reindex(EDU)
ediff=ef[P0]-ef['2024-02']
fig,ax=plt.subplots(figsize=(10,5));ax.barh(EDU,ediff/1000,color=np.where(ediff>=0,'#176b83','#b24f69'));ax.axvline(0,color='gray');ax.set_xlabel('Perubahan (ribu orang)')
finish(fig,'19_perubahan_perempuan_pendidikan','Pertambahan perempuan bekerja pada 2025 berbeda antarpendidikan','Ribu orang',period='Februari 2024–Februari 2025')
etpt=edu.query('periode==@P0').pivot(index='pendidikan',columns='jenis_kelamin',values='tpt').reindex(EDU)
fig,ax=plt.subplots(figsize=(8,5));bars_pair(ax,etpt,'TPT (% AK kelompok pendidikan)')
finish(fig,'20_tpt_pendidikan_gender','TPT perempuan dapat rendah meskipun EPR perempuan rendah','Persen AK kelompok',period='Februari 2025')
note('Pendidikan',f'EPR perempuan universitas Februari 2025 {fmt(ed25.loc["Universitas","Perempuan"])}%, laki-laki {fmt(ed25.loc["Universitas","Laki-laki"])}%.',limit='Perbedaan tidak mengisolasi mutu pendidikan, keterampilan, diskriminasi, atau pilihan kerja.')
note('Pendidikan',f'Perempuan lulusan SMK memiliki TPT {fmt(etpt.loc["SMK","Perempuan"])}%, dibanding laki-laki {fmt(etpt.loc["SMK","Laki-laki"])}% pada Februari 2025.',limit='Sel rinci dapat memiliki ketidakpastian tinggi; RSE pendidikan×gender belum diperoleh. Tidak menarik simpulan kausal atau peringkat pasti.')
note('Pendidikan',f'Pertambahan perempuan bekerja Feb 2024–2025 terbesar pada kelompok {ediff.idxmax()} ({fmt(ediff.max(),0)} orang), sementara penurunan terbesar pada {ediff.idxmin()} ({fmt(ediff.min(),0)} orang).',limit='Komposisi pendidikan berubah; ini bukan pelacakan lulusan yang sama dan bukan bukti kelompok tersebut menjadi sumber penurunan 2026.')
note('Pendidikan','Kategori SD ke bawah pada 2024 disusun dari tidak/belum sekolah, belum tamat SD, dan tamat SD agar sebanding dengan kategori 2025.',kind='Keputusan metodologis',limit='Persentase dihitung ulang dari jumlah orang; tidak merata-ratakan persentase subkelompok.')
''')
md('### 12. Sektor: struktur dan perubahan yang dapat dibandingkan secara sah')
code('''
st=sector.groupby(['periode','jenis_kelamin','sektor'],as_index=False).jumlah.sum()
st['total_bekerja']=st.groupby(['periode','jenis_kelamin']).jumlah.transform('sum');st['persen']=st.jumlah/st.total_bekerja*100
sc25=st.query('periode==@P0').pivot(index='sektor',columns='jenis_kelamin',values='persen').sort_values('Perempuan')
fig,ax=plt.subplots(figsize=(11,8));bars_pair(ax,sc25,'Persen bekerja masing-masing gender')
finish(fig,'21_struktur_sektor_feb2025','Perempuan dan laki-laki terkonsentrasi pada sektor yang berbeda','Persen bekerja gender',period='Februari 2025')
scdiff=st.pivot(index=['sektor','jenis_kelamin'],columns='periode',values='jumlah')
scdiff['delta']=scdiff[P0]-scdiff['2024-02'];scdiff=scdiff.delta.unstack('jenis_kelamin').sort_values('Perempuan')
fig,ax=plt.subplots(figsize=(11,8));bars_pair(ax,scdiff/1000,'Perubahan (ribu orang)');ax.axvline(0,color='gray')
finish(fig,'22_perubahan_sektor_feb2024_2025','Perubahan struktur sebelum 2026: kenaikan dan penurunan sektor','Ribu orang',period='Februari 2024–Februari 2025; KBLI 2020')
duncan=[]
for p in ['2024-02',P0]:
    tmp=st.query('periode==@p').pivot(index='sektor',columns='jenis_kelamin',values='persen')
    duncan.append(dict(periode=p,indeks=.5*abs(tmp['Laki-laki']-tmp['Perempuan']).sum()))
ds=pd.DataFrame(duncan)
fig,ax=plt.subplots(figsize=(8,4));ax.bar(ds.periode.map(LAB),ds.indeks,color=['#8ba3ae','#176b83']);ax.set_ylim(0,100);ax.set_ylabel('Indeks dissimilarity sektor (0–100)')
finish(fig,'23_dissimilarity_sektor','Seberapa berbeda distribusi sektor antara perempuan dan laki-laki?','Indeks 0–100',period='Februari 2024–Februari 2025; KBLI 2020')
note('Sektor',f'Pada Februari 2025, pertanian mencakup {fmt(sc25.loc["Pertanian","Perempuan"])}% perempuan bekerja dan {fmt(sc25.loc["Pertanian","Laki-laki"])}% laki-laki bekerja.',limit='Pangsa dalam gender berbeda dari pangsa perempuan di antara pekerja sektor pertanian.')
note('Sektor',f'Sektor dengan kenaikan perempuan bekerja terbesar Feb 2024–2025 adalah {scdiff.Perempuan.idxmax()} ({fmt(scdiff.Perempuan.max(),0)} orang); penurunan terbesar {scdiff.Perempuan.idxmin()} ({fmt(scdiff.Perempuan.min(),0)} orang).',limit='Perubahan sektor 2024–2025 tidak langsung menjelaskan penurunan total perempuan bekerja tahun 2026.')
note('Sektor',f'Indeks perbedaan distribusi sektor gender berubah dari {fmt(ds.indeks.iloc[0])} menjadi {fmt(ds.indeks.iloc[1])} pada Februari 2024–2025.',kind='Ukuran struktur deskriptif',limit='D = 0,5 × jumlah selisih mutlak pangsa sektor; bukan ukuran diskriminasi atau estimasi efek kebijakan.')
note('Sektor','Perubahan sektor Feb 2025–Feb 2026 tidak dihitung di sini karena KBLI 2020 berubah menjadi KBLI 2025 dan rincian gender 2026 belum diperoleh.',kind='Keputusan metodologis',limit='Perlu tabel korespondensi dan data gender terbaru sebelum membuat kesimpulan sektor penyebab.')
''')
md('### 13. Status pekerjaan: apakah semua tambahan bekerja memiliki bentuk yang sama?')
code('''
ss=status.groupby(['periode','jenis_kelamin','status'],as_index=False).jumlah.sum()
ss['persen']=ss.jumlah/ss.groupby(['periode','jenis_kelamin']).jumlah.transform('sum')*100
fig,ax=plt.subplots(figsize=(12,5))
labels=[('2024-02','Laki-laki'),('2024-02','Perempuan'),(P0,'Laki-laki'),(P0,'Perempuan')]
sp=ss.pivot(index=['periode','jenis_kelamin'],columns='status',values='persen').reindex(pd.MultiIndex.from_tuples(labels))
left=np.zeros(4)
colors=['#176b83','#6aa2af','#e7b966','#db8d28','#8f84a5','#b24f69']
for f,col in zip(sp.columns,colors):ax.barh([LAB[p]+' · '+s for p,s in labels],sp[f],left=left,label=f,color=col);left+=sp[f].values
ax.set_xlim(0,100);ax.set_xlabel('Persen bekerja kelompok')
handles,labs=ax.get_legend_handles_labels()
short={'Berusaha sendiri':'Berusaha sendiri','Buruh/karyawan/pegawai':'Buruh/karyawan','Dibantu buruh tetap':'Dibantu buruh tetap','Dibantu buruh tidak tetap/tidak dibayar':'Dibantu tidak tetap','Pekerja bebas':'Pekerja bebas','Pekerja keluarga/tidak dibayar':'Keluarga/tidak dibayar'}
ax.legend(handles,[short[s] for s in labs],ncol=3,fontsize=8,loc='upper center',bbox_to_anchor=(.5,1.18))
finish(fig,'24_komposisi_status_gender','Pekerja keluarga dan buruh memberi gambaran yang berbeda','Persen bekerja gender',period='Februari 2024–Februari 2025')
family=ss.query("status=='Pekerja keluarga/tidak dibayar'").pivot(index='periode',columns='jenis_kelamin',values='persen')
fig,ax=plt.subplots(figsize=(9,5));bars_pair(ax,family.rename(index=LAB),'Persen bekerja gender')
finish(fig,'25_pekerja_keluarga_gender','Pangsa pekerja keluarga perlu dibaca terpisah dari jumlah bekerja','Persen bekerja gender',period='Februari 2024–Februari 2025')
sf=status.query("periode==@P0 and jenis_kelamin=='Perempuan'").pivot(index='umur',columns='status',values='jumlah').reindex(AGE)
share_family=100*sf['Pekerja keluarga/tidak dibayar']/sf.sum(axis=1)
fig,ax=plt.subplots(figsize=(10,5));ax.bar(AGE,share_family,color=COL['Perempuan']);ax.set_ylabel('Pekerja keluarga / bekerja perempuan pada umur (%)')
finish(fig,'26_pekerja_keluarga_perempuan_umur','Bekerja sebagai pekerja keluarga juga berbeda menurut umur','Persen bekerja perempuan kelompok umur',period='Februari 2025')
note('Status pekerjaan',f'Pangsa pekerja keluarga perempuan Februari 2025 {fmt(family.loc[P0,"Perempuan"])}%, laki-laki {fmt(family.loc[P0,"Laki-laki"])}%.',limit='Pekerja keluarga dihitung bekerja walaupun tanpa upah langsung; bukan bukti otomatis rumah tangganya miskin.')
note('Status pekerjaan',f'Pangsa pekerja keluarga perempuan berubah {fmt(family.loc[P0,"Perempuan"]-family.loc["2024-02","Perempuan"])} pp pada Feb 2024–2025.',limit='Belum menunjukkan perpindahan pekerja keluarga menjadi buruh atau sebaliknya pada orang yang sama.')
bur=ss.query("periode==@P0 and status=='Buruh/karyawan/pegawai'").set_index('jenis_kelamin')
note('Status pekerjaan',f'Pada Februari 2025, buruh/karyawan/pegawai mencakup {fmt(bur.loc["Perempuan","persen"])}% perempuan bekerja dan {fmt(bur.loc["Laki-laki","persen"])}% laki-laki bekerja.',limit='Status buruh tidak menyatakan upah per jam, kepastian kontrak, atau kepesertaan jaminan sosial.')
''')
md('### 14. Konteks Agustus 2024–2025: umur dan kabupaten/kota')
code('''
fig,axes=plt.subplots(1,2,figsize=(14,5))
for ax,sex in zip(axes,SEX):
    for p,col in [('2024-08','#96a8b1'),('2025-08',COL[sex])]:
        g=ageaug.query('periode==@p and jenis_kelamin==@sex').set_index('umur').loc[AGE]
        ax.plot(AGE,g.tpak,'o-',label=LAB[p],color=col)
    ax.set_title(sex);ax.set_ylabel('TPAK (%)');ax.set_ylim(0,100);ax.tick_params(axis='x',rotation=45);ax.legend()
finish(fig,'27_tpak_umur_agustus','Kesenjangan partisipasi usia produktif juga tampak pada Agustus','Persen PUK umur dan gender',period='Agustus 2024–Agustus 2025',source='BPS Analisis Gender Jambi 2024/2025 PDF 34')
r25=reg25.pivot(index='kabupaten_kota',columns='jenis_kelamin',values='epr').sort_values('Perempuan')
fig,ax=plt.subplots(figsize=(10,7));dumbbell(ax,r25,'EPR (% PUK gender wilayah)')
finish(fig,'28_epr_kabupaten_gender_2025','Akses bekerja perempuan berbeda di 11 kabupaten/kota','Persen PUK kelompok',period='Agustus 2025',source='BPS Analisis Gender Jambi 2025 PDF 38; transkripsi visual')
r24=context24.query("indikator=='epr_kabupaten'").copy();r24['kabupaten_kota']=r24.penyebut.str.replace('PUK jenis kelamin di ','',regex=False)
r24=r24.pivot(index='kabupaten_kota',columns='jenis_kelamin',values='nilai')
rd=r25-r24
fig,ax=plt.subplots(figsize=(10,7));bars_pair(ax,rd.sort_values('Perempuan'),'Perubahan EPR (pp)');ax.axvline(0,color='gray')
finish(fig,'29_perubahan_epr_kabupaten_agustus','Perubahan EPR perempuan tidak sama di seluruh daerah Jambi','Persen poin',period='Agustus 2024–Agustus 2025')
note('Kabupaten/kota',f'EPR perempuan Agustus 2025 tertinggi di {r25.Perempuan.idxmax()} ({fmt(r25.Perempuan.max())}%), terendah di {r25.Perempuan.idxmin()} ({fmt(r25.Perempuan.min())}%).',limit='Estimasi subprovinsi pada Agustus, tidak mewakili posisi Februari 2026 dan belum diuji beda statistik.')
rgap=r25['Laki-laki']-r25['Perempuan']
note('Kabupaten/kota',f'Gap EPR Agustus 2025 terbesar di {rgap.idxmax()}, {fmt(rgap.max())} pp; terkecil di {rgap.idxmin()}, {fmt(rgap.min())} pp.',limit='Perbedaan belum disesuaikan struktur umur, pendidikan, dan sektor setiap wilayah.')
note('Kabupaten/kota',f'EPR perempuan meningkat di {int((rd.Perempuan>0).sum())} kabupaten/kota dan menurun di {int((rd.Perempuan<0).sum())} kabupaten/kota pada Agustus 2024–2025.',limit='Jumlah daerah tidak mengukur kontribusi jumlah pekerja tanpa bobot PUK gender tiap daerah.')
note('Kabupaten/kota',f'Perubahan EPR perempuan paling negatif pada Agustus 2024–2025 di {rd.Perempuan.idxmin()}, {fmt(rd.Perempuan.min())} pp.',limit='Tidak menentukan daerah penyumbang penurunan jumlah perempuan bekerja Februari 2026.')
augf=ageaug.query("periode=='2025-08' and jenis_kelamin=='Perempuan'").set_index('umur')
augm=ageaug.query("periode=='2025-08' and jenis_kelamin=='Laki-laki'").set_index('umur')
note('Umur Agustus',f'Pada umur 30–34, TPAK perempuan Agustus 2025 {fmt(augf.loc["30-34","tpak"])}%, laki-laki {fmt(augm.loc["30-34","tpak"])}%.',limit='Beban pengasuhan layak diteliti, tetapi korelasi umur tidak membuktikan alasan tidak bekerja.')
''')
md('### 15. Konteks Agustus 2025: jam kerja, status, dan pemisahan sektor')
code('''
c25=context25.pivot(index='indikator',columns='jenis_kelamin',values='nilai')
c24=context24.query("indikator!='epr_kabupaten'").pivot(index='indikator',columns='jenis_kelamin',values='nilai')
fig,ax=plt.subplots(figsize=(11,5));bars_pair(ax,c25.loc[['pekerja_tidak_penuh','paruh','under','jam_kurang15']].rename(index={'pekerja_tidak_penuh':'Bekerja 1–34 jam','paruh':'Paruh waktu','under':'Setengah pengangguran','jam_kurang15':'Bekerja <15 jam'}),'Persen bekerja gender')
finish(fig,'30_jam_kerja_gender_agustus2025','Jam pendek perempuan lebih tinggi; tidak semuanya kekurangan pekerjaan','Persen bekerja gender',period='Agustus 2025',source='BPS Analisis Gender Jambi 2025 PDF 44,46,47,49')
stable=['berusaha_sendiri','dibantu_tidak_tetap','pekerja_keluarga']
harm=pd.DataFrame({'2024-08':c24.loc[stable].sum(),'2025-08':c25.loc[stable].sum()}).T
harm.loc['2025-08',SEX]=c25.loc['tiga_status_resmi',SEX]
fig,ax=plt.subplots(figsize=(10,4.5));bars_pair(ax,harm.rename(index=LAB),'Persen bekerja gender: tiga status yang sama')
finish(fig,'31_status_harmonis_agustus','Perbandingan status memakai komponen yang sama pada dua tahun','Persen bekerja gender',period='Agustus 2024–Agustus 2025')
sa=secaug.pivot(index='sektor',columns='jenis_kelamin',values='persen').sort_values('Perempuan')
fig,ax=plt.subplots(figsize=(11,8));bars_pair(ax,sa,'Persen bekerja masing-masing gender')
finish(fig,'32_sektor_gender_agustus2025','Konteks sektor terbaru sebelum Februari 2026','Persen bekerja gender',period='Agustus 2025; KBLI 2020',source='BPS Analisis Gender Jambi 2025 PDF 39; transkripsi visual')
note('Jam kerja',f'Pada Agustus 2025, {fmt(c25.loc["pekerja_tidak_penuh","Perempuan"])}% perempuan bekerja 1–34 jam, dibanding {fmt(c25.loc["pekerja_tidak_penuh","Laki-laki"])}% laki-laki.',limit='Jam pendek tidak otomatis bermasalah; perlu dipisahkan paruh waktu dari setengah pengangguran.')
note('Jam kerja',f'Perempuan: paruh waktu {fmt(c25.loc["paruh","Perempuan"])}%, setengah pengangguran {fmt(c25.loc["under","Perempuan"])}%. Laki-laki: masing-masing {fmt(c25.loc["paruh","Laki-laki"])}% dan {fmt(c25.loc["under","Laki-laki"])}%.',limit='Jam pendek perempuan lebih tinggi, tetapi tingkat under laki-laki lebih tinggi pada periode ini. Tidak boleh menganggap semua dimensi perempuan lebih buruk.')
note('Jam kerja',f'Pangsa bekerja <15 jam mencapai {fmt(c25.loc["jam_kurang15","Perempuan"])}% pada perempuan dan {fmt(c25.loc["jam_kurang15","Laki-laki"])}% pada laki-laki.',limit='Tidak mengukur seluruh beban kerja karena kerja domestik dan pengasuhan tanpa bayaran tidak tercakup sebagai jam kerja ekonomi dalam indikator ini.')
note('Status Agustus',f'Tiga status yang sama mencakup {fmt(harm.loc["2025-08","Perempuan"])}% perempuan bekerja pada Agustus 2025, turun sekitar {fmt(harm.loc["2024-08","Perempuan"]-harm.loc["2025-08","Perempuan"])} pp dari Agustus 2024.',limit='Tiga status: berusaha sendiri, dibantu tidak tetap/tidak dibayar, dan pekerja keluarga. Total 2025 resmi; total 2024 penjumlahan komponen dibulatkan. Bukan seluruh informalitas atau ukuran lengkap kelayakan pekerjaan.')
note('Status Agustus',f'Pekerja keluarga perempuan Agustus 2025 {fmt(c25.loc["pekerja_keluarga","Perempuan"])}%, laki-laki {fmt(c25.loc["pekerja_keluarga","Laki-laki"])}%.',limit='Pekerja keluarga tanpa upah langsung berbeda dari perempuan BAK yang mengurus rumah tangga; kedua konsep tidak boleh disamakan.')
note('Sektor Agustus',f'Pada Agustus 2025, pertanian dan perdagangan mencakup {fmt(sa.loc[["Pertanian","Perdagangan"],"Perempuan"].sum())}% perempuan bekerja.',limit='Perlu tabulasi sektor×gender 2026 untuk menentukan apakah sektor-sektor ini menyumbang penurunan tahun berikutnya.')
note('Sektor Agustus',f'Pendidikan mencakup {fmt(sa.loc["Pendidikan","Perempuan"])}% perempuan bekerja, dibanding {fmt(sa.loc["Pendidikan","Laki-laki"])}% laki-laki.',limit='Komposisi sektor tidak menetapkan bahwa perempuan secara bawaan cocok untuk pekerjaan tertentu.')
''')
md('''
### 16. Upah buruh: dimensi pendukung dengan penyebut yang terbatas

Kenaikan rata-rata upah buruh perempuan dapat berlangsung bersamaan dengan penyusutan jumlah seluruh perempuan bekerja. Cakupan keduanya berbeda. Rata-rata juga dapat berubah akibat perubahan komposisi pekerja; data ini belum memastikan setiap pekerja menerima kenaikan upah.
''')
code('''
up=j.loc[[P0,P1]].reset_index().pivot(index='periode',columns='jenis_kelamin',values='upah').rename(index=LAB)
fig,ax=plt.subplots(figsize=(10,4.5));bars_pair(ax,up/1e6,'Rata-rata upah bersih buruh (juta Rp/bulan)')
finish(fig,'33_upah_buruh_gender','Upah melengkapi pembahasan akses kerja, dengan cakupan khusus','Juta rupiah/bulan; nominal')
for sex in SEX:
    note('Upah',f'Upah buruh {sex.lower()} Jambi berubah dari Rp{fmt(b.loc[sex,"upah"],0)} menjadi Rp{fmt(a.loc[sex,"upah"],0)} per bulan, atau {fmt(100*(a.loc[sex,"upah"]/b.loc[sex,"upah"]-1))}% secara nominal.',limit='Buruh/karyawan/pegawai saja; belum dikoreksi inflasi, jam, jenis pekerjaan, pendidikan, dan perubahan komposisi sampel.')
note('Upah',f'Gap kasar upah buruh Februari 2026 adalah {fmt(100*(a.loc["Laki-laki","upah"]-a.loc["Perempuan","upah"])/a.loc["Laki-laki","upah"])}% dari upah laki-laki.',limit='Bukan estimasi diskriminasi upah dan bukan pendapatan rata-rata seluruh pekerja.')
''')
md('''
### 17. Satu Data Jambi: layanan pencari kerja sebagai konteks terpisah

CSV resmi memuat **264 baris**, lengkap untuk 11 kabupaten/kota × 12 bulan × 2 gender pada 2023. Label sumber menyebut pencari kerja yang masuk. Penjumlahan bulan di bawah disebut **catatan pendaftaran tahunan**, karena metadata belum memastikan orang unik atau penanganan pendaftar berulang.

Data ini tidak digunakan sebagai pembilang TPT, tidak dianggap seluruh permintaan kerja, dan tidak menjelaskan perubahan pekerjaan pada Februari 2026. Fungsinya membantu merancang pertanyaan mengenai jangkauan layanan dan kebutuhan audit administrasi.
''')
code('''
assert len(admin)==264
assert not admin.duplicated(['kode_kabupaten_kota','bulan_angka','jenis_kelamin','tahun']).any()
ag=admin.groupby('jenis_kelamin').jumlah.sum().reindex(SEX)
fig,ax=plt.subplots(figsize=(8,4));ax.bar(ag.index,ag,color=[COL[s] for s in ag.index]);ax.set_ylabel('Jumlah catatan pendaftaran')
for i,v in enumerate(ag):ax.text(i,v,fmt(v,0),ha='center',va='bottom')
finish(fig,'34_sdi_pendaftaran_gender','Satu Data: pencatatan pencari kerja didominasi laki-laki','Catatan pendaftaran',period='Jan–Des 2023',source='Disnakertrans, Open Data Jambi; 264 baris CSV')
monthly=admin.groupby(['bulan_angka','jenis_kelamin']).jumlah.sum().unstack().reindex(columns=SEX)
fig,ax=plt.subplots(figsize=(11,5))
for sex in SEX:ax.plot(monthly.index,monthly[sex],'o-',color=COL[sex],label=sex)
ax.set_xticks(range(1,13));ax.set(xlabel='Bulan 2023',ylabel='Catatan pendaftaran per bulan');ax.legend()
finish(fig,'35_sdi_pendaftaran_bulanan','Pendaftaran layanan berfluktuasi sepanjang tahun','Catatan pendaftaran',period='Jan–Des 2023',source='Disnakertrans, Open Data Jambi')
ar=admin.groupby(['kabupaten_kota','jenis_kelamin']).jumlah.sum().unstack().reindex(columns=SEX).sort_values('Perempuan')
fig,ax=plt.subplots(figsize=(11,7));bars_pair(ax,ar,'Catatan pendaftaran tahunan')
finish(fig,'36_sdi_pendaftaran_kabupaten','Jangkauan catatan layanan berbeda antardaerah','Catatan pendaftaran',period='Jan–Des 2023',source='Disnakertrans, Open Data Jambi')
note('Satu Data',f'Terdapat {fmt(ag.sum(),0)} catatan pendaftaran tahun 2023: laki-laki {fmt(ag.loc["Laki-laki"],0)}, perempuan {fmt(ag.loc["Perempuan"],0)}. Pangsa perempuan {fmt(100*ag.loc["Perempuan"]/ag.sum())}%.',limit='Bukan jumlah penganggur atau orang unik yang telah terverifikasi; tidak dibandingkan langsung dengan TPT 2026.')
note('Satu Data',f'Catatan perempuan terbanyak terdapat di {ar.Perempuan.idxmax()} ({fmt(ar.Perempuan.max(),0)} catatan), paling sedikit di {ar.Perempuan.idxmin()} ({fmt(ar.Perempuan.min(),0)} catatan).',limit='Tanpa penyebut penduduk sasaran dan audit pencatatan, angka kecil tidak membuktikan kebutuhan layanan kecil atau akses layanan buruk.')
note('Satu Data',f'Pendaftaran perempuan tertinggi tercatat pada bulan ke-{int(monthly.Perempuan.idxmax())} dengan {fmt(monthly.Perempuan.max(),0)} catatan.',limit='Puncak pendaftaran tidak menjadi bukti musim PHK atau lonjakan pengangguran; bisa dipengaruhi program atau prosedur pencatatan.')
note('Satu Data','Seluruh kombinasi wilayah, bulan, dan gender tersedia dalam CSV; tidak ada kunci duplikat atau jumlah negatif.',kind='Hasil audit data',limit='Kelengkapan struktur bukan jaminan kelengkapan seluruh pencari kerja atau validitas orang unik.')
''')
md('''
### 18. Apa yang dapat dan belum dapat disimpulkan?

| Pernyataan | Penilaian bukti |
|---|---|
| Perempuan bekerja Jambi menyusut pada Feb 2025–2026, laki-laki bertambah | Didukung perubahan estimasi stok BPS |
| Penyusutan perempuan bekerja berlangsung terus setiap tahun | Tidak didukung tiga titik Februari; 2024–2025 justru meningkat |
| Pengangguran turun karena perempuan keluar pasar kerja | Tidak teridentifikasi; kontribusi penurunan penganggur lebih besar pada laki-laki |
| Kenaikan BAK perempuan tahun 2026 disebabkan pengasuhan | Belum teruji; pembagian kegiatan BAK 2026 belum diperoleh |
| Kelompok umur/pendidikan/sektor tertentu menyebabkan penyusutan 2026 | Belum dapat ditentukan dari rincian 2024/2025 |
| Angka pekerja keluarga sama dengan perempuan mengurus rumah tangga | Keliru; yang pertama bekerja secara ekonomi, yang kedua kelompok BAK menurut kegiatan utama |
| Pencari kerja terdaftar sama dengan seluruh penganggur | Keliru; data layanan administratif berbeda dari estimasi survei |
| Perubahan yang diamati signifikan secara statistik | Belum diuji; perlu varians selisih dan informasi rancangan sampel |

**Pendukung eksternal:** kajian [World Bank tentang pengasuhan anak dan pekerjaan perempuan di Indonesia](https://www.worldbank.org/en/country/indonesia/publication/access-to-childcare-can-improve-womens-labor-market-outcomes-in-indonesia) memberi alasan untuk menguji hambatan pengasuhan. Kajian nasional dengan periode berbeda tersebut tidak membuktikan penyebab perubahan Jambi pada 2026. [Bank Indonesia, Laporan Jambi Mei 2026](https://www.bi.go.id/id/publikasi/laporan/lpp/Pages/Laporan-Perekonomian-Provinsi-Jambi-Mei-2026.aspx), memberi konteks bahwa jumlah bekerja total ikut menurun; angka gender tetap merujuk BPS.

Narasi normatif dalam dokumen sumber mengenai kewajiban laki-laki/perempuan atau stereotip kemampuan tidak dijadikan instruksi maupun kesimpulan analisis. Tabulasi angka dan interpretasinya dinilai terpisah.
''')
md('''
### 19. Rencana validasi dan pertanyaan riset lanjutan

| Hipotesis | Data yang perlu diperoleh | Pemeriksaan yang menjawabnya |
|---|---|---|
| Penyusutan terkonsentrasi pada usia tertentu | Sakernas Feb 2026 umur×gender; PUK, AK, bekerja, varians | Perubahan jumlah dan EPR per umur; standardisasi umur |
| Sekolah, pengasuhan, atau kegiatan lain terkait kenaikan BAK | Kegiatan BAK dan alasan tidak mencari/bersedia bekerja menurut gender 2026 | Pisahkan kegiatan utama, alasan, keinginan, kesiapan, dan potensi AK |
| Ada kontraksi sektor yang banyak mempekerjakan perempuan | Sektor×gender Feb 2026 dan korespondensi KBLI | Bandingkan kategori yang benar-benar sepadan; uraikan kontribusi sektor |
| Perubahan hanya fluktuasi sampel/musim | Seri Februari beberapa tahun, bobot, SE dan kovarians survei | Selang selisih; sensitivitas tahun dasar; jangan menyamakan variasi musim dengan tren |
| Hambatan pengasuhan membatasi akses | Usia anak, penggunaan pengasuhan, biaya, waktu domestik, preferensi bekerja | Analisis desain yang dapat menangani seleksi dan faktor perancu |
| Layanan pencari kerja belum menjangkau perempuan | Registrasi terbaru, orang unik, wilayah, sasaran, hasil penempatan | Audit cakupan dan jalur layanan; tidak menggunakan jumlah pendaftar sebagai TPT |

**Prioritas tindakan yang masih berupa usulan:** diagnosis hambatan menurut kelompok; audit jangkauan layanan; penilaian dukungan pengasuhan; dan pencocokan kerja dengan kebutuhan setempat. Data dalam notebook belum mengevaluasi efektivitas program-program tersebut.

**Arah infografis yang paling ditopang bukti:** nasional singkat → penurunan penganggur Jambi → perubahan bekerja dua gender → pelebaran gap partisipasi dan penurunan EPR perempuan → satu konteks Agustus yang paling relevan → ajakan memperbaiki diagnosis serta akses berdasarkan kebutuhan. Hindari memasukkan seluruh grafik ke satu infografis.
''')
md('### 20. Daftar insight, data analisis, dan hasil pemeriksaan')
code('''
note('Kesimpulan','Judul ini didukung untuk perubahan estimasi jumlah perempuan bekerja Jambi Feb 2025–2026. Pesan yang lebih tepat ialah perbaikan pengangguran tidak berarti perkembangan pekerjaan yang sama bagi setiap gender.',kind='Interpretasi terpadu',limit='Gunakan frasa jumlah perempuan bekerja; hindari menyatakan jumlah PHK, penyebab keluar AK, atau tren terus-menerus.')
notes=pd.DataFrame(insights);notes.to_csv(OUT/'daftar_insight.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(figures).to_csv(OUT/'daftar_visualisasi.csv',index=False,encoding='utf-8-sig')
change.to_csv(D/'perubahan_jambi_gender_feb2025_2026.csv',encoding='utf-8-sig')
gd.to_csv(D/'empat_pola_38_provinsi.csv',encoding='utf-8-sig')
dc.to_csv(D/'dekomposisi_shapley.csv',encoding='utf-8-sig')
scdiff.to_csv(D/'perubahan_sektor_feb2024_2025.csv',encoding='utf-8-sig')
rd.to_csv(D/'perubahan_epr_kabupaten_agustus2024_2025.csv',encoding='utf-8-sig')
ar.to_csv(D/'ringkasan_pendaftaran_kabupaten_2023.csv',encoding='utf-8-sig')
lines=['# Pengangguran Turun, Pekerjaan Perempuan Menyusut: Jambi','','Riset 15 Oktober 2026. Periode utama Feb 2025–Feb 2026. Konteks Februari dan Agustus dipisahkan.','',
       '**Kesimpulan utama:** jumlah perempuan bekerja menyusut sementara laki-laki bertambah; penyebab, perpindahan individu, dan signifikansi perubahan belum ditentukan.','']
for section,g in notes.groupby('bagian',sort=False):
    lines+=['## '+section,'']
    for _,r in g.iterrows():lines += [f'- **{r.id} [{r.jenis}]** {r.insight} Batas: {r.batas}']
    lines+=['']
lines+=['## Sumber','']
for _,s in sources.iterrows():lines+=[f"- [{s['id']}: {s['judul']}]({s['url']}) — {s['status']}. {s['batas']}"]
(OUT/'hasil_riset_dan_insight.md').write_text('\\n'.join(lines),encoding='utf-8')
report=dict(jumlah_insight=len(insights),jumlah_visualisasi=len(figures),audit_rekonsiliasi=len(audits),
            baris_panel_gender=len(hist),baris_umur=len(age),baris_pendidikan=len(edu),baris_status=len(status),baris_sektor=len(sector),baris_sdi=len(admin),
            periode_utama='Feb 2025–Feb 2026',rincian_gender_2026_umur_sektor_alasan_bak='Belum diperoleh',klaim_kausal=False)
(OUT/'ringkasan_validasi_data.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
view(notes[['id','bagian','jenis','insight']],n=len(notes))
print(json.dumps(report,ensure_ascii=False,indent=2))
''')

nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'},'title':'Pengangguran Turun, Pekerjaan Perempuan Menyusut: Jambi'})
path=ROOT/'Analisis_Gender_Jambi_Pengangguran_dan_Pekerjaan.ipynb'
nbf.write(nb,path)
print(path,len(cells),'cells')
