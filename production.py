import time
import logging
import numpy as np
from datetime import datetime

# ── Configuração do sistema de logging ───────────────────────────────────────
# basicConfig define o formato global de todos os logs do sistema.
# level=DEBUG significa que todos os níveis serão exibidos (DEBUG, INFO, WARNING, ERROR, CRITICAL).
# format define o que aparece em cada linha de log:
#   %(asctime)s     → timestamp automático
#   %(levelname)-8s → nível com padding fixo (INFO    , WARNING , etc.)
#   %(name)s        → nome do logger (definido em getLogger abaixo)
#   %(message)s     → a mensagem de fato
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Cada módulo/subsistema tem seu próprio logger com nome próprio.
# Em produção isso permite filtrar logs por subsistema no Datadog/CloudWatch.
logger_sessao   = logging.getLogger("session")
logger_metricas = logging.getLogger("metrics")
logger_dano     = logging.getLogger("damage")
logger_partida  = logging.getLogger("match")
logger_audit    = logging.getLogger("audit")
logger_perf     = logging.getLogger("perf")
logger_cache    = logging.getLogger("cache")
logger_store    = logging.getLogger("store")
logger_numpy    = logging.getLogger("analytics")
logger_pipeline = logging.getLogger("pipeline")


# ═══════════════════════════════════════════════════════════════════════════════
# 1. VARIÁVEIS — Ficha de Jogador
# ═══════════════════════════════════════════════════════════════════════════════

player_id       = "PLR-00421"
username        = "ShadowByte_99"
nivel           = 47
xp_atual        = 83_450
hp_percentual   = 0.68
esta_vivo       = True
regiao          = "SA-EAST-1"
ping_ms         = 24

logger_sessao.info("=" * 40)
logger_sessao.info("FICHA DE JOGADOR — SESSÃO ATIVA")
logger_sessao.info("=" * 40)
logger_sessao.info(f"ID       : {player_id}")
logger_sessao.info(f"Username : {username}")
logger_sessao.info(f"Nível    : {nivel}")
logger_sessao.info(f"XP       : {xp_atual:,}")
logger_sessao.info(f"HP       : {hp_percentual * 100:.0f}%")
logger_sessao.info(f"Vivo     : {esta_vivo}")
logger_sessao.info(f"Região   : {regiao}")
logger_sessao.info(f"Ping     : {ping_ms}ms")

for var, val in [("player_id", player_id), ("nivel", nivel),
                 ("hp_percentual", hp_percentual), ("esta_vivo", esta_vivo)]:
    logger_sessao.debug(f"tipo | {var:15} → {type(val).__name__}")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. FUNÇÕES — KDA e Win Rate
# ═══════════════════════════════════════════════════════════════════════════════

def calcular_kda(kills: int, deaths: int, assists: int) -> float:
    """KDA = (kills + assists) / max(1, deaths) — evita divisão por zero."""
    return round((kills + assists) / max(1, deaths), 2)


def calcular_winrate(vitorias: int, total_partidas: int) -> float:
    """Retorna win rate em percentual. Retorna 0.0 se sem partidas."""
    if total_partidas == 0:
        logger_metricas.warning("calcular_winrate chamado com total_partidas=0")
        return 0.0
    return round((vitorias / total_partidas) * 100, 1)


def classificar_jogador(kda: float, winrate: float) -> str:
    """Classifica o jogador com score ponderado entre KDA e win rate."""
    score = (kda * 0.6) + (winrate / 100 * 10 * 0.4)
    if score >= 8:   return "💎 Diamond"
    elif score >= 6: return "🥇 Platinum"
    elif score >= 4: return "⭐ Gold"
    elif score >= 2: return "🥈 Silver"
    else:            return "🥉 Bronze"


jogadores_teste = [
    ("ShadowByte_99", 340, 87, 210, 178, 220),
    ("NoviceGamer01",  45, 180, 30,  12, 100),
    ("ProSniper_X",   520, 60, 180, 290, 330),
]

