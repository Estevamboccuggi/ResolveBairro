# ResolveBairro — dados públicos reais | ODS 9 e 11

## Fonte e recorte
Prefeitura de São Paulo, SP156: https://dados.prefeitura.sp.gov.br/dataset/dados-do-sp156
Download direto: https://dados.prefeitura.sp.gov.br/dataset/0aecfa2b-aa3a-40d4-8183-0d4351b7fd0a/resource/75105148-4efd-48f3-8ae0-fc6c2adf7060/download/arquivo-final-1-trim-26.csv
Preparação: 11/11/2026. Município assumido: São Paulo, por disponibilidade de fonte pública compatível com o produto.
Arquivo identificado como 1º trimestre de 2026. Aberturas efetivamente encontradas no recorte: 2026-01-01 a 2026-03-31. Fonte com 577,989 linhas; recorte com 81,350. O portal informa extração em 07/08/2026; o status não representa uma consulta em tempo real. O arquivo original permanece disponível no link e seu SHA-256 consta nos metadados. Sem amostragem aleatória ou geração de valores.

Serviços incluídos: Tapa-buraco, Tapa-buraco em faixa exclusiva ou corredor de ônibus, Entulho e grandes objetos em via pública - solicitar remoção, Denunciar descarte irregular de entulho e outros resíduos em área pública. Não foram incluídas denúncias de caçambas nem descarte em flagrante, por não serem equivalentes ao recorte escolhido. Iluminação pública não foi encontrada e não foi criada artificialmente.

## Arquivos
- chamados_reais.csv / dados_reais.json / resolvebairro_real.sqlite: mesma base inicial em três formatos.
- indicadores.csv / indicadores.json: valores calculáveis e justificativas para os indisponíveis.
- indicadores_territoriais.csv: distrito e serviço, contagens, média e mediana dos tempos, tamanho da amostra.
- base_ml_real.csv: apenas finalizadas com duração válida. Alvo: tempo_finalizacao_dias.
- painel_ODS9_11.html: painel local de leitura dos indicadores reais.
- fontes_e_metodologia.json: origem, recorte e rastreabilidade.

## Significado e limites
Este pacote substitui a simulação como fonte de dados, mas não altera o HTML anterior nem oferece sincronização. O painel incluso usa indicadores embutidos e não aceita novos chamados. Para integrar o aplicativo, carregue dados_reais.json ou use SQLite no backend. IDs SP156-2026T1-L correspondem à linha do CSV, não são protocolos oficiais. Não foram inventados histórico, prazos, previsões ou avaliações. Não se deduplicou por semelhança: a fonte não fornece protocolo para provar duplicação.

Finalizada é um encerramento administrativo. Percentual finalizado = finalizadas / todas, incluindo canceladas no denominador. Pendentes = Aberto + Em Andamento. Canceladas não são tratadas como resolvidas nem pendentes. Tempo = data de finalização menos data de abertura, em dias corridos, apenas finalizadas e datas válidas; 0 registros com problemas de datas sinalizados. Mesmo dia resulta em zero dias por granularidade da fonte. Distrito é a unidade disponível; não foi renomeado como bairro. Registros sem distrito ficam em NÃO INFORMADO.

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
