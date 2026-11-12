# Integração do dashboard do 2º trimestre de 2026

## Escopo

Documento fornecido pelo usuário: Dashboard Completo ResolveBairro - 2º Trimestre (1).pdf. Arquivo preservado integralmente em dashboard_2_trimestre_2026.pdf, com duas páginas. Inclusão autorizada no projeto e no repositório pelo pedido de integração.

O painel principal ganhou um acesso para app/dashboard_2trimestre.html. A página permite ler o PDF, abrir em nova aba e baixar, com alternativa para navegadores sem leitor embutido. Trata-se de relatório estático, não de um dashboard conectado ao banco.

## Separação das fontes

O PDF declara como base arquivo-final-2-trim-26.csv. A base verificável versionada neste repositório é do 1º trimestre de 2026, com outro recorte de serviços. O CSV do 2º trimestre e o notebook de origem do relatório não foram fornecidos nesta integração. Não é possível confirmar os números, as categorias, a origem dos bairros ou os resultados dos modelos a partir do PDF isoladamente. Nenhum número do PDF foi importado para o banco nem para os indicadores calculados.

## Conferências necessárias

- A soma de Finalizados na tabela por bairro é 52.621; o resumo apresenta 52.593 (diferença de 28).
- O consolidado por bairro soma 6.655 registros Em Aberto; o resumo apresenta backlog de 6.350. Além da diferença numérica, deve-se esclarecer o tratamento de cancelamentos na tabela.
- Os MAEs apresentados (baseline, Ridge e Random Forest) são resultados declarados pelo documento; precisam ser reproduzidos com notebook executado, corte temporal e conjunto de teste preservado. A base atual não oferece comprovação desses resultados.
- Confirmar a unidade territorial: o documento alterna bairros e distritos, enquanto a base SP156 utilizada no projeto fornece distrito.
- Confirmar o significado de resolução: finalização administrativa não comprova solução efetiva ou satisfação do cidadão.

O PDF não foi corrigido nem recebeu conteúdo novo. A página de integração apresenta essas limitações e conserva os indicadores do painel atual como um conjunto separado.
