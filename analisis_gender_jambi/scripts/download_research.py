from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'
URLS={
  "Jambi_Feb2024.pdf": "https://web-api.bps.go.id/download.php?f=dAbs8NrM0wNfBmJX7uogO2ZQNSswR1pxNld1UWEwUmpIWCtCOGdhQlFGbzQzVmZubmdnSlM1UUZuMzRqZ3lJeHlJUHQvSWloUDI2OUlsdEtKb2J5RDN4UjkvQXp6NTJVcVQyVjF4WFFQLzZDSDFEZDZuN3FtVnFDRTVHTVVMQTEvZGlsTVlnS3RWd0Zjb1dESW1nclJ1dmJyUlVBZERDRmxhcEdQSHVpQkZ6RFVvZFNwdjVrODVmbktoWEdXYXdHOWo3UEptcjBUVEI0VTQwZXdWTm10ZWxQeXJrRHhMa1R6aWJGVWJTWnhlTUN6d1R4eU50eDdnalB4MU5sZ1o5Vkx1RXlVS0VPeFFlbDNyeTZ4a2YyTnlpajBOL3ZtNVhkR1ZEeU93PT0%3D",
  "Jambi_Feb2025.pdf": "https://web-api.bps.go.id/download.php?f=cQO2+CbPh2qHnkme4iTWHGJFQlI1NHIwS3ZoUlBkV0RlS2Q4WTdXUERqQkVVWFlYY28xSUJNUVlHWXVZbHF1SHkwZDluaHd6VTR5RU82R2o3bEpsRW1hbkdXSXRqclhRSXgwcmYwbGdjN0dBV2I1ODFmdEFxSXl3ZWJaY2dQREFHUzVIUFZNeFBLMXVCTjNTSmhCRmNLaTBqaHRzWjByQ2tXYjBCZDBYQVczbU9xZDRYUVBxZ2tJRjVZbmd3QW5ONDM5S1cxV3ZOSkp4dkFRYlhkRjkyZGg4c2Jnem94cDhielNyTVZkbE1JWW5CV1lEcWhNSFFKYXRoT0YraWpKQzdWdGhvaVFTQ1BGWkZoOWxuMTBYdGloK25FbW9YMkJ6ZDF6RVV3PT0%3D",
  "Analisis_Gender_Jambi_2024.pdf": "https://web-api.bps.go.id/download.php?f=lblbBGWhH8yG3DUYa5XoZXZRbHdlR2F0Y2RTai95dnlLQk1kN2VTelhzUnc4QmJXaUl1YmVicU1mUDB1MWkwQUpWUHd6YklKckZaZFpmcmxzUEJFM2tjdVd0amdPV29TZWhwN29YallRcEtXQmJLTXhHZFNoUTNKcnhyTUZQZjBkM3JjaXRVVGFLNkoybTFvQjNic2RURDM2ZFJJWk9YMlQ3ajY1Q0ZLN3BHNVhzMEE2VUN4dWZxcWUxczNCbVEvMmtBQlRXaHUwNldiaFVPSkx2WDZnZVZyQm05ZGxzVmlJSkJtVi9BYkVwclZpTmJhTEpweXM5QVZuTm85VVVBZ1RWc3hpNVozK0g3a1VKYUg%3D",
  "Analisis_Gender_Jambi_2025.pdf": "https://web-api.bps.go.id/download.php?f=Fj1JgrdjRqMKpsQ2KuqkITlSM25kQlFPYWg4TXR4WWpZbWlmZm8vVFFPNlFOREkvZkhDNEpCcWFqSFJWNzhmNUpaNkxZNE5KUlBIUUdJNFRWWHZNYjNpY2RYcVkwVU1uMW5jQ0Vmanl2eG5qZ1ZxTGxvRkgrM0o4ejlxTzhtRUVySzcxREN4a291VS9scWR1T2ZwKzVHb2lYMHhFWEhQV3BNSTAvN3d3blJRYnRoU25GcHVNWmpHK3BuS0R3OHVSTXVtRDlYZ25BMzBHK2RKNXRCaXZ5UTByRUdNT0dWNS91bG1yT2c0OG5OdHduTlBnNWNEOGx0TkxRS29wZVA1WWx2VEZ3RDFoMFkxL2pWNDM%3D"
}

def download(item):
    name,url=item
    path=RAW/name
    if path.exists() and path.read_bytes()[:4]==b'%PDF':
        print(name,'tersedia',path.stat().st_size,flush=True)
        return
    part=RAW/(name+'.part')
    result=subprocess.run(['curl.exe','-L','--max-time','45','--connect-timeout','10','-sS','-A','Mozilla/5.0','-o',str(part),url],capture_output=True,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if result.returncode==0 and part.exists() and part.read_bytes()[:4]==b'%PDF':
        part.replace(path)
        print(name,'diunduh',path.stat().st_size,flush=True)
    else:
        print(name,'gagal',result.returncode,result.stderr[:140],flush=True)
        part.unlink(missing_ok=True)

if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(download,URLS.items()))
