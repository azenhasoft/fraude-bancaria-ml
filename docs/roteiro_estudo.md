# Roteiro para estudar e explicar o projeto

Eu começaria executando `python -m fraude executar`. Depois abriria `resultados/resumo.md` e `resultados/novas_previsoes.csv` para ver a saída antes de entrar nos detalhes do código.

## Ordem de leitura

1. `exemplos/novas_transacoes.csv`: entender o que entra no modelo.
2. `fraude/dados.py`: localizar as variáveis, a simulação do rótulo e a divisão por data.
3. `fraude/modelo.py`: seguir o pipeline, o treinamento e a escolha do limiar.
4. `fraude/relatorio.py`: conferir como os resultados são apresentados.
5. `tests/test_projeto.py`: entender os erros que os testes tentam evitar.

## Perguntas que eu preciso conseguir responder

**Por que usar dados fictícios?** Para estudar o fluxo sem depender de dados bancários. Isso limita o que eu posso concluir sobre o desempenho.

**Qual a diferença entre treino, validação e teste?** O treino ajusta o modelo. A validação ajuda a escolher modelo e limiar. O teste reservado avalia a escolha final.

**Por que o tratamento fica dentro do pipeline?** Para que os valores usados para preencher e padronizar os dados sejam aprendidos no treino, sem consultar a validação ou o teste.

**O que acontece quando eu baixo o limiar?** Mais transações podem virar alerta. Posso encontrar mais fraudes, mas também aumentar os alarmes falsos e o trabalho de revisão.

**Por que comparar dois modelos?** A Regressão Logística é uma referência mais simples. A Random Forest consegue representar outras relações. Eu comparo as saídas sem presumir qual vai ganhar.

**Um score alto confirma fraude?** Não. O modelo sinaliza uma prioridade de análise dentro da simulação, e o score não foi calibrado como probabilidade real.

**O que falta para usar em um banco?** Dados autorizados e representativos, rótulos confirmados, validação temporal, análise de custos, integração e monitoramento. Este projeto não executa essas etapas operacionais.

## Experimentos para fazer depois

Altere uma coisa por vez e anote o motivo. Compare F1 com F2 na validação. Observe como mudam precision, recall e a taxa de alertas. Depois experimente remover uma variável e refazer o treino.

Se eu usar o teste repetidamente para decidir mudanças, ele deixa de ser uma avaliação independente. Para um novo ciclo de decisões, eu precisaria reservar outro conjunto de teste.

Uma descrição curta para apresentar o trabalho:

> Eu montei um estudo em Python para sinalizar possíveis fraudes em transações fictícias. Comparei Regressão Logística e Random Forest, separei os dados por data e escolhi o limiar na validação. O foco foi entender fraudes detectadas e alarmes falsos. Ainda é uma simulação, sem integração bancária.

Use essa descrição depois de executar e revisar o projeto, ajustando qualquer parte que não corresponda ao que você já entendeu.
