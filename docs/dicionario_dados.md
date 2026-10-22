# Dicionário dos dados

Cada linha representa uma transação fictícia. O CSV usa vírgula como separador, ponto decimal e codificação UTF-8. Os nomes das colunas não têm acentos para facilitar o uso no código.

| Coluna | Tipo | Definição e momento de disponibilidade |
| --- | --- | --- |
| `id_transacao` | texto | Identificador único. Obrigatório no treino; opcional na previsão. Não entra no modelo. |
| `data_hora` | data/hora | Momento da transação, usado na separação temporal. Obrigatório no treino; não entra no modelo. |
| `valor` | número ≥ 0 | Valor fictício em reais, conhecido na solicitação. |
| `hora` | inteiro de 0 a 23 | Hora da transação no referencial do conjunto. |
| `transacoes_1h` | inteiro ≥ 0 | Quantidade fictícia de transações anteriores na última hora; exclui a atual. |
| `distancia_km` | número ≥ 0 | Distância fictícia até a localização de referência já conhecida. |
| `idade_conta_dias` | inteiro ≥ 0 | Idade da conta na hora da solicitação. |
| `canal` | texto | Canal, como `pix`, `cartao` ou `transferencia`. Novas categorias são aceitas. |
| `dispositivo_novo` | `sim` / `nao` | Se o dispositivo ainda não era conhecido antes da transação. |
| `favorecido_novo` | `sim` / `nao` | Se não havia histórico anterior com o favorecido. |
| `fraude` | inteiro 0 / 1 | Rótulo simulado. Obrigatório no treino; não é entrada na previsão. |

As oito variáveis do modelo precisam existir no CSV, mesmo quando uma célula está vazia. O pipeline trata células ausentes. Cada variável precisa ter pelo menos um valor observado em cada divisão do experimento; uma coluna totalmente vazia indica falha de dados e interrompe o treino.

Datas do gerador são uma linha do tempo fictícia em UTC. Na validação de entrada, datas sem fuso são interpretadas como UTC. A coluna `hora` deve estar alinhada com o mesmo referencial. Em uma base real, a conversão de fuso e o cálculo de `hora` precisariam acontecer antes da entrada no projeto; essa consistência não é verificada automaticamente.

Os identificadores não são CPF, número de conta ou qualquer dado pessoal. Frequência e distância são sorteadas no gerador, sem reconstrução de histórico. As definições acima descrevem como esses sinais seriam interpretados, não uma implementação de consulta bancária.

Na saída, `score_fraude` é um score não calibrado. `enviar_para_analise` recebe 1 quando o score é maior ou igual ao limiar salvo. Não é rótulo confirmado.
