# ResolveBairro

Projeto CitizenTech da equipe Bug Hunters para a Global Solution FIAP 2026. Analisa solicitações de zeladoria urbana do SP156 de São Paulo para apoiar transparência, manutenção de infraestrutura e comparação territorial, em alinhamento aos ODS 9 e 11.

## O que está disponível

- Base pública real com 81.350 registros de quatro serviços de tapa-buracos e resíduos, abertos entre 01/01 e 31/03/2026.
- Painel HTML com indicadores e comparação por distrito e serviço.
- Banco SQLite e exportações CSV para análise e integração.
- Scripts Python reproduzíveis para baixar a fonte oficial e preparar a base.
- Base de 72.168 registros finalizados com duração válida, preparada para futuros experimentos de regressão.

O projeto está na etapa de preparação de dados e visualização. Não há modelo treinado/validado, API, autenticação, envio à prefeitura ou alertas automáticos nesta versão. Dados simulados das versões anteriores não fazem parte deste repositório.

## Como visualizar

Os CSVs completos e o banco SQLite são distribuídos sem perda em arquivos `.gz`. Na raiz do projeto, execute `python scripts/descompactar_dados.py` para restaurá-los antes de acessar os links de dados do painel ou abrir o banco. O painel em si pode ser aberto imediatamente.

Baixe ou clone o repositório e abra `app/index.html` no navegador. O painel é estático e usa os indicadores reais embutidos no HTML. Ele não recebe novos chamados nem consulta a prefeitura em tempo real.

Opcionalmente, na raiz do projeto:

```sh
python -m http.server 8000
```

Acesse http://localhost:8000/app/ . O banco para integração está em `data/resolvebairro_real.sqlite`.

## Indicadores do recorte

| Indicador | Valor |
|---|---:|
| Solicitações registradas | 81.350 |
| Finalizadas | 72.168 (88,71%) |
| Pendentes no snapshot | 8.354 |
| Canceladas | 828 |
| Tempo médio até finalização | 8,64 dias corridos |

Status histórico: o portal informa extração em 07/08/2026. Finalização administrativa não comprova que o cidadão teve seu problema resolvido. Distrito não equivale a bairro. Os indicadores se referem exclusivamente ao recorte selecionado, não a todos os serviços da cidade.

Prazo oficial, satisfação, MAE e risco de atraso permanecem sem valor quando não há dados ou modelo avaliado. Repetições no mesmo ponto são apenas candidatas, sem comprovação de reincidência. Consulte as definições completas em [metodologia](docs/metodologia.md).

## Estrutura

```text
app/index.html                   Painel dos ODS 9 e 11
data/chamados_reais.csv           Registros operacionais tratados
data/base_ml_real.csv             Base para experimentos supervisionados
data/resolvebairro_real.sqlite    Banco relacional
data/indicadores*                 Indicadores gerais e territoriais
data/fontes_e_metodologia.json    Origem, recorte e hash da fonte
docs/metodologia.md               Dicionário, critérios e limitações
docs/arquitetura.md               Fluxo atual e próximos componentes
scripts/baixar_fonte.py           Download verificado da fonte oficial
scripts/preparar_base_real.py     Tratamento e geração dos artefatos
```

## Reproduzir a preparação

Python 3.11 ou superior. Os scripts usam somente a biblioteca padrão; não é necessário instalar pacotes. Na raiz:

```sh
python scripts/baixar_fonte.py
python scripts/preparar_base_real.py
```

A fonte original tem aproximadamente 119 MiB e fica fora do Git. O SHA-256 é conferido antes de substituir o arquivo local: se a prefeitura republicar a base, o download será preservado como `.part` e será necessária revisão. A preparação regenera os arquivos em `data/`, inclusive uma versão completa em JSON e um painel em `data/painel_ODS9_11.html`. O painel publicado em `app/index.html` é o snapshot versionado; atualize-o conscientemente ao mudar a fonte. A data de preparação nos metadados identifica esta versão, não o horário atual de execução.

## Arquitetura e Machine Learning

Fonte SP156 → download com verificação → tratamento em Python → SQLite/CSV → indicadores → painel HTML. Veja [arquitetura](docs/arquitetura.md).

Alvo proposto: dias entre abertura e finalização administrativa. Preditores candidatos: serviço, distrito e calendário da abertura. Não usar status final, data de finalização ou informações futuras como entrada. Em cada corte de treino, apenas rótulos já conhecidos naquela data podem participar. A comparação de modelos e a validação temporal ainda precisam ser executadas; este repositório não apresenta métricas preditivas.

## ODS e uso responsável

- **ODS 9 — Indústria, inovação e infraestrutura:** apoio à análise de manutenção da infraestrutura, associado à meta 9.1.
- **ODS 11 — Cidades e comunidades sustentáveis:** gestão participativa e acompanhamento de demandas de resíduos, associados às metas 11.3 e 11.6.

São relações propostas pelo projeto, não indicadores oficiais da ONU nem comprovação de impacto. A base publicada omite endereços, coordenadas, nomes, contatos e texto livre. IDs são referências técnicas à linha de origem, não protocolos oficiais. Diferenças entre distritos exigem análise de composição de serviços, acesso ao canal e amostras pequenas.

## Fontes

- [SP156 — Portal de Dados Abertos de São Paulo](https://dados.prefeitura.sp.gov.br/dataset/dados-do-sp156)
- [ODS 9 — ONU](https://sdgs.un.org/goals/goal9)
- [ODS 11 — ONU](https://sdgs.un.org/goals/goal11)

Dados públicos atribuídos à Prefeitura de São Paulo. Nenhuma licença nova sobre os dados de terceiros é concedida por este repositório; consulte os termos da fonte.
