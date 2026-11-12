from pathlib import Path
import gzip
import shutil

pasta = Path(__file__).resolve().parents[1] / 'data'
for arquivo in pasta.glob('*.gz'):
    destino = arquivo.with_suffix('')
    with gzip.open(arquivo, 'rb') as origem, destino.open('wb') as saida:
        shutil.copyfileobj(origem, saida)
    print('Restaurado:', destino.name)
