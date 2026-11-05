# CasePy · Game Analytics Engine

Estudo de caso em Python usado nas aulas de desenvolvimento de software da **Educação Tecnológica Paula Peclat**. A turma constrói um pipeline que recebe estatísticas de jogadores, limpa e valida os dados com **Pydantic**, calcula um **índice de combate** e grava o resultado em JSON. Um simulador web em **Flask** permite testar o pipeline pelo navegador.

## O que tem aqui

| Pasta / arquivo | Para que serve |
|---|---|
| `projeto_inicial/` | Ponto de partida do caso: `completo.py`, versão comentada, notebook e guia visual do pipeline |
| `simulador/` | Servidor Flask local que roda o pipeline a cada envio e salva em `simulador/dados/` |
| `explicasues/` | Notebooks de gabarito comentados |
| `completo_gabarito.py` | Gabarito de estudo, linha por linha, do bloco novo de `completo.py` |
| `simulador_educacional.pdf` | Material de apoio |

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

Código sob licença [MIT](LICENSE). © Paula Peclat.
