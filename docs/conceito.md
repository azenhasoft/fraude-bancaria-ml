# Conceito do projeto

## Objetivo

Estudar classificação supervisionada para sinalizar transações que precisam de revisão. A unidade de análise é uma transação. O rótulo é `fraude`, com 0 para legítima e 1 para fraude simulada.

O problema de negócio é equilibrar fraudes detectadas e alarmes falsos. O projeto implementa a etapa de pontuação, sem bloquear transações e sem movimentar dinheiro.

## Hipóteses da simulação

Eu considero que horário, valor, frequência recente, distância, idade da conta, canal e novidade de dispositivo ou favorecido estão disponíveis na hora da transação.

O gerador calcula uma propensão artificial e sorteia o rótulo. Isso mantém sobreposição entre as classes: transações com sinais de risco podem ser legítimas e transações sem sinais fortes podem receber rótulo de fraude. A prevalência varia com o tamanho da base e a semente, sem balanceamento forçado.

O canal é incluído no contrato, mas não participa da fórmula de propensão. Ele funciona como uma variável candidata sem relação causal definida pelo gerador. Não devo assumir que todas as variáveis incluídas ajudam o modelo.

Não são simulados clientes, redes de favorecidos ou sequências reais. Portanto, eu não consigo medir desempenho por cliente ou generalização para clientes novos.

## Fluxo implementado

1. Gerar a base ou ler um CSV com o contrato definido.
2. Validar identificadores, rótulos, campos e datas.
3. Separar períodos sem sobreposição: treino, validação e teste.
4. Ajustar os pipelines somente no treino.
5. Comparar os modelos e escolher o limiar na validação.
6. Avaliar o modelo escolhido no teste reservado.
7. Salvar o pipeline, o limiar, as versões e os relatórios.
8. Aplicar o mesmo tratamento às novas transações.

O tratamento numérico preenche ausências pela mediana e padroniza os valores. O categórico preenche pela categoria mais frequente e usa one-hot encoding. Categorias novas de canal são ignoradas pelo encoder; isso evita erro de execução, mas exige monitoramento em uma aplicação real. Os campos binários só aceitam `sim`, `nao` ou ausência.

A Random Forest não depende da padronização. Eu mantenho o mesmo tratamento nos dois pipelines para simplificar a comparação com a Regressão Logística. Os pesos de classe aumentam a atenção da função de treinamento à classe minoritária; não criam novos exemplos de fraude nem garantem melhor desempenho.

## O que mudaria em uma aplicação real

Primeiro eu definiria com a área responsável o que conta como fraude confirmada e quando esse rótulo fica disponível. Uma contestação ainda em análise não deveria virar fraude confirmada automaticamente. A extração histórica precisaria respeitar a informação disponível no momento da transação.

Para a frequência em uma hora, eu contaria somente transações anteriores à atual. Para dispositivo e favorecido, consultaria o histórico anterior à decisão. Distância precisaria de uma definição consistente e não poderia usar a posição de uma transação futura. Também reservaria tempo para maturação dos rótulos antes de avaliar um período.

Depois, compararia o modelo com regras já usadas e reservaria períodos futuros para avaliação. Se houver clientes recorrentes, a estratégia de separação deve refletir se o objetivo é prever novas transações de clientes conhecidos ou generalizar para clientes novos.

O limiar dependeria do volume diário de alertas e do custo dos erros. F2 não substitui essa análise. Scores usados como probabilidades exigiriam avaliação de calibração em dados representativos e separados.

A integração poderia receber a transação, montar os sinais com histórico anterior, gerar o score e enviar o caso para uma fila de revisão. A confirmação humana alimentaria uma base de rótulos com rastreabilidade. Esse fluxo é apenas uma proposta: não está implementado no projeto.

Antes de qualquer uso operacional, eu avaliaria permissões de acesso, tratamento de dados, revisão dos alertas, recuperação em falhas e monitoramento. Também acompanharia volume de alertas, qualidade por canal, atraso dos rótulos e mudança na distribuição das variáveis. Esses pontos exigem decisões técnicas e da instituição que não podem ser inferidas desta simulação.
