# Detecção de fraudes bancárias com Machine Learning

Projeto conceitual de estudo e portfólio de [azenhasoft](https://github.com/azenhasoft).

A ideia é estudar como um modelo em Python pode sinalizar transações suspeitas para análise. Eu uso dados fictícios, comparo dois modelos e avalio quantas fraudes eles conseguem encontrar e quantos alarmes falsos geram.

**Este projeto não usa dados de clientes, não tem vínculo com uma instituição financeira e não foi validado para uso bancário.** Os resultados mostram o comportamento do modelo dentro da simulação.

## O problema

Uma transação de valor alto pode ser legítima. Uma transação pequena pode ser fraude. Por isso, eu considero vários sinais juntos, como horário, frequência de transações, dispositivo e favorecido novo.

O modelo recebe esses sinais e gera um score. Quando o score ultrapassa o limiar escolhido, a transação é encaminhada para análise. O projeto não bloqueia pagamentos nem confirma fraude automaticamente.

## O que está implementado

- Geração reproduzível de 20 mil transações fictícias, com fraude como classe minoritária.
- Validação das entradas e divisão cronológica em treino, validação e teste.
- Tratamento de valores ausentes, padronização numérica e codificação de categorias dentro de um pipeline.
- Comparação entre Regressão Logística e Random Forest, com pesos para lidar com o desbalanceamento.
- Escolha do modelo por average precision na validação e ajuste do limiar por F2.
- Comparação com um baseline que sempre prevê transação legítima.
- Relatórios, gráficos, modelo salvo e previsão em novas transações.
- Testes automatizados e workflow para GitHub Actions.

## Como executar

Use o terminal na pasta em que este README está. As bibliotecas estão fixadas nas versões usadas no experimento de referência. A execução foi verificada em Python 3.12; o workflow está configurado para Python 3.13.

O projeto declara Python 3.11 ou superior, mas isso não garante que as versões fixadas das bibliotecas funcionem em toda versão futura do Python. Se o `pip` tentar compilar bibliotecas ou avisar que não existe versão compatível, use um ambiente Python compatível com essas dependências. Não é necessário substituir o Python que você já usa em outros projetos.

### Windows / PowerShell

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m fraude executar
```

### Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m fraude executar
```

Os caminhos acima usam o Python do ambiente diretamente, então não é preciso ativar o ambiente. No VS Code, selecione esse mesmo interpretador em **Python: Select Interpreter**. Nos comandos seguintes, `python` representa o interpretador desse ambiente.

### Executar cada etapa

```bash
python -m fraude gerar --linhas 20000
python -m fraude treinar
python -m fraude prever --dados exemplos/novas_transacoes.csv
python -m unittest discover -s tests -v
```

Também é possível escolher os caminhos:

```bash
python -m fraude treinar --dados dados/transacoes.csv --saida resultados
python -m fraude prever --dados exemplos/novas_transacoes.csv --modelo resultados/modelo.joblib --saida resultados/novas_previsoes.csv
```

Não é preciso criar conta, baixar uma base externa ou configurar credenciais. O comando `executar` recria os arquivos gerados nos caminhos padrão. Copie os resultados antes de rodar novamente se quiser guardar uma execução anterior.

## Como eu organizei o experimento

As datas são separadas em aproximadamente 60% para treino, 20% para validação e 20% para teste. Transações com a mesma data e hora ficam na mesma divisão. O tamanho exato pode variar um pouco.

O treino é usado para ajustar os modelos e o tratamento dos dados. Na validação, eu escolho o modelo com maior average precision e o limiar com maior F2. Se houver empate no F2, uso o maior limiar. O teste só é usado depois dessas decisões.

Eu não retreino com a validação depois de escolher o limiar. Isso mantém o mesmo modelo que produziu os scores usados no ajuste. Se eu retreinasse, precisaria reservar outro período para revisar esse limiar.

Os campos `id_transacao`, `data_hora` e `fraude` não entram como variáveis no modelo. O horário entra separadamente como `hora`. Nenhuma variável usa informações de transações futuras.

## Por que não olhar só para a acurácia?

Se quase todas as transações forem legítimas, um modelo que sempre responda “legítima” pode ter acurácia alta e não encontrar nenhuma fraude. Eu mantenho esse baseline no relatório para deixar o problema visível.

| Medida | O que eu observo |
| --- | --- |
| Precision | Entre os alertas, quantos eram fraudes simuladas? |
| Recall | Entre as fraudes simuladas, quantas foram sinalizadas? |
| F2 | Combina precision e recall, com maior peso para recall. |
| Average precision (AP) | Resume a relação entre precision e recall ao variar o limiar. |
| ROC-AUC | Avalia a ordenação dos scores entre as classes. |
| Taxa de alertas | Qual parte das transações seria enviada para análise? |
| Falsos positivos | Quantas transações legítimas geraram alerta? |
| Falsos negativos | Quantas fraudes passaram sem alerta? |

Average precision não é a mesma conta que a área trapezoidal sob a curva precision-recall. Neste projeto, o código usa `average_precision_score` do scikit-learn.

Escolher F2 é uma hipótese de estudo, não uma decisão operacional pronta. Em um cenário real, eu precisaria definir o custo de deixar uma fraude passar, o impacto de um alarme falso e a quantidade de casos que a equipe consegue revisar.

## Resultados

Os números são calculados quando o projeto é executado. Uma execução de referência está em [docs/resultado_referencia.md](docs/resultado_referencia.md).

| Arquivo gerado em `resultados/` | Conteúdo |
| --- | --- |
| `resumo.md` | Relatório para leitura, com os gráficos. |
| `metricas.json` | Métricas, versões, períodos e comparação dos modelos. |
| `matriz_confusao.png` | Acertos e erros no teste. |
| `curva_precision_recall.png` | Relação entre precision e recall. |
| `previsoes_teste.csv` | Scores e alertas das transações de teste. |
| `novas_previsoes.csv` | Resultado dos exemplos sem rótulo. |
| `modelo.joblib` | Pipeline e limiar usados na previsão. |

`score_fraude` é uma saída do classificador, entre 0 e 1. Como os modelos usam pesos de classe e não passaram por calibração, eu não interpreto um score de 0,80 como “80% de chance real de fraude”. `enviar_para_analise = 1` significa apenas que o score atingiu o limiar.

Os exemplos EX001 a EX004 não têm fraude confirmada. Eles servem para demonstrar a entrada e a saída, inclusive um valor ausente.

## Estrutura

| Caminho | Responsabilidade |
| --- | --- |
| `fraude/dados.py` | Gerar, validar e separar os dados. |
| `fraude/modelo.py` | Treinar, avaliar e prever. |
| `fraude/relatorio.py` | Gerar gráficos e resumo. |
| `fraude/__main__.py` | Receber os comandos do terminal. |
| `exemplos/novas_transacoes.csv` | Entradas fictícias para previsão. |
| `tests/test_projeto.py` | Verificar comportamento e pontos de falha. |
| `docs/conceito.md` | Escopo, hipóteses e evolução do projeto. |
| `docs/dicionario_dados.md` | Definição dos campos. |
| `docs/roteiro_estudo.md` | Ordem sugerida para estudar e explicar o código. |
| `.github/workflows/testes.yml` | Testes e execução reduzida no GitHub Actions. |

## Limitações

O gerador define relações artificiais entre os sinais e os rótulos. Os modelos aprendem essas relações, então os resultados não demonstram que eles funcionariam com transações reais. Também não basta variar a semente para validar essa aplicação.

A simulação não possui clientes recorrentes, disputas de transações, atraso na confirmação das fraudes ou mudanças de comportamento ao longo do tempo. A divisão por data demonstra o procedimento, mas não simula esses problemas. Os campos de frequência e distância são gerados diretamente, sem histórico real.

Não há busca de hiperparâmetros, calibração de scores, explicação individual dos alertas, API, monitoramento contínuo ou integração bancária. São extensões possíveis depois de validar o fluxo básico.

Um uso real exigiria dados autorizados, rótulos confiáveis e avaliação fora desta simulação. Também seria necessário verificar qualidade por canal, acompanhar mudança de comportamento e testar a operação em modo de observação antes de tomar decisões sobre pagamentos.

Carregue arquivos `.joblib` somente de origem confiável: esse formato pode executar código ao ser aberto. O modelo deve ser recriado a partir do código nas versões registradas. Bases reais, credenciais e modelos gerados ficam fora do Git por padrão.

## Referências técnicas

- [scikit-learn: vazamento de dados e boas práticas](https://scikit-learn.org/stable/common_pitfalls.html)
- [scikit-learn: pipelines e ColumnTransformer](https://scikit-learn.org/stable/modules/compose.html)
- [scikit-learn: average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
- [scikit-learn: ajuste do limiar de decisão](https://scikit-learn.org/stable/modules/classification_threshold.html)

## Autoria e preparação

Portfólio: [github.com/azenhasoft](https://github.com/azenhasoft).

Este projeto foi elaborado com apoio de IA para estruturar o código e a documentação. A proposta é executar, revisar e entender cada etapa antes de apresentar o trabalho como parte do meu portfólio. Não representa experiência comprovada em implantação de um sistema antifraude.

Repositório: [azenhasoft/fraude-bancaria-ml](https://github.com/azenhasoft/fraude-bancaria-ml). O [roteiro de publicação](docs/publicar_github.md) fica como referência para outras cópias do projeto.
