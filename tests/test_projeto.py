"""Testes de comportamento, sem depender de um resultado exato do modelo."""
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import fbeta_score
from fraude.dados import FEATURES, NUMERICAS, gerar_dados, validar, dividir_por_data
from fraude.modelo import criar_pipeline, escolher_limiar, avaliar, prever
import joblib
import sklearn


class TestProjeto(unittest.TestCase):
    def test_geracao_reproduzivel_e_desbalanceada(self):
        a, b = gerar_dados(5000), gerar_dados(5000)
        pd.testing.assert_frame_equal(a, b)
        self.assertGreater(a.fraude.mean(), 0)
        self.assertLess(a.fraude.mean(), .1)

    def test_divisao_preserva_tempo_e_nao_repete_transacoes(self):
        dados = gerar_dados(5000)
        # Eu acrescento uma transação no mesmo instante para conferir os cortes.
        repetida = dados.iloc[[3000]].copy()
        repetida["id_transacao"] = "OUTRA"
        partes = dividir_por_data(pd.concat([dados, repetida], ignore_index=True))
        self.assertEqual(sum(map(len, partes)), len(dados) + 1)
        for antes, depois in zip(partes, partes[1:]):
            self.assertLess(antes.data_hora.max(), depois.data_hora.min())
            self.assertTrue(set(antes.id_transacao).isdisjoint(depois.id_transacao))

    def test_rejeita_entradas_invalidas(self):
        base = gerar_dados(5000)
        alteracoes = [("hora", 24), ("hora", 2.5), ("valor", -1),
                      ("valor", float("inf")), ("valor", "erro"),
                      ("transacoes_1h", 1.5), ("dispositivo_novo", "talvez"),
                      ("fraude", 2), ("data_hora", None), ("id_transacao", None)]
        for coluna, valor in alteracoes:
            with self.subTest(coluna=coluna, valor=valor):
                df = base.copy()
                if isinstance(valor, (str, float)) or valor is None:
                    df[coluna] = df[coluna].astype(object)
                df.loc[0, coluna] = valor
                with self.assertRaises((ValueError, TypeError)):
                    validar(df, treino=True)
        with self.assertRaises(ValueError):
            validar(base.drop(columns="valor"))
        duplicado = pd.concat([base, base.iloc[[0]]])
        with self.assertRaises(ValueError):
            validar(duplicado, treino=True)
        sem_fraude = base.assign(fraude=0)
        with self.assertRaises(ValueError):
            dividir_por_data(sem_fraude)

    def test_limiar_realmente_maximiza_f2_e_empate(self):
        y = np.array([0, 1, 0, 1, 1, 0])
        scores = np.array([.1, .3, .4, .7, .7, .9])
        limiar = escolher_limiar(y, scores)
        grade = np.unique(scores)
        valores = [fbeta_score(y, scores >= t, beta=2, zero_division=0) for t in grade]
        melhor = max(t for t, f in zip(grade, valores) if np.isclose(f, max(valores)))
        self.assertEqual(limiar, melhor)
        self.assertAlmostEqual(avaliar(y, scores, limiar)["f2"], max(valores))
        self.assertEqual(escolher_limiar([0, 1], [.5, .5]), .5)

    def test_pipeline_nao_aprende_com_novas_entradas(self):
        treino, _, teste = dividir_por_data(gerar_dados(5000))
        pipeline = criar_pipeline(LogisticRegression(max_iter=1000))
        pipeline.fit(treino[FEATURES], treino.fraude)
        imputador = pipeline.named_steps["tratamento"].named_transformers_["numericas"].named_steps["preencher"]
        np.testing.assert_allclose(imputador.statistics_, treino[NUMERICAS].median().to_numpy())
        anteriores = imputador.statistics_.copy()
        novas = teste.head(3)[FEATURES].copy()
        novas["valor"] = [np.nan, 999999, 1]
        novas["canal"] = "canal_desconhecido"
        scores = pipeline.predict_proba(novas)[:, 1]
        self.assertTrue(np.isfinite(scores).all())
        np.testing.assert_array_equal(imputador.statistics_, anteriores)

    def test_modelo_salvo_reproduz_previsao(self):
        treino, _, teste = dividir_por_data(gerar_dados(5000))
        pipeline = criar_pipeline(LogisticRegression(max_iter=1000)).fit(treino[FEATURES], treino.fraude)
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            entrada, modelo = pasta / "entrada.csv", pasta / "modelo.joblib"
            teste.head(10)[FEATURES].to_csv(entrada, index=False)
            joblib.dump({"pipeline": pipeline, "limiar": .4, "features": FEATURES,
                         "versoes": {"sklearn": sklearn.__version__}}, modelo)
            saida = prever(entrada, modelo, pasta / "saida.csv")
            esperado = pipeline.predict_proba(pd.read_csv(entrada))[:, 1]
            np.testing.assert_allclose(saida.score_fraude, esperado)
            np.testing.assert_array_equal(saida.enviar_para_analise, esperado >= .4)


if __name__ == "__main__":
    unittest.main()
