"""
Servidor localhost do simulador de inserção de jogadores.

A cada envio (formulário HTML ou POST JSON), executa o pipeline definido em
completo.py (sanitização + validação Pydantic + índice de combate) e grava
um novo arquivo JSON em ./dados/insercao_<timestamp>.json.
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flask import Flask, request, render_template, jsonify, send_from_directory

from projeto_inicial.completo import processar_registros, salvar_novo_json

app = Flask(__name__)

PASTA_DADOS = BASE_DIR / "dados"


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/inserir", methods=["POST"])
def inserir():
    """
    Recebe múltiplos registros de jogadores. Aceita:
      - JSON: lista de objetos OU um único objeto
      - Form URL-encoded: campos repetidos Nickname/Mortes/Abates/Assistências
    """
    registros: list[dict] = []

    if request.is_json:
        payload = request.get_json(silent=True) or []
        if isinstance(payload, dict):
            registros = [payload]
        elif isinstance(payload, list):
            registros = payload
    else:
        nicknames = request.form.getlist("Nickname")
        mortes = request.form.getlist("Mortes")
        abates = request.form.getlist("Abates")
        assistencias = request.form.getlist("Assistências")

        for i, nick in enumerate(nicknames):
            if not nick.strip():
                continue
            try:
                registros.append({
                    "Nickname": nick.strip(),
                    "Mortes": int(mortes[i]),
                    "Abates": int(abates[i]),
                    "Assistências": int(assistencias[i]),
                })
            except (ValueError, IndexError):
                continue

    if not registros:
        return jsonify({"erro": "Nenhum registro válido enviado."}), 400

    resultados = processar_registros(registros)
    caminho = salvar_novo_json(resultados, pasta_destino=str(PASTA_DADOS))

    return jsonify({
        "arquivo_gerado": Path(caminho).name,
        "caminho": caminho,
        "total": len(resultados),
        "resultados": resultados,
    })


@app.route("/dados", methods=["GET"])
def listar_dados():
    """Lista todos os JSONs já gerados."""
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    arquivos = sorted(
        [f.name for f in PASTA_DADOS.glob("insercao_*.json")],
        reverse=True,
    )
    return jsonify({"total": len(arquivos), "arquivos": arquivos})


@app.route("/dados/<path:nome>", methods=["GET"])
def obter_dado(nome: str):
    """Devolve o conteúdo de um JSON gerado."""
    return send_from_directory(PASTA_DADOS, nome, mimetype="application/json")


if __name__ == "__main__":
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    app.run(host="127.0.0.1", port=5000, debug=True)