logger_metricas.info("-" * 48)
logger_metricas.info(f"{'JOGADOR':<18} {'KDA':>6} {'WINRATE':>9} {'TIER'}")
logger_metricas.info("-" * 48)
for nick, k, d, a, w, t in jogadores_teste:
    kda  = calcular_kda(k, d, a)
    wr   = calcular_winrate(w, t)
    tier = classificar_jogador(kda, wr)
    logger_metricas.info(f"{nick:<18} {kda:>6.2f} {wr:>8.1f}%  {tier}")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. *args e TUPLAS — Processamento de Eventos de Dano
# ═══════════════════════════════════════════════════════════════════════════════

def processar_dano(player_id: str, *eventos_dano) -> dict:
    """Processa todos os eventos de dano de um jogador em uma partida."""
    dano_total = sum(eventos_dano)
    dano_medio = dano_total / len(eventos_dano)
    dano_max   = max(eventos_dano)
    headshots  = sum(1 for d in eventos_dano if d >= 100)

    logger_dano.info(f"[MATCH EVENT] Player: {player_id}")
    logger_dano.debug(f"  hits registrados : {len(eventos_dano)}")
    logger_dano.debug(f"  dados brutos     : {eventos_dano}")
    logger_dano.info(f"  dano total       : {dano_total}")
    logger_dano.info(f"  dano médio/hit   : {dano_medio:.1f}")
    logger_dano.info(f"  maior hit        : {dano_max}")
    logger_dano.info(f"  headshots        : {headshots}")

    return {
        "player": player_id,
        "total":  dano_total,
        "medio":  round(dano_medio, 1),
        "max":    dano_max,
        "hs":     headshots
    }


r1 = processar_dano("PLR-00421", 45, 120, 80, 33, 150, 95, 110, 62, 88)
r2 = processar_dano("PLR-00789", 30, 75, 140, 55)
r3 = processar_dano("PLR-00112", 200, 180, 175, 190, 210, 165, 195, 188, 201, 177, 185, 193)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. **kwargs e DICIONÁRIOS — Registro de Partidas
# ═══════════════════════════════════════════════════════════════════════════════

match_registry = []


