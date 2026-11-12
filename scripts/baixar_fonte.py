from pathlib import Path
import hashlib
from urllib.request import urlopen

URL = "https://dados.prefeitura.sp.gov.br/dataset/0aecfa2b-aa3a-40d4-8183-0d4351b7fd0a/resource/75105148-4efd-48f3-8ae0-fc6c2adf7060/download/arquivo-final-1-trim-26.csv"
EXPECTED = "5305b2b13630b05bdd396a5c3e1185cd7d952eec681e07eed957868783e7aa21"
target = Path(__file__).resolve().parents[1] / "data/raw/original.csv"
target.parent.mkdir(parents=True, exist_ok=True)
temporary = target.with_suffix(".part")
digest = hashlib.sha256()
with urlopen(URL, timeout=180) as response, temporary.open("wb") as output:
    while chunk := response.read(1024 * 1024):
        output.write(chunk)
        digest.update(chunk)
if digest.hexdigest() != EXPECTED:
    raise ValueError("A fonte mudou. Arquivo .part preservado; revise o recorte antes de atualizar o projeto.")
temporary.replace(target)
print("Fonte oficial baixada e SHA-256 verificado:", target)
