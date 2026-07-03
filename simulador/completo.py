import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pydantic import BaseModel, field_validator, ValidationError
import json

# === INICIO NOVO ===
from datetime import datetime
from pathlib import Path
# === FIM NOVO ===


class Jogador(BaseModel):
    Nickname: str
    Mortes: int
    Abates: int
    Assistências: int

    @field_validator('Mortes', 'Abates', 'Assistências')
    @classmethod
    def validar_valores(cls, value: int, info) -> int:
        if value < 0:
            raise ValueError("Os valores de mortes, abates e assistências devem ser não negativos.")
        return value


def indice_combate(Mortes: int, Abates: int, Assistências: int):
    if Mortes == 0:
        divisor = 1
        resultado = (Abates + Assistências) / divisor
    else:
        resultado = (Abates + Assistências) / Mortes
    return resultado


def carregar_registros_jogadores(json_file: str) -> list[dict]:
    with open(json_file, 'r', encoding='utf-8') as file:
        registros_jogadores = json.load(file)
    return registros_jogadores


def sanitizar_registro(registro: dict) -> dict:
    campos_numericos = ['Mortes', 'Abates', 'Assistências']
    for campo in campos_numericos:
        if campo in registro and registro[campo] < 0:
            print(f"[AVISO] '{registro.get('Nickname', '?')}': campo '{campo}' era {registro[campo]}, corrigido para 0.")
            registro[campo] = 0
    return registro


# === INICIO NOVO ===
def _processar(r: dict) -> dict:
    r = sanitizar_registro(dict(r))
    try:
        j = Jogador(**r)
        return {
            "Nickname": j.Nickname, "Mortes": j.Mortes,
            "Abates": j.Abates, "Assistências": j.Assistências,
            "IndiceCombate": round(indice_combate(j.Mortes, j.Abates, j.Assistências), 2),
        }
    except (ValidationError, Exception) as e:
        return {**r, "Erro": str(e)}


def processar_registros(registros: list[dict]) -> list[dict]:
    return [_processar(r) for r in registros]


def salvar_novo_json(resultados: list[dict], pasta_destino: str = "dados") -> str:
    pasta = Path(pasta_destino); pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"insercao_{datetime.now():%Y%m%d_%H%M%S_%f}.json"
    caminho.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(caminho)
# === FIM NOVO ===


if __name__ == "__main__":
    import os

    json_file = str(Path(__file__).with_name("ficha_geral_player.json"))

    if os.path.exists(json_file):
        registros_jogadores = carregar_registros_jogadores(json_file)

        for registro in registros_jogadores:
            try:
                registro = sanitizar_registro(registro)
                jogador = Jogador(**registro)
                indice = indice_combate(
                    jogador.Mortes,
                    jogador.Abates,
                    jogador.Assistências
                )
                print(f"Jogador: {jogador.Nickname} | Índice de Combate: {indice:.2f}")

            except ValidationError as e:
                print(f"[ERRO DE VALIDAÇÃO] Jogador '{registro.get('Nickname', '?')}': {e}")

            except Exception as e:
                print(f"[ERRO] {e}")

    else:
        print(f"Arquivo '{json_file}' não encontrado. Verifique se o caminho está correto.")
