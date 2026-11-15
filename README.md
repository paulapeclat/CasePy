# CasePy · Game Analytics Engine

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24238326.svg)](https://doi.org/10.5281/zenodo.24238326)

Estudo de caso em Python usado nas aulas de desenvolvimento de software da **Educação Tecnológica Paula Peclat**. A turma constrói um pipeline que recebe estatísticas de jogadores, limpa e valida os dados com **Pydantic**, calcula um **índice de combate** e grava o resultado em JSON. Um simulador web em **Flask** permite testar o pipeline pelo navegador.

## O que tem aqui

| Pasta / arquivo | Para que serve |
|---|---|
| `projeto_inicial/` | Ponto de partida do caso: `completo.py`, versão comentada, notebook, guia visual do pipeline e o briefing do cliente |
| `simulador/` | Servidor Flask local que roda o pipeline a cada envio e salva em `simulador/dados/` |
| `simulador_educacional.pdf` | Material de apoio |

O cliente do briefing, a Arena Carioca, é fictício e foi criado para este estudo de caso.

## Como rodar o simulador

```bash
cd simulador
python -m venv .venv
source .venv/bin/activate      # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Depois, abra http://127.0.0.1:5000 no navegador.

> O simulador roda em modo de desenvolvimento (`debug=True`) e só aceita conexões da própria máquina. Não publique esse servidor na internet do jeito que está.

## Licença

© 2026 Paula Peclat.

- **Código** (`.py`, `.ipynb`, `simulador/`): licença [MIT](LICENSE).
- **Textos e materiais de apoio** (PDFs, `pipeline_guia.html` e este README): licença [CC BY 4.0](LICENSE-CONTEUDO.md).

## Como citar

Use o botão **Cite this repository**, no alto da página do repositório, ou os dados do arquivo [`CITATION.cff`](CITATION.cff).
