from pathlib import Path
import ast
import os
import sys
import json
import asyncio
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from jupyter_client.kernelspec import KernelSpecManager

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'Analisis_TPT_Rendah_Kecukupan_Pekerjaan.ipynb'
nb=nbformat.read(path,as_version=4)
for i,c in enumerate(nb.cells):
    if c.cell_type=='code':
        ast.parse(c.source,filename=f'cell_{i}')
if sys.platform=='win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
specdir=ROOT/'outputs'/'kernel_temp'
specdir.mkdir(exist_ok=True)
(specdir/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'ACTION research Python','language':'python'}),encoding='utf-8')
manager=KernelSpecManager()
kernel_name='action2026-research'
manager.install_kernel_spec(str(specdir),kernel_name=kernel_name,user=True,replace=True)
try:
    client=NotebookClient(nb,timeout=240,kernel_name=kernel_name,resources={'metadata':{'path':str(ROOT)}})
    client.execute()
    nbformat.write(nb,path)
finally:
    manager.remove_kernel_spec(kernel_name)
    (specdir/'kernel.json').unlink(missing_ok=True)
    specdir.rmdir()
errors=[(i,o) for i,c in enumerate(nb.cells) if c.cell_type=='code' for o in c.get('outputs',[]) if o.output_type=='error']
assert not errors, errors
assert all(c.execution_count is not None for c in nb.cells if c.cell_type=='code')
images=sum('image/png' in o.get('data',{}) for c in nb.cells for o in c.get('outputs',[]))
assert images==26,images
exporter=HTMLExporter(template_name='lab')
body,_=exporter.from_notebook_node(nb)
(ROOT/'Analisis_TPT_Rendah_Kecukupan_Pekerjaan.html').write_text(body,encoding='utf-8')
report={'code_cells':sum(c.cell_type=='code' for c in nb.cells),'error_outputs':len(errors),'embedded_images':images,'execution_complete':True,'python':sys.version.split()[0]}
(ROOT/'outputs/notebook_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
