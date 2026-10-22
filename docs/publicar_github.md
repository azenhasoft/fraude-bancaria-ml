# Publicar no GitHub

O projeto está publicado em [azenhasoft/fraude-bancaria-ml](https://github.com/azenhasoft/fraude-bancaria-ml). As instruções abaixo ficam como referência para publicar uma nova cópia.

## Pelo navegador

1. Entre no GitHub e crie um repositório chamado `fraude-bancaria-ml`.
2. Escolha a visibilidade e deixe desmarcada a criação automática de README.
3. Extraia o ZIP recebido. Abra a pasta `fraude-bancaria-ml` e use **Add file → Upload files** para enviar seu conteúdo.
4. Confira se `README.md` ficou na raiz do repositório, junto com `fraude/`, `docs/`, `exemplos/` e `tests/`.
5. Garanta que os arquivos ocultos `.gitignore` e `.github/workflows/testes.yml` também foram enviados. No seletor de arquivos, talvez seja necessário habilitar a exibição de arquivos ocultos.
6. Salve o commit. A aba **Actions** mostra o workflow configurado, quando Actions estiver habilitado no repositório.

## Pelo Git

Com Git instalado, execute na pasta que contém o README:

```bash
git init
git add .
git commit -m "Adiciona projeto conceitual de deteccao de fraudes"
git branch -M main
git remote add origin https://github.com/azenhasoft/fraude-bancaria-ml.git
git push -u origin main
```

O repositório remoto precisa existir e sua conta precisa ter permissão de escrita. O GitHub pode solicitar autenticação. Não coloque senha ou token nos arquivos do projeto.

Os dados gerados, os resultados de novas execuções e o modelo não entram no Git por causa do `.gitignore`. O relatório de referência em `docs/` pode ser publicado para demonstrar uma execução com dados sintéticos.

O pacote não inclui licença de código aberto. Se quiser permitir reutilização sob uma licença específica, escolha-a e adicione o arquivo `LICENSE` antes de divulgar essa permissão.
