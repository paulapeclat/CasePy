# sys e io são módulos da biblioteca padrão do Python (standard library).
# Não precisam ser instalados — já vêm com o Python.
import sys
import io

# No Windows, o terminal usa cp1252 por padrão, que não suporta caracteres
# como 'ç', 'ã', 'é'. Forçamos o stdout (saída padrão) a usar UTF-8,
# que é o encoding universal capaz de representar qualquer caractere.
# sys.stdout.buffer é o stream binário bruto por baixo do stdout de texto.
# Substituímos o wrapper de texto por um novo com encoding explícito.
# Isso é uma técnica de monkey patching: substituir um objeto em runtime.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Pydantic é uma biblioteca de validação de dados baseada em type hints do Python.
# BaseModel é a classe base que transforma uma classe Python em um schema validado.
# field_validator permite adicionar regras de validação customizadas por campo.
# ValidationError é a exceção lançada quando os dados não passam na validação.
from pydantic import BaseModel, field_validator, ValidationError

# json é um módulo da standard library para serializar/deserializar JSON.
# Serializar = converter Python → JSON. Deserializar = JSON → Python.
import json


# ─── MODELO DE DADOS ────────────────────────────────────────────────────────────

# Herdar de BaseModel transforma Jogador em um schema Pydantic.
# Isso significa que ao instanciar Jogador(**dados), o Pydantic:
#   1. Verifica os tipos de cada campo (str, int)
#   2. Roda os validators customizados
#   3. Lança ValidationError se algo estiver errado
# É uma forma de garantir integridade dos dados na entrada — princípio de "fail fast".
class Jogador(BaseModel):
    # Type hints não são apenas documentação aqui — o Pydantic os usa para validação.
    # str: qualquer string. int: número inteiro (sem casas decimais).
    # Se vier um float como 3.5, o Pydantic tenta converter para int. Se vier "abc", falha.
    Nickname: str
    Mortes: int
    Abates: int
    Assistências: int

    # @field_validator é um decorator do Pydantic.
    # Decorators são funções que envolvem outras funções, adicionando comportamento.
    # Aqui ele registra validar_valores como validador dos campos listados.
    # O Pydantic chama esse método automaticamente para cada campo especificado,
    # passando o valor já convertido para o tipo correto (int, no caso).
    @field_validator('Mortes', 'Abates', 'Assistências')

    # @classmethod significa que o método pertence à classe, não à instância.
    # O Pydantic exige isso nos validators porque eles rodam antes do objeto existir.
    # 'cls' representa a própria classe Jogador (equivalente ao 'self' de instância).
    # 'value' é o valor do campo sendo validado.
    # 'info' é um objeto do Pydantic com metadados (ex: nome do campo).
    # '-> int' é o tipo de retorno: o validator deve devolver o valor validado.
    @classmethod
    def validar_valores(cls, value: int, info) -> int:
        # Regra de negócio: valores negativos são semanticamente impossíveis.
        # Ninguém pode ter -1 mortes. Rejeitar aqui evita cálculos corrompidos adiante.
        # Lançar ValueError dentro de um validator do Pydantic é o contrato esperado:
        # o Pydantic captura e converte em ValidationError com contexto do campo.
        if value < 0:
            raise ValueError("Os valores de mortes, abates e assistências devem ser não negativos.")
        # O validator DEVE retornar o valor — é ele que será atribuído ao campo.
        # Se esquecer o return, o campo fica None.
        return value


# ─── FUNÇÃO DE CÁLCULO ──────────────────────────────────────────────────────────

# Função pura: recebe dados, retorna resultado, sem efeitos colaterais.
# Funções puras são previsíveis, fáceis de testar e de reutilizar.
# Type hints nos parâmetros documentam a interface e permitem checagem estática
# com ferramentas como mypy ou o próprio VS Code (Pylance).
def indice_combate(Mortes: int, Abates: int, Assistências: int):
    # Guarda de divisão por zero: se Mortes == 0, usar divisor 1 evita ZeroDivisionError.
    # Isso é chamado de "caso especial" ou "edge case" — situação limite que quebraria
    # a lógica normal. Todo código de produção precisa tratar edge cases explicitamente.
    if Mortes == 0:
        # divisor = 1 mantém a fórmula legível e consistente,
        # em vez de ter um 'return' separado que quebraria o fluxo visual da função.
        divisor = 1
        resultado = (Abates + Assistências) / divisor
    else:
        # Divisão normal: Python usa / para float e // para inteiro.
        # Aqui usamos / porque o índice pode ser decimal (ex: 2.33).
        resultado = (Abates + Assistências) / Mortes
    return resultado


# ─── FUNÇÃO DE I/O ──────────────────────────────────────────────────────────────

# Separar a leitura de arquivo em uma função própria é um princípio de design:
# Single Responsibility — cada função faz uma coisa só.
# Isso facilita trocar a fonte de dados no futuro (banco de dados, API, etc.)
# sem mexer no resto do código.
# -> list[dict] é o tipo de retorno: uma lista de dicionários.
# list[dict] é uma type hint genérica disponível a partir do Python 3.9.
def carregar_registros_jogadores(json_file: str) -> list[dict]:
    # 'with' é um context manager: garante que o arquivo será fechado
    # automaticamente ao sair do bloco, mesmo que ocorra uma exceção.
    # É mais seguro que open/close manuais, que podem vazar file handles.
    # 'r' = modo leitura. encoding='utf-8' garante que caracteres especiais
    # (ç, ã, é) sejam lidos corretamente, independente do SO.
    with open(json_file, 'r', encoding='utf-8') as file:
        # json.load() deserializa o arquivo JSON diretamente para Python:
        # arrays JSON → listas Python, objects JSON → dicionários Python,
        # strings → str, numbers → int ou float, true/false → True/False, null → None.
        registros_jogadores = json.load(file)
    return registros_jogadores