def registrar_partida(match_id: str, modo: str, **config) -> dict:
    """Registra uma partida com configurações variáveis por modo de jogo."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    partida = {
        "match_id":  match_id,
        "modo":      modo,
        "timestamp": timestamp,
        **config
    }
    match_registry.append(partida)

    logger_partida.info(f"[MATCH REGISTERED] {match_id} — {modo.upper()}")
    for chave, valor in partida.items():
        logger_partida.debug(f"  {chave:<20} : {valor}")

    return partida


registrar_partida(
    "MATCH-9981", "ranked",
    mapa="Distrito_Neon", jogadores=10, duracao_seg=1847,
    mvp="ShadowByte_99", temporada="S7"
)
registrar_partida(
    "MATCH-9982", "torneio",
    mapa="Bunker_Alpha", times=2, prize_pool_usd=5000,
    transmissao_ao_vivo=True, organizador="ESL_Brazil"
)
registrar_partida(
    "MATCH-9983", "casual",
    mapa="Praia_Caos", jogadores=20, modo_especial="gravidade_reduzida"
)

logger_partida.info(f"[REGISTRY] Total de partidas registradas: {len(match_registry)}")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. DECORADORES — Auditoria e Latência
# ═══════════════════════════════════════════════════════════════════════════════

def audit_log(func):
    """Decorator: registra chamada, argumentos e resultado de toda operação crítica."""
    def wrapper(*args, **kwargs):
        logger_audit.info(f"▶ {func.__name__}() | args={args} kwargs={kwargs}")
        resultado = func(*args, **kwargs)
        logger_audit.info(f"✓ {func.__name__}() → {resultado}")
        return resultado
    return wrapper


def medir_latencia(func):
    """Decorator: mede tempo de execução e alerta se ultrapassar SLA de 100ms."""
    def wrapper(*args, **kwargs):
        inicio    = time.perf_counter()
        resultado = func(*args, **kwargs)
        latencia  = (time.perf_counter() - inicio) * 1000
        if latencia < 100:
            logger_perf.info(f"{func.__name__}() → {latencia:.2f}ms ✅ OK")
        else:
            logger_perf.warning(f"{func.__name__}() → {latencia:.2f}ms ⚠️  SLOW — SLA violado")
        return resultado
    return wrapper


@audit_log
@medir_latencia
def aplicar_ban(player_id: str, motivo: str, duracao_horas: int = 24):
    """Aplica ban em um jogador — operação crítica com audit trail obrigatório."""
    time.sleep(0.002)
    return {"status": "BANNED", "player": player_id, "horas": duracao_horas}


@audit_log
@medir_latencia
def atualizar_ranking(player_id: str, pontos_delta: int):
    """Atualiza MMR do jogador após uma partida."""
    time.sleep(0.001)
    novo_mmr = 1850 + pontos_delta
    return {"player": player_id, "novo_mmr": novo_mmr}


atualizar_ranking("PLR-00421", +25)
atualizar_ranking("PLR-00789", -18)
aplicar_ban("PLR-09999", motivo="cheating_aimbot", duracao_horas=720)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. CACHE — Player Profile Service (Cache-Aside Pattern)
# ═══════════════════════════════════════════════════════════════════════════════

_database = {
    "PLR-00421": {"username": "ShadowByte_99",  "nivel": 47, "rank": "Platinum", "pais": "BR"},
    "PLR-00789": {"username": "DesertEagle_42",  "nivel": 31, "rank": "Gold",     "pais": "AR"},
    "PLR-00112": {"username": "ProSniper_X",     "nivel": 82, "rank": "Diamond",  "pais": "BR"},
    "PLR-00055": {"username": "CasualPlayer_77", "nivel": 12, "rank": "Bronze",   "pais": "CL"},
    "PLR-00300": {"username": "TheCommander",    "nivel": 61, "rank": "Platinum", "pais": "BR"},
}

_cache_perfis   = {}
_access_counter = {}
_cache_hits     = 0
_db_hits        = 0


def buscar_perfil(player_id: str) -> dict | None:
    """Busca perfil com Cache-Aside: verifica cache antes de ir ao banco."""
    global _cache_hits, _db_hits

    _access_counter[player_id] = _access_counter.get(player_id, 0) + 1

    if player_id in _cache_perfis:
        _cache_hits += 1
        logger_cache.debug(f"[CACHE HIT]  {player_id} → {_cache_perfis[player_id]['username']}")
        return _cache_perfis[player_id]

    _db_hits += 1
    time.sleep(0.05)
    perfil = _database.get(player_id)

    if perfil:
        _cache_perfis[player_id] = perfil
        logger_cache.info(f"[DB QUERY]   {player_id} → {perfil['username']} (cacheado)")
    else:
        logger_cache.warning(f"[NOT FOUND]  {player_id} — jogador inexistente no banco")

    return perfil


requisicoes = [
    "PLR-00421", "PLR-00789", "PLR-00421",
    "PLR-00112", "PLR-00055", "PLR-00421",
    "PLR-00300", "PLR-00789", "PLR-00999",
    "PLR-00112", "PLR-00300", "PLR-00112",
]

logger_cache.info("LOBBY — REQUISIÇÕES DE PERFIL")
for pid in requisicoes:
    buscar_perfil(pid)

total_req = len(requisicoes)
logger_cache.info(f"Total requisições : {total_req}")
logger_cache.info(f"DB queries        : {_db_hits}  ({_db_hits/total_req*100:.0f}%)")
logger_cache.info(f"Cache hits        : {_cache_hits}  ({_cache_hits/total_req*100:.0f}%)")
for pid, count in sorted(_access_counter.items(), key=lambda x: -x[1]):
    uname = _database.get(pid, {}).get("username", "desconhecido")
    logger_cache.info(f"  {uname:<22} : {count}x")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. EXCEPTIONS — In-Game Store
# ═══════════════════════════════════════════════════════════════════════════════

class SaldoInsuficienteError(Exception):     pass
class ItemNaoEncontradoError(Exception):     pass
class JogadorBanidoError(Exception):         pass
class LimiteTransacaoDiariaError(Exception): pass


_catalogo = {
    "skin_dragon":   {"nome": "Skin Dragão Ancestral",  "preco": 1500},
    "passe_batalha": {"nome": "Passe de Batalha S7",    "preco": 950},
    "emote_dance":   {"nome": "Emote: Victory Dance",   "preco": 300},
    "arma_gold":     {"nome": "Skin Arma Gold Edition", "preco": 2200},
}

_jogadores_banidos = {"PLR-09999"}


def comprar_item(player_id: str, item_id: str, saldo_gc: int,
                 gasto_hoje: int = 0, limite_diario: int = 5000) -> dict | None:
    """Processa compra na In-Game Store com validações completas."""
    try:
        if player_id in _jogadores_banidos:
            raise JogadorBanidoError(f"Player {player_id} está banido e não pode realizar compras.")

        if item_id not in _catalogo:
            raise ItemNaoEncontradoError(f"Item '{item_id}' não encontrado no catálogo.")

        item  = _catalogo[item_id]
        preco = item["preco"]

        if gasto_hoje + preco > limite_diario:
            raise LimiteTransacaoDiariaError(
                f"Limite diário de {limite_diario} GC atingido. "
                f"Gasto hoje: {gasto_hoje} GC | Tentativa: {preco} GC")

        if saldo_gc < preco:
            raise SaldoInsuficienteError(
                f"Saldo insuficiente: {saldo_gc} GC disponível, {preco} GC necessário.")

        novo_saldo = saldo_gc - preco
        resultado  = {
            "status":     "SUCCESS",
            "player":     player_id,
            "item":       item["nome"],
            "pago":       preco,
            "novo_saldo": novo_saldo
        }
        logger_store.info(f"✅ COMPRA APROVADA | {item['nome']} | {preco} GC | saldo restante: {novo_saldo} GC")
        return resultado

    except JogadorBanidoError         as e: logger_store.error(f"🚫 BANIDO          | {e}")
    except ItemNaoEncontradoError     as e: logger_store.error(f"❌ ITEM INVÁLIDO   | {e}")
    except LimiteTransacaoDiariaError as e: logger_store.warning(f"⛔ LIMITE DIÁRIO  | {e}")
    except SaldoInsuficienteError     as e: logger_store.warning(f"💸 SALDO INSUF.   | {e}")
    finally:
        logger_store.debug(f"[TX LOG] tentativa registrada | player={player_id} item={item_id}")


logger_store.info("IN-GAME STORE — PROCESSANDO TRANSAÇÕES")
comprar_item("PLR-00421", "passe_batalha",      saldo_gc=2000)
comprar_item("PLR-00789", "arma_gold",          saldo_gc=500)
comprar_item("PLR-00112", "item_inexistente_xp", saldo_gc=9999)
comprar_item("PLR-09999", "emote_dance",        saldo_gc=5000)
comprar_item("PLR-00300", "skin_dragon",        saldo_gc=9999, gasto_hoje=4800)


# ═══════════════════════════════════════════════════════════════════════════════
# 8. NUMPY — Match Analytics Dashboard
# ═══════════════════════════════════════════════════════════════════════════════

kills_por_partida = np.array([8, 12, 3, 15, 7, 20, 5, 11, 9, 18,
                               6, 14, 2, 16, 10, 13, 4, 19, 8, 11,
                              17,  6, 12, 3, 14,  9, 21, 7, 15, 10])

dano_por_partida  = np.array([820, 1240, 310, 1580, 740, 2100, 490, 1120, 940, 1870,
                               630, 1450, 210, 1690, 1050, 1380, 420, 1950, 830, 1180,
                              1780,  610, 1290, 340, 1470, 980, 2250, 710, 1560, 1080])

resultado_partida = np.array([1, 1, 0, 1, 0, 1, 0, 1, 1, 1,
                               0, 1, 0, 1, 1, 1, 0, 1, 0, 0,
                               1, 0, 1, 0, 1, 1, 1, 0, 1, 1])

logger_numpy.info("SEASON REPORT — ShadowByte_99")

logger_numpy.info(f"[KILLS] total={kills_por_partida.sum()} | média={kills_por_partida.mean():.1f} | "
                  f"melhor={kills_por_partida.max()} | pior={kills_por_partida.min()} | "
                  f"desvio={kills_por_partida.std():.1f}")

logger_numpy.info(f"[DANO]  total={dano_por_partida.sum():,} | média={dano_por_partida.mean():.0f} | "
                  f"pico={dano_por_partida.max():,}")

total_vitorias = resultado_partida.sum()
total_partidas = len(resultado_partida)
winrate        = (total_vitorias / total_partidas) * 100
logger_numpy.info(f"[WIN RATE] {total_vitorias}/{total_partidas} vitórias → {winrate:.1f}%")

partidas_vitoria_kills = kills_por_partida[resultado_partida == 1]
partidas_derrota_kills = kills_por_partida[resultado_partida == 0]
logger_numpy.info(f"[ANÁLISE] carry(≥15k)={len(kills_por_partida[kills_por_partida >= 15])} | "
                  f"ruins(≤5k)={len(kills_por_partida[kills_por_partida <= 5])} | "
                  f"média kills vitória={partidas_vitoria_kills.mean():.1f} | "
                  f"média kills derrota={partidas_derrota_kills.mean():.1f}")

for p in [25, 50, 75, 90]:
    logger_numpy.info(f"[PERCENTIL P{p:<2}] dano={np.percentile(dano_por_partida, p):.0f}")

correlacao = np.corrcoef(kills_por_partida, dano_por_partida)[0, 1]
logger_numpy.info(f"[CORRELAÇÃO kills↔dano] {correlacao:.3f}")

if winrate >= 60 and kills_por_partida.mean() >= 10:
    logger_numpy.info("🏆 Performance ELITE — Elegível para ranking Diamond")
elif winrate >= 50:
    logger_numpy.info("⭐ Performance ACIMA DA MÉDIA — Mantendo Platinum")
else:
    logger_numpy.warning("📉 Performance ABAIXO DA META — Risco de rebaixamento")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. PIPELINE COMPLETO — Pós-Partida
# ═══════════════════════════════════════════════════════════════════════════════

def pipeline_pos_partida(match_id: str, resultados: list[dict]):
    """Executa o pipeline completo de pós-partida integrando todos os módulos."""
    logger_pipeline.info(f"MATCH OVER — {match_id}")

    for p in resultados:
        logger_pipeline.info(f"processando jogador: {p['username']}")

        kda        = calcular_kda(p["kills"], p["deaths"], p["assists"])
        tier       = classificar_jogador(kda, p["winrate_historico"])
        stats_dano = processar_dano(p["player_id"], *p["hits"])
        delta      = +20 if p["venceu"] else -15

        atualizar_ranking(p["player_id"], delta)
        logger_pipeline.info(f"{p['username']} | KDA={kda} | tier={tier} | dano total={stats_dano['total']}")

    logger_pipeline.info(f"pipeline concluído para {match_id} — {len(resultados)} jogadores processados")


resultado_partida_final = [
    {
        "player_id": "PLR-00421", "username": "ShadowByte_99",
        "kills": 14, "deaths": 3, "assists": 6,
        "hits": [95, 110, 145, 80, 200, 75, 130, 88],
        "winrate_historico": 64.2, "venceu": True
    },
    {
        "player_id": "PLR-00789", "username": "DesertEagle_42",
        "kills": 5, "deaths": 9, "assists": 2,
        "hits": [40, 55, 30, 70, 48],
        "winrate_historico": 41.0, "venceu": False
    },
]

pipeline_pos_partida("MATCH-9981", resultado_partida_final)
logger_pipeline.info("✅ Todos os dados gravados.")