from pathlib import Path
import struct,zipfile,json
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'data/raw/KEMENDAGRI_WFS_ZIP.zip'
with zipfile.ZipFile(path) as z:
    shp=next(n for n in z.namelist() if n.lower().endswith('.shp'))
    dbf=next(n for n in z.namelist() if n.lower().endswith('.dbf'))
    with z.open(shp) as f:header=f.read(100)
    with z.open(dbf) as f:dh=f.read(32)
    shape_type=struct.unpack('<i',header[32:36])[0]
    records=struct.unpack('<I',dh[4:8])[0]
    out={'source':'Kemendagri WFS, resource dari katalog SDI_GEOMETRI','zip':str(path.relative_to(ROOT)).replace('\\','/'),'shape_type':shape_type,'geometry_type':{3:'Polyline',5:'Polygon',13:'PolylineZ',15:'PolygonZ'}.get(shape_type,'Lainnya'),'dbf_records':records,'usable_as_polygon':shape_type in [5,15,25],'status':'DITOLAK sebagai polygon choropleth; sumber ternyata berupa segmen garis batas' if shape_type not in [5,15,25] else 'Perlu audit atribut dan wilayah sebelum join','files':z.namelist()}
(ROOT/'data/processed/audit_geometri_sdi.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=True,indent=2))
