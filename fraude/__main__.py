"""Execute com python -m fraude."""
import argparse
from pathlib import Path
from .dados import salvar_dados
from .modelo import treinar, prever


def main():
    parser = argparse.ArgumentParser(description="Estudo de fraude bancária com dados fictícios")
    sub = parser.add_subparsers(dest="comando", required=True)
    gerar = sub.add_parser("gerar", help="Criar a base sintética")
    gerar.add_argument("--saida", default="dados/transacoes.csv")
    gerar.add_argument("--linhas", type=int, default=20000)
    treino = sub.add_parser("treinar", help="Treinar e avaliar")
    treino.add_argument("--dados", default="dados/transacoes.csv")
    treino.add_argument("--saida", default="resultados")
    predicao = sub.add_parser("prever", help="Analisar um CSV com novas transações")
    predicao.add_argument("--dados", required=True)
    predicao.add_argument("--modelo", default="resultados/modelo.joblib")
    predicao.add_argument("--saida", default="resultados/novas_previsoes.csv")
    tudo = sub.add_parser("executar", help="Gerar dados, treinar, avaliar e prever os exemplos")
    tudo.add_argument("--linhas", type=int, default=20000)
    args = parser.parse_args()
    try:
        if args.comando == "gerar":
            print(salvar_dados(args.saida, args.linhas))
        elif args.comando == "prever":
            saida = prever(args.dados, args.modelo, args.saida)
            print(f"{len(saida)} transações analisadas. Saída: {args.saida}")
        else:
            if args.comando == "executar":
                dados, destino = salvar_dados("dados/transacoes.csv", args.linhas), "resultados"
            else:
                dados, destino = args.dados, args.saida
            resultado = treinar(dados, destino)
            print(f"Modelo: {resultado['modelo_escolhido']}")
            print(f"Recall no teste sintético: {resultado['teste']['recall']:.2%}")
            print(f"Relatório: {Path(destino) / 'resumo.md'}")
            if args.comando == "executar":
                prever("exemplos/novas_transacoes.csv", "resultados/modelo.joblib",
                       "resultados/novas_previsoes.csv")
    except (ValueError, FileNotFoundError) as erro:
        parser.exit(2, f"Erro: {erro}\n")


if __name__ == "__main__":
    main()
