# Referências técnicas

Estas fontes ajudam a entender as decisões de implementação. Elas não validam os resultados da simulação para uso bancário.

- [scikit-learn: riscos comuns e vazamento de dados](https://scikit-learn.org/stable/common_pitfalls.html) — cuidados para evitar que informações do teste influenciem o treinamento.
- [scikit-learn: composição de estimadores e pipelines](https://scikit-learn.org/stable/modules/compose.html) — uso de pipelines e `ColumnTransformer` para tratar variáveis numéricas e categóricas.
- [scikit-learn: `average_precision_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html) — definição da métrica usada para comparar os modelos na validação.
- [scikit-learn: ajuste do limiar de decisão](https://scikit-learn.org/stable/modules/classification_threshold.html) — escolha de limiar conforme o objetivo da classificação.

## Como essas fontes se relacionam com o projeto

O tratamento dos dados fica dentro de cada pipeline, ajustado no treino. A divisão cronológica reserva períodos posteriores para validação e teste. O modelo é escolhido pela average precision na validação, e o limiar é selecionado pelo F2 nesse mesmo período.

Essas escolhas organizam o experimento. Não substituem validação com dados representativos, rótulos confiáveis e critérios operacionais definidos para um contexto real.
