# Detecção de fraudes bancárias com Machine Learning

Projeto de estudo e portfólio em Python. Eu simulei transações bancárias e construí um fluxo que compara modelos de classificação para sinalizar casos que poderiam seguir para análise.

**O projeto não usa dados de clientes, não bloqueia transações e não foi validado para uso bancário.** Os resultados abaixo vêm de dados sintéticos e mostram apenas o comportamento do experimento.

## O problema

Fraudes são uma classe rara: um modelo pode acertar quase todas as transações legítimas e ainda deixar passar as fraudes. Por isso, avaliei quantas fraudes o modelo sinaliza e quantos alertas falsos ele gera, em vez de olhar apenas para a acurácia.

## O que eu construí

- Geração reproduzível de 20 mil transações fictícias.
- Separação cronológica em treino, validação e teste, sem misturar períodos.
- Pipeline de preparação dos dados e comparação entre Regressão Logística e Random Forest.
- Seleção do modelo por average precision e ajuste do limiar por F2 na validação.
- Relatórios, gráficos, previsão de novas transações, testes automatizados e workflow no GitHub Actions.

## Resultado de referência

Na execução registrada, a Random Forest foi selecionada na validação. No teste reservado, encontrou 17 das 46 fraudes simuladas e gerou 72 alertas falsos.

| Medida no teste | Resultado |
| --- | ---: |
| Fraudes sinalizadas (recall) | 17 de 46 (36,96%) |
| Precision | 19,10% |
| Transações enviadas para análise | 2,23% |
| F2 | 0,3114 |
| Average precision | 0,1238 |

O baseline que sempre prevê “legítima” teve 98,85% de acurácia e não encontrou nenhuma fraude. Isso mostra por que a acurácia, sozinha, não descreve bem esse problema. Os números também deixam claro que este experimento ainda tem muitos erros e não representa desempenho em transações reais.

Detalhes, gráficos e condições da execução estão em [docs/resultado_referencia.md](docs/resultado_referencia.md).

## Como executar

Use Python 3.12 e o terminal na pasta do projeto.

**Windows / PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m fraude executar
```

**Linux / macOS**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m fraude executar
```

A execução de referência foi registrada no Python 3.12.14. O workflow automatizado roda em Python 3.13. As dependências estão fixadas em `requirements.txt`.

O comando `executar` gera os dados, treina os modelos e grava os relatórios em `resultados/`. Para rodar as etapas separadamente ou gerar previsões com o CSV de exemplo:

```bash
python -m fraude gerar --linhas 20000
python -m fraude treinar
python -m fraude prever --dados exemplos/novas_transacoes.csv
python -m unittest discover -s tests -v
```

## O que sai da execução

Em `resultados/`, o projeto grava métricas em JSON, um resumo em Markdown, gráficos, previsões de teste, previsões para novas transações e o pipeline treinado. O campo `score_fraude` não é uma probabilidade calibrada; o alerta indica apenas que o score atingiu o limiar escolhido.

## Documentação

- [Conceito, hipóteses e possíveis próximos passos](docs/conceito.md)
- [Resultado de referência e gráficos](docs/resultado_referencia.md)
- [Dicionário dos dados](docs/dicionario_dados.md)
- [Roteiro para estudar e explicar o projeto](docs/roteiro_estudo.md)
- [Referências técnicas](docs/referencias_tecnicas.md)

O repositório também inclui [testes](tests/) e o workflow de [integração contínua](.github/workflows/testes.yml).

## Autoria

Projeto de estudo de [azenhasoft](https://github.com/azenhasoft). Foi elaborado com apoio de IA para estruturar código e documentação; estou revisando e estudando cada etapa antes de apresentá-lo como parte do meu portfólio. Não representa experiência de implantação de um sistema antifraude.