# ─── FUNÇÃO DE SANITIZAÇÃO ──────────────────────────────────────────────────────

# Sanitizar dados antes de validar é uma camada de defesa extra.
# O padrão é chamado de "defensive programming": não confiar cegamente nos dados
# de entrada, especialmente vindos de fontes externas (arquivos, APIs, usuários).
# Aqui a escolha arquitetural é corrigir e continuar, não rejeitar e parar.
# Essa decisão depende do contexto: em dados financeiros, rejeitar seria mais seguro.
# Em dados de jogos, corrigir para um valor neutro (0) é razoável.
def sanitizar_registro(registro: dict) -> dict:
    # Lista de campos que precisam ser verificados.
    # Usar uma lista aqui evita repetição de código (DRY: Don't Repeat Yourself).
    # Se um novo campo numérico for adicionado, basta incluir na lista.
    campos_numericos = ['Mortes', 'Abates', 'Assistências']

    # Iteramos sobre os nomes dos campos, não sobre os valores diretamente,
    # porque precisamos tanto do nome (para acessar o dict) quanto do valor.
    for campo in campos_numericos:
        # 'campo in registro' verifica se a chave existe no dicionário.
        # Isso evita KeyError caso o JSON esteja incompleto.
        # O 'and' usa short-circuit evaluation: se a primeira condição for False,
        # a segunda nem é avaliada — evitando erro de chave inexistente.
        if campo in registro and registro[campo] < 0:
            # Avisamos o usuário sobre a correção: transparência no processamento.
            # registro.get('Nickname', '?') usa valor padrão '?' caso a chave não exista,
            # evitando KeyError na mensagem de aviso.
            print(f"[AVISO] '{registro.get('Nickname', '?')}': campo '{campo}' era {registro[campo]}, corrigido para 0.")
            # Mutação direta do dicionário: como dicts são mutáveis em Python,
            # essa alteração reflete fora da função também.
            # Retornamos o registro mesmo assim para deixar o fluxo explícito.
            registro[campo] = 0
    return registro


# ─── PONTO DE ENTRADA ───────────────────────────────────────────────────────────

# __name__ é uma variável especial do Python.
# Quando o arquivo é executado diretamente, __name__ == "__main__".
# Quando o arquivo é importado por outro módulo, __name__ == nome do módulo.
# Esse padrão permite que o arquivo seja tanto executável quanto importável,
# sem rodar código indesejado ao ser importado como biblioteca.
if __name__ == "__main__":
    # os é importado aqui dentro porque só é necessário neste bloco.
    # Importar no escopo local reduz acoplamento e deixa claro onde é usado.
    import os

    # String com o nome do arquivo JSON esperado.
    # Colocar em variável (não hardcodar direto nas chamadas) facilita manutenção:
    # se o nome mudar, altera em um lugar só.
    json_file = "ficha_geral_player.json"

    # os.path.exists() verifica se o caminho existe no sistema de arquivos.
    # Checar antes de abrir evita FileNotFoundError e permite uma mensagem
    # de erro mais clara e amigável para o usuário.
    if os.path.exists(json_file):
        registros_jogadores = carregar_registros_jogadores(json_file)

        # Iteramos sobre cada registro da lista.
        # Cada registro é um dicionário com os dados brutos do JSON.
        for registro in registros_jogadores:
            # try/except é o mecanismo de tratamento de exceções do Python.
            # Separar os tipos de exceção (ValidationError vs Exception genérica)
            # é boa prática: permite respostas diferentes para erros diferentes.
            # Capturar Exception genérica no final é uma rede de segurança —
            # em produção, seria logado em um sistema de monitoramento (ex: Sentry).
            try:
                # Sanitizamos antes de validar: corrige dados ruins e continua.
                # A ordem importa: sanitizar → validar → calcular.
                registro = sanitizar_registro(registro)

                # ** (double splat) desempacota o dicionário como argumentos nomeados.
                # Jogador(**registro) é equivalente a Jogador(Nickname=..., Mortes=..., ...)
                # É um idioma Python muito usado para passar dados dinâmicos para funções/classes.
                jogador = Jogador(**registro)

                # Chamamos a função de cálculo com os atributos validados do objeto.
                # Usar jogador.Mortes em vez de registro['Mortes'] é mais seguro:
                # o objeto já passou pela validação do Pydantic.
                indice = indice_combate(
                    jogador.Mortes,
                    jogador.Abates,
                    jogador.Assistências
                )

                # f-string é a forma moderna de formatação de strings no Python (3.6+).
                # {indice:.2f} formata o float com exatamente 2 casas decimais.
                # Apresentar sempre 2 casas deixa a saída consistente e legível.
                print(f"Jogador: {jogador.Nickname} | Índice de Combate: {indice:.2f}")

            # ValidationError é específico do Pydantic.
            # Capturá-lo separadamente permite uma mensagem contextualizada,
            # sem expor o stack trace completo para o usuário final.
            except ValidationError as e:
                print(f"[ERRO DE VALIDAÇÃO] Jogador '{registro.get('Nickname', '?')}': {e}")

            # Exception é a classe base de todas as exceções não-sistema no Python.
            # Captura qualquer erro inesperado que não seja ValidationError.
            # Manter o loop funcionando (não re-raise) é uma decisão arquitetural:
            # um registro ruim não deve parar o processamento dos demais.
            except Exception as e:
                print(f"[ERRO] {e}")

    else:
        # Mensagem clara indica o problema e o que verificar.
        # Em sistemas reais, isso seria um log de nível ERROR com stack trace.
        print(f"Arquivo '{json_file}' não encontrado. Verifique se o caminho está correto.")