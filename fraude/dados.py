"""Dados fictícios e validação do contrato de entrada."""
from pathlib import Path
import numpy as np
import pandas as pd

NUMERICAS = ["valor", "hora", "transacoes_1h", "distancia_km", "idade_conta_dias"]
CATEGORICAS = ["canal", "dispositivo_novo", "favorecido_novo"]
FEATURES = NUMERICAS + CATEGORICAS
SEED = 42


def gerar_dados(n=20000, seed=SEED):
    if n < 1000:
        raise ValueError("Use pelo menos 1000 transações para este experimento.")
    rng = np.random.default_rng(seed)
    # Aqui eu crio dados fictícios. Nenhuma transação vem de um banco real.
    datas = pd.Timestamp("2025-01-01") + pd.to_timedelta(
        np.sort(rng.integers(0, 180 * 86400, n)), unit="s"
    )
    df = pd.DataFrame({
        "id_transacao": [f"TX{i:07d}" for i in range(n)],
        "data_hora": datas,
        "valor": np.round(np.clip(rng.lognormal(4.7, 1.2, n), 1, 50000), 2),
        "hora": datas.hour,
        "transacoes_1h": rng.poisson(1.5, n),
        "distancia_km": np.round(rng.exponential(35, n), 2),
        "idade_conta_dias": rng.integers(1, 3651, n),
        "canal": rng.choice(["pix", "cartao", "transferencia"], n, p=[.55, .30, .15]),
        "dispositivo_novo": rng.choice(["sim", "nao"], n, p=[.12, .88]),
        "favorecido_novo": rng.choice(["sim", "nao"], n, p=[.18, .82]),
    })
    # Os sinais aumentam a chance de fraude, mas não determinam o resultado.
    # Os rótulos também são simulados. Na prática, eu precisaria de casos confirmados.
    logit = (-6.0 + .8 * (df.valor > 1000) + .9 * (df.hora < 5)
             + .9 * (df.transacoes_1h >= 4) + .8 * (df.distancia_km > 100)
             + .7 * (df.idade_conta_dias < 90)
             + 1.5 * (df.dispositivo_novo == "sim")
             + 1.1 * (df.favorecido_novo == "sim")
             + 1.3 * ((df.dispositivo_novo == "sim") & (df.favorecido_novo == "sim")))
    df["fraude"] = rng.binomial(1, 1 / (1 + np.exp(-logit)))
    return df


def validar(df, treino=False):
    obrigatorias = FEATURES + (["id_transacao", "data_hora", "fraude"] if treino else [])
    faltantes = sorted(set(obrigatorias) - set(df.columns))
    if faltantes:
        raise ValueError(f"Colunas ausentes: {', '.join(faltantes)}")
    if df.empty:
        raise ValueError("O arquivo está vazio.")
    dados = df.copy()
    for coluna in NUMERICAS:
        original = dados[coluna]
        dados[coluna] = pd.to_numeric(original, errors="coerce")
        if (original.notna() & dados[coluna].isna()).any():
            raise ValueError(f"Valor não numérico em {coluna}.")
        presentes = dados[coluna].dropna()
        if not np.isfinite(presentes).all() or (presentes < 0).any():
            raise ValueError(f"Valor negativo ou infinito em {coluna}.")
    if (dados.hora.dropna() > 23).any() or (dados.hora.dropna() % 1 != 0).any():
        raise ValueError("Hora deve ser um inteiro entre 0 e 23.")
    for coluna in ["transacoes_1h", "idade_conta_dias"]:
        if (dados[coluna].dropna() % 1 != 0).any():
            raise ValueError(f"{coluna} deve conter inteiros.")
    for coluna in CATEGORICAS:
        dados[coluna] = dados[coluna].where(dados[coluna].notna(), np.nan)
    for coluna in ["dispositivo_novo", "favorecido_novo"]:
        if not dados[coluna].dropna().isin(["sim", "nao"]).all():
            raise ValueError(f"{coluna} aceita sim, nao ou valor ausente.")
    if treino:
        if dados.id_transacao.isna().any() or dados.id_transacao.duplicated().any():
            raise ValueError("Cada transação precisa de um identificador único e preenchido.")
        dados["data_hora"] = pd.to_datetime(dados.data_hora, errors="raise", utc=True)
        if dados.data_hora.isna().any():
            raise ValueError("Data da transação não pode ficar vazia.")
        if dados.fraude.isna().any() or not dados.fraude.isin([0, 1]).all():
            raise ValueError("Fraude deve ser 0 ou 1, sem valores ausentes.")
    return dados


def dividir_por_data(df):
    # Eu treino no passado e deixo o período mais recente para o teste.
    df = validar(df, treino=True).sort_values("data_hora", kind="stable")
    datas = df.data_hora.drop_duplicates().sort_values().to_numpy()
    if len(datas) < 5:
        raise ValueError("Preciso de pelo menos cinco datas distintas.")
    corte1, corte2 = datas[int(len(datas) * .6)], datas[int(len(datas) * .8)]
    partes = (df[df.data_hora < corte1],
              df[(df.data_hora >= corte1) & (df.data_hora < corte2)],
              df[df.data_hora >= corte2])
    for parte in partes:
        if parte.fraude.nunique() != 2:
            raise ValueError("Treino, validação e teste precisam conter as duas classes.")
        if parte[FEATURES].isna().all().any():
            raise ValueError("Há uma variável inteiramente vazia em uma das divisões.")
    return partes


def salvar_dados(destino, n=20000):
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    gerar_dados(n).to_csv(destino, index=False)
    return destino
