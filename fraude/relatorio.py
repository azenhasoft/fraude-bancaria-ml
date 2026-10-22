"""Saídas para interpretar o experimento."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, PrecisionRecallDisplay


def criar_graficos(y, scores, limiar, pasta):
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(y, scores >= limiar,
        display_labels=["Legítima", "Fraude"], ax=ax, colorbar=False)
    ax.set(title="Teste com dados sintéticos", xlabel="Previsão", ylabel="Rótulo simulado")
    fig.tight_layout()
    fig.savefig(pasta / "matriz_confusao.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 5))
    PrecisionRecallDisplay.from_predictions(y, scores, ax=ax, name="Modelo selecionado")
    ax.axhline(y.mean(), color="gray", linestyle="--", label="Prevalência no teste")
    ax.set(title="Precision e recall: dados sintéticos", xlabel="Recall", ylabel="Precision")
    ax.legend()
    fig.tight_layout()
    fig.savefig(pasta / "curva_precision_recall.png", dpi=150)
    plt.close(fig)


def criar_resumo(relatorio, pasta):
    m = relatorio["teste"]
    texto = f"""# Resultado do experimento

Dados sintéticos. Estes números não medem desempenho bancário real.

Modelo escolhido na validação: `{relatorio['modelo_escolhido']}`.
Limiar escolhido na validação: {m['limiar']:.6f}.

| Medida no teste | Resultado |
| --- | ---: |
| Transações | {m['total']} |
| Fraudes simuladas | {m['fraudes']} |
| Precision | {m['precision']:.2%} |
| Recall | {m['recall']:.2%} |
| Average precision | {m['average_precision']:.4f} |
| F2 | {m['f2']:.4f} |
| Taxa de alertas | {m['taxa_alertas']:.2%} |
| Alarmes falsos | {m['falsos_positivos']} |
| Fraudes não detectadas | {m['falsos_negativos']} |

O modelo sinalizou {m['verdadeiros_positivos']} fraudes simuladas e deixou passar
{m['falsos_negativos']}. Entre os alertas, {m['falsos_positivos']} eram transações legítimas.
O F2 favorece recall, mas essa escolha pode aumentar o volume de revisão.

O arquivo `metricas.json` inclui a comparação na validação, o baseline que
sempre prevê transação legítima e o resultado com limiar padrão de 0,5.

![Matriz de confusão](matriz_confusao.png)

![Curva precision-recall](curva_precision_recall.png)
"""
    (pasta / "resumo.md").write_text(texto, encoding="utf-8")
