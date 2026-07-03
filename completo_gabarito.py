"""
================================================================================
  GABARITO DE ESTUDO — bloco NOVO do completo.py comentado linha por linha
================================================================================

  Este arquivo NÃO é usado pela aplicação. Ele existe apenas como material
  de estudo para você entender exatamente o que cada linha do bloco marcado
  com # === INICIO NOVO === faz.

  Ele importa as funções ORIGINAIS de completo.py (Jogador, sanitizar_registro,
  indice_combate) e reescreve apenas as três funções novas, agora com
  comentários explicativos ao lado de cada construção da linguagem.

  Se você quiser rodar este arquivo isolado para experimentar:
      python completo_gabarito.py
  ele mostra um exemplo prático no final.
================================================================================
"""

# ------------------------------------------------------------------------------
# 1) IMPORTAÇÕES — módulos da biblioteca padrão do Python
# ------------------------------------------------------------------------------

# datetime: classe que representa um instante (data + hora + microssegundo).
#           Usamos para gerar nomes de arquivo únicos por inserção.
from datetime import datetime

# Path: forma moderna e orientada a objetos de manipular caminhos de arquivo.
#       Substitui as funções de os.path do jeito antigo.
from pathlib import Path

# json: converte estruturas Python (dict, list) em texto JSON e vice-versa.
#       Já existia no completo.py original — importado aqui de novo para
#       este arquivo ser autossuficiente.
import json


# ------------------------------------------------------------------------------
# 2) REAPROVEITAMENTO — importamos do completo.py o que já foi feito lá
# ------------------------------------------------------------------------------
# Regra de ouro: NÃO reimplementar o que já existe. Reaproveitamos o modelo
# Pydantic (Jogador), a função de sanitização e a função do índice de combate.
# Se um dia essas funções mudarem em completo.py, este arquivo continua correto.
from simulador.completo import Jogador, sanitizar_registro, indice_combate

# ValidationError vem do Pydantic e é levantada quando um dado não bate com
# o modelo Jogador (por exemplo, faltar um campo obrigatório).
from pydantic import ValidationError


# ==============================================================================
# 3) _processar — pega UM registro cru e devolve UM resultado processado
# ==============================================================================
def _processar(r: dict) -> dict:
    #  ^        ^   ^        ^
    #  |        |   |        └── type hint: essa função devolve um dict
    #  |        |   └── tipo do parâmetro: espera-se um dict
    #  |        └── nome curto (r = registro). Nomes curtos são OK dentro de
    #  |            funções pequenas, quando o contexto deixa claro.
    #  └── o underscore antes do nome é uma CONVENÇÃO em Python: sinaliza
    #      "esta é uma função INTERNA, use processar_registros() em vez dela".
    #      O Python não impede o uso, mas outros programadores saberão respeitar.

    # ---- 3.1) Cópia defensiva + sanitização --------------------------------
    r = sanitizar_registro(dict(r))
    #           ^          ^
    #           |          └── dict(r) cria uma CÓPIA rasa do dicionário
    #           |              recebido. Sem isso, se sanitizar_registro
    #           |              modificar o dicionário (e ele modifica — troca
    #           |              valores negativos por 0), estaríamos mexendo
    #           |              no objeto do CHAMADOR. Cópia defensiva evita
    #           |              efeitos colaterais surpresas.
    #           └── função que veio do completo.py — corrige valores
    #               negativos para 0 e imprime aviso no console.
    #
    # Curiosidade: a atribuição "r = ..." não muda o dict externo, ela apenas
    # faz o nome local "r" apontar para o dict novo (sanitizado). O original
    # que veio de fora fica intocado — porque fizemos a cópia.

    # ---- 3.2) Tentativa de validar e processar -----------------------------
    try:
        # Jogador é a classe Pydantic definida em completo.py.
        # A sintaxe **r "desempacota" o dicionário como argumentos nomeados.
        # É equivalente a escrever:
        #     Jogador(Nickname=r["Nickname"], Mortes=r["Mortes"], ...)
        # Se faltar um campo obrigatório ou o tipo estiver errado, Pydantic
        # levanta ValidationError automaticamente — não precisamos validar
        # à mão.
        j = Jogador(**r)

        # Se chegamos aqui, o registro é válido. Montamos o dicionário de
        # saída MANUALMENTE — assim controlamos a ORDEM das chaves e quais
        # campos serão expostos.
        return {
            "Nickname": j.Nickname, "Mortes": j.Mortes,
            "Abates": j.Abates, "Assistências": j.Assistências,
            # round(valor, 2) arredonda para 2 casas decimais.
            # indice_combate() é a função original do completo.py.
            # Passamos os atributos JÁ VALIDADOS por Pydantic (j.Mortes etc.),
            # não os originais — garantia extra de que os números são inteiros.
            "IndiceCombate": round(indice_combate(j.Mortes, j.Abates, j.Assistências), 2),
        }

    # ---- 3.3) Tratamento de erro -------------------------------------------
    except (ValidationError, Exception) as e:
        #    ^                ^
        #    |                └── Exception é o "guarda-chuva" que pega
        #    |                    qualquer outro erro inesperado.
        #    └── ValidationError é o erro específico do Pydantic.
        #
        # Nota didática: capturar Exception assim é uma escolha DEFENSIVA —
        # queremos que UM registro ruim NÃO derrube o processamento dos
        # outros. Em código de produção mais estrito, você trataria cada
        # tipo de erro separadamente para agir de formas diferentes.

        # Devolvemos o próprio registro (com os campos que ele tinha) mais
        # uma chave nova "Erro" contendo a descrição textual do problema.
        #
        # A sintaxe {**r, "Erro": str(e)} lê-se assim:
        #   "Crie um dicionário novo com TUDO que estava em r, e adicione/
        #    sobrescreva a chave 'Erro' com o texto do erro."
        # É o equivalente moderno de: novo = dict(r); novo["Erro"] = str(e)
        return {**r, "Erro": str(e)}


