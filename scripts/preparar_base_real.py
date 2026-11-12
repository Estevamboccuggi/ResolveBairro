import csv, json, sqlite3, hashlib, statistics, zipfile, html
from pathlib import Path
from datetime import datetime, date
from collections import Counter, defaultdict
from bisect import bisect_left

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'; OUT.mkdir(parents=True,exist_ok=True)
SOURCE='https://dados.prefeitura.sp.gov.br/dataset/0aecfa2b-aa3a-40d4-8183-0d4351b7fd0a/resource/75105148-4efd-48f3-8ae0-fc6c2adf7060/download/arquivo-final-1-trim-26.csv'
PORTAL='https://dados.prefeitura.sp.gov.br/dataset/dados-do-sp156'
original=ROOT/'data/raw/original.csv'
mapping={'Tapa-buraco':'Buraco na via','Tapa-buraco em faixa exclusiva ou corredor de ônibus':'Buraco na via', 'Entulho e grandes objetos em via pública - solicitar remoção':'Resíduos em via pública','Denunciar descarte irregular de entulho e outros resíduos em área pública':'Descarte irregular'}
def dt(value):
    if not value.strip(): return None
    try:return datetime.strptime(value.strip(),'%d/%m/%Y').date().isoformat()
    except ValueError:return None
def dump(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def csvout(name,items):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(items[0])); w.writeheader(); w.writerows(items)
rows=[]; total=0; invalid=0; statuses=Counter(); all_dates=[]; pairs=defaultdict(list)
with original.open(encoding='cp1252',newline='') as f:
    for line,x in enumerate(csv.DictReader(f,delimiter=';'),start=2):
        total+=1
        if x['Serviço'] not in mapping:continue
        opened,closed=dt(x['Data de Abertura']),dt(x['Data de Finalização'])
        days=(date.fromisoformat(closed)-date.fromisoformat(opened)).days if opened and closed else None
        anomaly=not opened or bool(x['Data de Finalização'].strip() and not closed) or (days is not None and days<0)
        if anomaly: invalid+=1
        valid_final=x['Status']=='Finalizada' and days is not None and days>=0
        row=dict(id_registro=f'SP156-2026T1-L{line}',linha_fonte=line,
          categoria=mapping[x['Serviço']],servico_original=x['Serviço'],distrito=x['Distrito'].strip() or None,
          subprefeitura=x['Prefeitura Operacional'].strip() or None,canal=x['Meio de Comunicação'],
          aberto_em=opened,finalizado_em=closed,status_original=x['Status'],
          tempo_finalizacao_dias=days if valid_final else None,
          prazo_oficial_dias=None,finalizado_no_prazo=None,satisfacao=None,previsao_dias=None,risco_atraso=None,
          repeticao_candidata_90d=False,qualidade_datas='REVISAR' if anomaly else 'OK',origem='SP156/PMSP - dado público real')
        rows.append(row);statuses[row['status_original']]+=1
        if x['Logradouro'].strip() and x['Número'].strip() and row['distrito'] and opened:
            key=(x['Logradouro'].strip().casefold(),x['Número'].strip().casefold(),row['distrito'],x['Serviço'])
            pairs[key].append(row)
# Não publica endereços ou coordenadas. Somente sinaliza repetição compatível com a regra.
for group in pairs.values():
    group.sort(key=lambda r:(r['aberto_em'],r['linha_fonte']))
    finishes=sorted(r['finalizado_em'] for r in group if r['tempo_finalizacao_dias'] is not None)
    for r in group:
        index=bisect_left(finishes,r['aberto_em'])-1
        last_finish=finishes[index] if index>=0 else None
        if last_finish and 0<(date.fromisoformat(r['aberto_em'])-date.fromisoformat(last_finish)).days<=90:
            r['repeticao_candidata_90d']=True
