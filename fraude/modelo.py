"""Treinamento, comparação e escolha do limiar de alerta."""
import json
import platform
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix,
    fbeta_score, precision_score, recall_score, roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .dados import NUMERICAS, CATEGORICAS, FEATURES, SEED, dividir_por_data, validar


def criar_pipeline(classificador):
    numericas = Pipeline([("preencher", SimpleImputer(strategy="median")),
                          ("escala", StandardScaler())])
    categoricas = Pipeline([("preencher", SimpleImputer(strategy="most_frequent")),
                           ("codificar", OneHotEncoder(handle_unknown="ignore"))])
    # Eu deixo o tratamento no pipeline para aprender os ajustes só no treino.
    tratamento = ColumnTransformer([("numericas", numericas, NUMERICAS),
                                    ("categoricas", categoricas, CATEGORICAS)])
    return Pipeline([("tratamento", tratamento), ("modelo", classificador)])


def escolher_limiar(y, scores):
    # Eu dou mais peso ao recall com F2. Isso é uma escolha didática.
    # Em um banco, eu teria que considerar os custos e a capacidade de análise.
    from sklearn.metrics import precision_recall_curve
    precision, recall, thresholds = precision_recall_curve(y, scores)
    f2 = 5 * precision[:-1] * recall[:-1] / np.maximum(
        4 * precision[:-1] + recall[:-1], 1e-15)
    # Em caso de empate, eu uso o maior limiar, que gera menos alertas.
    melhores = np.flatnonzero(np.isclose(f2, f2.max(), rtol=0, atol=1e-12))
    return float(thresholds[melhores[-1]])


def avaliar(y, scores, limiar):
    previsto = (np.asarray(scores) >= limiar).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, previsto, labels=[0, 1]).ravel()
    return {
        "limiar": float(limiar), "total": len(y), "fraudes": int(np.sum(y)),
        "prevalencia": float(np.mean(y)), "acuracia": accuracy_score(y, previsto),
        "precision": precision_score(y, previsto, zero_division=0),
        "recall": recall_score(y, previsto, zero_division=0),
        "f2": fbeta_score(y, previsto, beta=2, zero_division=0),
        "average_precision": average_precision_score(y, scores),
        "roc_auc": roc_auc_score(y, scores),
        "taxa_alertas": float(previsto.mean()),
        "verdadeiros_negativos": int(tn), "falsos_positivos": int(fp),
        "falsos_negativos": int(fn), "verdadeiros_positivos": int(tp),
    }


def treinar(arquivo, saida="resultados"):
    pasta = Path(saida)
    pasta.mkdir(parents=True, exist_ok=True)
    treino, validacao, teste = dividir_por_data(pd.read_csv(arquivo))
    modelos = {
        "regressao_logistica": criar_pipeline(LogisticRegression(
            class_weight="balanced", max_iter=2000, random_state=SEED)),
        "random_forest": criar_pipeline(RandomForestClassifier(
            n_estimators=180, max_depth=9, min_samples_leaf=15,
            class_weight="balanced_subsample", n_jobs=-1, random_state=SEED)),
    }
    comparacao = {}
    for nome, pipeline in modelos.items():
        pipeline.fit(treino[FEATURES], treino.fraude)
        scores = pipeline.predict_proba(validacao[FEATURES])[:, 1]
        limiar = escolher_limiar(validacao.fraude, scores)
        comparacao[nome] = avaliar(validacao.fraude, scores, limiar)
    escolhido = max(comparacao, key=lambda nome: comparacao[nome]["average_precision"])
    pipeline = modelos[escolhido]
    limiar = comparacao[escolhido]["limiar"]
    # Eu escolho modelo e limiar na validação. O teste fica fora dessa decisão.
    # Também não retreino aqui, porque isso mudaria os scores usados no ajuste.
    scores = pipeline.predict_proba(teste[FEATURES])[:, 1]
    baseline = DummyClassifier(strategy="most_frequent").fit(treino[FEATURES], treino.fraude)
    baseline_scores = baseline.predict_proba(teste[FEATURES])[:, 1]
    relatorio = {
        "aviso": "Dados sintéticos. Não representa desempenho em um banco real.",
        "seed": SEED, "modelo_escolhido": escolhido,
        "criterio_modelo": "Maior average precision na validação",
        "criterio_limiar": "Maior F2 na validação; empate favorece o maior limiar",
        "versoes": {"python": platform.python_version(), "sklearn": sklearn.__version__,
                     "numpy": np.__version__, "pandas": pd.__version__, "joblib": joblib.__version__},
        "divisoes": {nome: {"linhas": len(parte), "fraudes": int(parte.fraude.sum()),
                    "inicio": str(parte.data_hora.min()), "fim": str(parte.data_hora.max())}
                     for nome, parte in zip(["treino", "validacao", "teste"], [treino, validacao, teste])},
        "validacao": comparacao, "teste": avaliar(teste.fraude, scores, limiar),
        "teste_limiar_05": avaliar(teste.fraude, scores, .5),
        "baseline_teste": avaliar(teste.fraude, baseline_scores, .5),
    }
    (pasta / "metricas.json").write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")
    joblib.dump({"pipeline": pipeline, "limiar": limiar, "features": FEATURES,
                 "versoes": relatorio["versoes"]}, pasta / "modelo.joblib")
    previsoes = teste[["id_transacao", "data_hora", "fraude"]].copy()
    previsoes["score_fraude"] = scores
    previsoes["enviar_para_analise"] = (scores >= limiar).astype(int)
    previsoes.to_csv(pasta / "previsoes_teste.csv", index=False)
    from .relatorio import criar_graficos, criar_resumo
    criar_graficos(teste.fraude, scores, limiar, pasta)
    criar_resumo(relatorio, pasta)
    return relatorio


def prever(arquivo, modelo, destino):
    # Eu carrego apenas arquivos joblib que eu mesmo gerei ou de origem confiável.
    pacote = joblib.load(modelo)
    if pacote["versoes"]["sklearn"] != sklearn.__version__:
        raise ValueError("Use a mesma versão do scikit-learn usada no treinamento.")
    df = validar(pd.read_csv(arquivo))
    scores = pacote["pipeline"].predict_proba(df[pacote["features"]])[:, 1]
    saida = df.copy()
    # O score ajuda a priorizar a análise. Não é uma confirmação de fraude.
    saida["score_fraude"] = scores
    saida["enviar_para_analise"] = (scores >= pacote["limiar"]).astype(int)
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    saida.to_csv(destino, index=False)
    return saida