# ==============================================================================
# 4) processar_registros — recebe a LISTA inteira e devolve a lista processada
# ==============================================================================
def processar_registros(registros: list[dict]) -> list[dict]:
    #                              ^
    #                              └── list[dict] significa "lista onde cada
    #                                  elemento é um dicionário". Sintaxe
    #                                  disponível a partir do Python 3.9.

    # Esta linha é uma LIST COMPREHENSION — jeito compacto de fazer:
    #     resultado = []
    #     for r in registros:
    #         resultado.append(_processar(r))
    #     return resultado
    # As três linhas viram uma só. Ganhos: mais curto, mais legível DEPOIS
    # que você se acostuma, e ligeiramente mais rápido.
    return [_processar(r) for r in registros]
    #       ^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^
    #       o que fazer    de onde vem cada r


# ==============================================================================
# 5) salvar_novo_json — grava a lista processada em um novo arquivo JSON
# ==============================================================================
def salvar_novo_json(resultados: list[dict], pasta_destino: str = "dados") -> str:
    #                                                                 ^        ^
    #                                                                 |        └── retorna uma string
    #                                                                 └── valor DEFAULT: se ninguém
    #                                                                     passar pasta_destino, usa "dados"

    # ---- 5.1) Preparar a pasta ---------------------------------------------
    # Path("dados") cria um OBJETO Path — o Python ainda não tocou no disco.
    # O ; junta duas instruções na mesma linha (uso raro; aqui foi para
    # deixar mais compacto, mas você pode separar em duas linhas se preferir).
    pasta = Path(pasta_destino); pasta.mkdir(parents=True, exist_ok=True)
    #                                        ^             ^
    #                                        |             └── se a pasta JÁ existir, não reclama
    #                                        └── se as pastas-mãe não existirem, cria também
    #                                            (ex.: "a/b/c" cria a, depois b, depois c)

    # ---- 5.2) Montar o nome único ------------------------------------------
    # f-string com FORMAT SPEC de datetime. Sintaxe:
    #     f"{objeto:formato}"
    # Aqui o objeto é datetime.now() (o instante atual) e o formato é:
    #     %Y  ano com 4 dígitos
    #     %m  mês
    #     %d  dia
    #     %H  hora (24h)
    #     %M  minuto
    #     %S  segundo
    #     %f  microssegundo (6 dígitos)
    # Exemplo de resultado: "insercao_20260703_113815_142858.json"
    #
    # O microssegundo (%f) é o que garante UNICIDADE mesmo se duas inserções
    # chegarem no mesmo segundo. Sem ele, o segundo arquivo sobrescreveria
    # o primeiro.
    caminho = pasta / f"insercao_{datetime.now():%Y%m%d_%H%M%S_%f}.json"
    #                ^
    #                └── operador / do pathlib: junta partes de caminho de
    #                    forma cross-platform. No Windows vira "\", no Linux "/".

    # ---- 5.3) Gravar o conteúdo --------------------------------------------
    # write_text() faz três coisas em um único gesto: abre o arquivo, escreve
    # o texto, fecha o arquivo. Substitui o "with open(...) as f: f.write(...)".
    #
    # json.dumps() converte a estrutura Python em uma STRING JSON.
    #   - ensure_ascii=False  →  mantém acentos em vez de virar "ç"
    #   - indent=2            →  formata o JSON com 2 espaços de recuo (bonito de ler)
    #
    # encoding="utf-8" garante que os acentos sejam gravados corretamente
    # no disco, independente do sistema operacional.
    caminho.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- 5.4) Retornar o caminho como string -------------------------------
    # str(caminho) converte o objeto Path em texto simples. É útil para quem
    # chama a função poder imprimir, logar ou mandar em uma resposta JSON.
    return str(caminho)


# ==============================================================================
# 6) DEMO — só roda se você executar este arquivo diretamente
# ==============================================================================
# A construção if __name__ == "__main__" é o "portão" que separa código de
# biblioteca de código de teste/demonstração. Se este arquivo for IMPORTADO
# por outro (from completo_gabarito import ...), o bloco abaixo NÃO executa.
# Se for RODADO direto (python completo_gabarito.py), ele executa.
if __name__ == "__main__":
    entrada_exemplo = [
        # Caso 1: jogador normal — passa direto
        {"Nickname": "ShadowByte_99",  "Mortes":  5, "Abates": 20, "Assistências": 8},
        # Caso 2: valor negativo — o sanitizar_registro corrige para 0
        {"Nickname": "GhostRunner_77", "Mortes": -1, "Abates": 10, "Assistências": 4},
        # Caso 3: campo faltando — Pydantic vai levantar ValidationError,
        #         e o except devolve o dicionário com uma chave "Erro"
        {"Nickname": "IncompletoZ",    "Mortes":  2, "Abates":  8},
    ]

    print("=== Entrada crua ===")
    print(json.dumps(entrada_exemplo, ensure_ascii=False, indent=2))

    processados = processar_registros(entrada_exemplo)

    print("\n=== Saída processada ===")
    print(json.dumps(processados, ensure_ascii=False, indent=2))

    caminho_final = salvar_novo_json(processados, pasta_destino="dados_estudo")
    print(f"\nArquivo gerado em: {caminho_final}")