resolved=[r for r in rows if r['tempo_finalizacao_dias'] is not None]
pending=[r for r in rows if r['status_original'] in ('Aberto','Em Andamento')]
dates=[r['aberto_em'] for r in rows if r['aberto_em']]
metrics=[
 dict(indicador='Total de chamados no recorte',valor=len(rows),unidade='registros',situacao='CALCULADO',ods='9;11',metodo='Quantidade de linhas dos quatro serviços selecionados; sem deduplicação por ausência de protocolo.'),
 dict(indicador='Solicitações finalizadas',valor=round(100*statuses['Finalizada']/len(rows),2),unidade='%',situacao='CALCULADO',ods='9;11',metodo='Status Finalizada / todos os registros. Não comprova solução efetiva.'),
 dict(indicador='Tempo médio até finalização',valor=round(statistics.mean(r['tempo_finalizacao_dias'] for r in resolved),2),unidade='dias corridos',situacao='CALCULADO',ods='9;11',metodo='Finalização menos abertura; somente Finalizada com datas válidas e duração não negativa.'),
 dict(indicador='Chamados pendentes',valor=len(pending),unidade='registros',situacao='CALCULADO',ods='9;11',metodo='Status Aberto ou Em Andamento no snapshot publicado; não situação atual.'),
 dict(indicador='Finalização dentro do prazo',valor=None,unidade='%',situacao='INDISPONÍVEL',ods='9;11',metodo='Sem prazo oficial por serviço e versão temporal na fonte selecionada.'),
 dict(indicador='Chamados por distrito',valor=len({r['distrito'] for r in rows if r['distrito']}),unidade='distritos identificados',situacao='CALCULADO',ods='11',metodo='Contagens detalhadas em indicadores_territoriais.csv; distrito não equivale a bairro.'),
 dict(indicador='MAE do modelo',valor=None,unidade='dias',situacao='NÃO AVALIADO',ods='9',metodo='Exige treinamento e previsões fora da amostra; não há modelo avaliado neste pacote.'),
 dict(indicador='Satisfação dos cidadãos',valor=None,unidade='%',situacao='INDISPONÍVEL',ods='11',metodo='Não consta no CSV de solicitações selecionado. Avaliação do canal não equivale à satisfação com a resolução.'),
 dict(indicador='Risco de atraso',valor=None,unidade='probabilidade',situacao='NÃO AVALIADO',ods='9;11',metodo='Exige prazo de referência, modelo e validação; nenhum risco foi inventado.'),
 dict(indicador='Reincidência confirmada',valor=None,unidade='registros',situacao='INDISPONÍVEL',ods='11',metodo='Sem identificador persistente do problema, não é possível confirmar reincidência.'),
 dict(indicador='Novos registros no mesmo ponto após finalização',valor=sum(r['repeticao_candidata_90d'] for r in rows),unidade='candidatos',situacao='PROXY',ods='11',metodo='Mesmo serviço, logradouro, número e distrito; nova abertura 1 a 90 dias depois de finalização anterior. Não confirma mesmo problema.'),
 dict(indicador='Diferenças territoriais',valor=None,unidade='dias',situacao='DESCRITIVO',ods='11',metodo='Compare tempos por distrito E serviço no arquivo territorial. Diferenças não demonstram discriminação nem causalidade.')]
territories=[];groups=defaultdict(list)
for r in rows:groups[(r['distrito'] or 'NÃO INFORMADO',r['servico_original'])].append(r)
for (district,service),g in sorted(groups.items()):
    values=[r['tempo_finalizacao_dias'] for r in g if r['tempo_finalizacao_dias'] is not None]
    territories.append(dict(distrito=district,servico=service,total=len(g),finalizadas=sum(r['status_original']=='Finalizada' for r in g),pendentes=sum(r['status_original'] in ('Aberto','Em Andamento') for r in g),canceladas=sum(r['status_original']=='Cancelada' for r in g),n_tempos_validos=len(values),media_dias=round(statistics.mean(values),2) if values else None,mediana_dias=statistics.median(values) if values else None,amostra_pequena=len(values)<30))
