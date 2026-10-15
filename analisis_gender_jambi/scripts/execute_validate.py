from pathlib import Path
import ast
import asyncio
import json
import sys
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from jupyter_client.kernelspec import KernelSpecManager

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'Analisis_Gender_Jambi_Pengangguran_dan_Pekerjaan.ipynb'
nb=nbformat.read(path,as_version=4)
for i,c in enumerate(nb.cells):
    if c.cell_type=='code':ast.parse(c.source,filename=f'cell_{i}')
    if c.cell_type=='markdown':assert '\x0c' not in c.source and '\t' not in c.source,(i,'Unexpected control character')
if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
spec=ROOT/'outputs/kernel_temp'
spec.mkdir(exist_ok=True)
(spec/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Jambi research Python','language':'python'}),encoding='utf-8')
ksm=KernelSpecManager()
name='action2026-jambi-gender-research'
assert name not in ksm.find_kernel_specs(),'Temporary kernel name already exists; inspect before replacing.'
ksm.install_kernel_spec(str(spec),kernel_name=name,user=True)
try:
    NotebookClient(nb,timeout=240,kernel_name=name,resources={'metadata':{'path':str(ROOT)}}).execute()
    nbformat.write(nb,path)
except Exception:
    nbformat.write(nb,ROOT/'outputs/execution_diagnostic.ipynb')
    raise
finally:
    ksm.remove_kernel_spec(name)
    (spec/'kernel.json').unlink(missing_ok=True)
    spec.rmdir()
errors=[(i,o.ename) for i,c in enumerate(nb.cells) for o in c.get('outputs',[]) if o.output_type=='error']
assert not errors,errors
assert all(c.execution_count is not None for c in nb.cells if c.cell_type=='code')
images=sum('image/png' in o.get('data',{}) for c in nb.cells for o in c.get('outputs',[]))
assert images==36,images
body,_=HTMLExporter(template_name='lab').from_notebook_node(nb)
path.with_suffix('.html').write_text(body,encoding='utf-8')
report={'code_cells':sum(c.cell_type=='code' for c in nb.cells),'error_outputs':len(errors),'embedded_figures':images,'execution_complete':True,'python':sys.version.split()[0]}
(ROOT/'outputs/notebook_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2),flush=True)