csvout('chamados_reais.csv',rows);csvout('indicadores.csv',metrics);csvout('indicadores_territoriais.csv',territories)
ml=[dict(id_registro=r['id_registro'],categoria=r['categoria'],servico=r['servico_original'],distrito=r['distrito'],aberto_em=r['aberto_em'],finalizado_em=r['finalizado_em'],mes=date.fromisoformat(r['aberto_em']).month,dia_semana=date.fromisoformat(r['aberto_em']).weekday(),tempo_finalizacao_dias=r['tempo_finalizacao_dias']) for r in resolved]
csvout('base_ml_real.csv',ml)
meta=dict(fonte=PORTAL,download=SOURCE,sha256_original=hashlib.sha256(original.read_bytes()).hexdigest(),data_preparacao='2026-11-11',origem='REAL',municipio='São Paulo/SP',periodo_aberturas=[min(dates),max(dates)],snapshot='Portal declara extração em 2026-08-07; não representa o estado atual.',linhas_fonte=total,linhas_recorte=len(rows),servicos_incluidos=mapping,problemas_datas=invalid,status=dict(statuses),observacoes=['IDs são chaves técnicas por linha de origem, não protocolos oficiais.','Não foram criados eventos intermediários nem dados pessoais.','Finalização administrativa não é comprovação de resolução efetiva.','Iluminação pública não encontrada neste recorte; não foram fabricados chamados dessa categoria.','Indicadores operacionais associados aos ODS, não indicadores oficiais da ONU.'])
dump('fontes_e_metodologia.json',meta);dump('indicadores.json',dict(metadata=meta,indicadores=metrics,territorios=territories));dump('dados_reais.json',dict(metadata=meta,chamados=rows))
dbpath=OUT/'resolvebairro_real.sqlite'
if dbpath.exists():dbpath.unlink()
con=sqlite3.connect(dbpath)
con.execute('CREATE TABLE chamados ('+','.join('"'+k+'" '+('INTEGER PRIMARY KEY' if k=='linha_fonte' else 'REAL' if k in ['tempo_finalizacao_dias','prazo_oficial_dias','finalizado_no_prazo','satisfacao','previsao_dias','risco_atraso'] else 'INTEGER' if k=='repeticao_candidata_90d' else 'TEXT') for k in rows[0])+')')
con.executemany('INSERT INTO chamados VALUES ('+','.join('?' for _ in rows[0])+')',[tuple(r.values()) for r in rows]);con.execute('CREATE UNIQUE INDEX idx_id ON chamados(id_registro)');con.execute('CREATE INDEX idx_distrito ON chamados(distrito,servico_original)')
con.execute("CREATE VIEW fila_pendente AS SELECT * FROM chamados WHERE status_original IN ('Aberto','Em Andamento')")
con.execute('CREATE VIEW treinamento AS SELECT id_registro,categoria,servico_original,distrito,aberto_em,finalizado_em,tempo_finalizacao_dias FROM chamados WHERE tempo_finalizacao_dias IS NOT NULL')
con.execute('CREATE TABLE metadados (chave TEXT PRIMARY KEY, valor TEXT)');con.executemany('INSERT INTO metadados VALUES (?,?)',[(k,json.dumps(v,ensure_ascii=False)) for k,v in meta.items()]);con.commit()
assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert con.execute('SELECT COUNT(*) FROM chamados').fetchone()[0]==len(rows)
assert all(r['tempo_finalizacao_dias']>=0 for r in resolved)
assert len({r['id_registro'] for r in rows})==len(rows)
con.close()
readme=f'''# ResolveBairro — dados públicos reais | ODS 9 e 11

## Fonte e recorte
Prefeitura de São Paulo, SP156: {PORTAL}
Download direto: {SOURCE}
Preparação: 11/11/2026. Município assumido: São Paulo, por disponibilidade de fonte pública compatível com o produto.
Arquivo identificado como 1º trimestre de 2026. Aberturas efetivamente encontradas no recorte: {min(dates)} a {max(dates)}. Fonte com {total:,} linhas; recorte com {len(rows):,}. O portal informa extração em 07/08/2026; o status não representa uma consulta em tempo real. O arquivo original permanece disponível no link e seu SHA-256 consta nos metadados. Sem amostragem aleatória ou geração de valores.

Serviços incluídos: {', '.join(mapping)}. Não foram incluídas denúncias de caçambas nem descarte em flagrante, por não serem equivalentes ao recorte escolhido. Iluminação pública não foi encontrada e não foi criada artificialmente.

## Arquivos
- chamados_reais.csv / dados_reais.json / resolvebairro_real.sqlite: mesma base inicial em três formatos.
- indicadores.csv / indicadores.json: valores calculáveis e justificativas para os indisponíveis.
- indicadores_territoriais.csv: distrito e serviço, contagens, média e mediana dos tempos, tamanho da amostra.
- base_ml_real.csv: apenas finalizadas com duração válida. Alvo: tempo_finalizacao_dias.
- painel_ODS9_11.html: painel local de leitura dos indicadores reais.
- fontes_e_metodologia.json: origem, recorte e rastreabilidade.

## Significado e limites
Este pacote substitui a simulação como fonte de dados, mas não altera o HTML anterior nem oferece sincronização. O painel incluso usa indicadores embutidos e não aceita novos chamados. Para integrar o aplicativo, carregue dados_reais.json ou use SQLite no backend. IDs SP156-2026T1-L correspondem à linha do CSV, não são protocolos oficiais. Não foram inventados histórico, prazos, previsões ou avaliações. Não se deduplicou por semelhança: a fonte não fornece protocolo para provar duplicação.

Finalizada é um encerramento administrativo. Percentual finalizado = finalizadas / todas, incluindo canceladas no denominador. Pendentes = Aberto + Em Andamento. Canceladas não são tratadas como resolvidas nem pendentes. Tempo = data de finalização menos data de abertura, em dias corridos, apenas finalizadas e datas válidas; {invalid} registros com problemas de datas sinalizados. Mesmo dia resulta em zero dias por granularidade da fonte. Distrito é a unidade disponível; não foi renomeado como bairro. Registros sem distrito ficam em NÃO INFORMADO.

## ODS
ODS 9, meta 9.1: a análise da manutenção viária apoia decisões sobre infraestrutura confiável e acesso equitativo.
ODS 11, metas 11.3 e 11.6: transparência dos registros apoia gestão participativa e acompanhamento das demandas por resíduos. Relação proposta pelo projeto; os KPIs não são os indicadores oficiais da ONU nem demonstram causalmente impacto nos ODS.
Referências: https://sdgs.un.org/goals/goal9 e https://sdgs.un.org/goals/goal11

## Indicadores sem suporte
Cumprimento de prazo exige tabela oficial de prazos por serviço válida na data do chamado e regras de dias úteis/corridos. Satisfação exige pesquisa de resultado do serviço; avaliações de canal não são equivalentes. MAE e risco de atraso exigem modelos treinados e avaliação fora da amostra. Campos ausentes permanecem nulos, nunca zero.

Reincidência confirmada não é identificável. O campo repeticao_candidata_90d indica uma nova abertura do mesmo serviço no mesmo logradouro/número/distrito, de 1 a 90 dias após finalização anterior, quando os campos estão preenchidos. Pode refletir erro, outro problema no mesmo local ou novo pedido. Não comprova retorno do defeito. Apenas essa sinalização derivada é publicada, sem os endereços usados para calculá-la.

Diferenças territoriais são descritivas. Compare o mesmo serviço, observe amostras pequenas e pendências. Muitos chamados podem representar maior acesso ao canal; poucos não significam poucos problemas. Não há denominador populacional para taxas por habitante.

## Machine Learning
Entradas: serviço/categoria, distrito, mês e dia da semana da abertura. Excluir identificadores, status final, finalizado_em e qualquer variável conhecida depois da abertura. Datas de finalização servem ao alvo e à disponibilidade do rótulo: em cada corte temporal só usar no treino chamados já finalizados até o corte. Preservar teste futuro e ajustar transformações apenas no treino. Avaliar MAE/RMSE por serviço e distrito; treinar só com finalizados pode favorecer atendimentos rápidos. A coluna órgão não foi incluída porque pode mudar depois da abertura. Nenhum resultado de modelo foi inventado.

## Dados e validação
Dados públicos tratados sem nomes, contatos, texto livre, coordenadas e endereços no produto final. Datas, serviço, canal e território preservados da fonte; chaves técnicas e métricas derivadas identificadas. UTF-8 com BOM nos CSV, separador vírgula, datas ISO. Conferidos contagens, unicidade das chaves, integridade SQLite e durações não negativas da base ML.
'''
(OUT/'LEIA-ME.md').write_text(readme,encoding='utf-8')
cards=''.join('<article><h2>'+html.escape(m['indicador'])+'</h2><strong>'+('Indisponível' if m['valor'] is None else str(m['valor']).replace('.',','))+'</strong> '+html.escape(m['unidade'])+'<p>'+html.escape(m['metodo'])+'</p><small>ODS '+html.escape(m['ods'])+' · '+html.escape(m['situacao'])+'</small></article>' for m in metrics)
table=''.join('<tr>'+''.join('<td>'+html.escape(str(r[k]) if r[k] is not None else '—')+'</td>' for k in ['distrito','servico','total','pendentes','n_tempos_validos','media_dias','mediana_dias'])+'</tr>' for r in territories)
page='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ResolveBairro | ODS 9 e 11 | Dados reais</title><style>body{font:16px/1.6 system-ui;margin:0;background:#f1f5f4;color:#142b3b}header{background:#142b3b;color:white;padding:28px}main{max-width:1200px;margin:auto;padding:24px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px}article{background:white;border:1px solid #b7cbc7;border-radius:10px;padding:20px}h2{font-size:19px}strong{font-size:28px;color:#08665c}small{color:#3d5955}.notice{background:#fff0c9;padding:18px;margin-bottom:20px}.scroll{overflow:auto;max-height:650px}table{border-collapse:collapse;background:white;width:100%}th,td{border-bottom:1px solid #ddd;padding:12px;text-align:left}th{position:sticky;top:0;background:#dcebe6}a{color:#08665c}</style><header><h1>ResolveBairro · ODS 9 e 11</h1><p>Infraestrutura urbana e cidades sustentáveis | São Paulo · SP156</p></header><main><div class="notice">Dados públicos reais. Recorte de solicitações, não de todos os problemas da cidade. Status histórico: não é uma consulta em tempo real. Finalização não comprova resolução percebida pelo cidadão.</div><p>Fonte: <a href="'''+PORTAL+'''">Portal de Dados Abertos de São Paulo</a>. Aberturas no recorte: '''+min(dates)+' a '+max(dates)+'''. Consulte a metodologia antes de comparar territórios.</p><div class="cards">'''+cards+'''</div><h2>Comparação territorial por serviço</h2><p>Médias e medianas em dias corridos, somente finalizadas com duração válida. Menos de 30 observações exige cautela. Distrito não equivale a bairro; diferenças não comprovam desigualdade causal de atendimento.</p><div class="scroll"><table><caption>Todos os distritos e serviços do recorte; campos ausentes preservados.</caption><thead><tr><th>Distrito</th><th>Serviço</th><th>Total</th><th>Pendentes</th><th>N tempos válidos</th><th>Média dias</th><th>Mediana dias</th></tr></thead><tbody>'''+table+'''</tbody></table></div><p><a href="LEIA-ME.md">Metodologia</a> · <a href="chamados_reais.csv">CSV real</a> · <a href="indicadores_territoriais.csv">Indicadores territoriais</a></p></main></html>'''
(OUT/'painel_ODS9_11.html').write_text(page,encoding='utf-8')
print('Base regenerada em data/. Consulte data/LEIA-ME.md; o painel regenerado fica em data/painel_ODS9_11.html.')
