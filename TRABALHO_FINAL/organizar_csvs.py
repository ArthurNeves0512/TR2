"""
Organiza os CSVs do TR2 para a entrega final.

Uso (dentro da pasta TRABALHO_FINAL):
    python3 organizar_csvs.py            -> só MOSTRA o que vai fazer (não mexe em nada)
    python3 organizar_csvs.py --aplicar  -> move e renomeia de verdade
"""
import csv
import glob
import hashlib
import os
import re
import shutil
import sys
from datetime import datetime

APLICAR = "--aplicar" in sys.argv
if os.path.exists("CSVs/indice_csvs.csv"):
    print("Os CSVs já foram organizados (CSVs/indice_csvs.csv existe). Nada a fazer.")
    sys.exit(0)
GRUPO = "grupo09"

# Rodadas da Entrega 3 usadas no relatório, identificadas pelo total de retransmissões
# valor: (descrição, perda %, alpha, beta, seed, rede)
ENTREGA3 = {
    915:   ("fixo x adaptativo (5G)",      5, None,  None, 1, "5G"),
    1235:  ("fixo x adaptativo (5G)",      5, 0.125, 0.25, 1, "5G"),
    1256:  ("fixo x adaptativo",           5, None,  None, 2, "UnB Wireless"),
    1640:  ("fixo x adaptativo / alfa-beta", 5, 0.125, 0.25, 2, "UnB Wireless"),
    2120:  ("fixo x adaptativo",          10, None,  None, 2, "UnB Wireless"),
    3048:  ("fixo x adaptativo",          10, 0.125, 0.25, 2, "UnB Wireless"),
    3104:  ("fixo x adaptativo",          10, None,  None, 1, "UnB Wireless"),
    5984:  ("fixo x adaptativo",          10, 0.125, 0.25, 1, "UnB Wireless"),
    2435:  ("alfa-beta",                   5, 0.05,  0.25, 2, "UnB Wireless"),
    5104:  ("alfa-beta",                   5, 0.05,  0.25, 1, "UnB Wireless"),
    3843:  ("alfa-beta",                   5, 0.5,   0.25, 1, "UnB Wireless"),
    4584:  ("alfa-beta",                   5, 0.5,   0.25, 2, "UnB Wireless"),
    1027:  ("alfa-beta",                   5, 0.125, 0.1,  1, "UnB Wireless"),
    1016:  ("alfa-beta",                   5, 0.125, 0.1,  2, "UnB Wireless"),
    1107:  ("alfa-beta",                   5, 0.125, 0.5,  1, "UnB Wireless"),
    3640:  ("alfa-beta",                   5, 0.125, 0.5,  2, "UnB Wireless"),
    360:   ("Wireshark (arquivo large)",   0, None,  None, None, "residencial"),
    208:   ("visao integrada (large)",     0, None,  None, None, "residencial"),
    36567: ("visao integrada (large)",     0, 0.125, 0.25, None, "residencial"),
    32:    ("visao integrada (large)",     0, None,  None, None, "residencial"),
}


def md5(caminho):
    with open(caminho, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def ler(caminho):
    """Lê um CSV de métricas e devolve um resumo, ou None se não for um CSV de métricas válido."""
    try:
        with open(caminho, newline="") as f:
            linhas = list(csv.DictReader(f))
    except Exception:
        return None
    if not linhas or "segment" not in linhas[0] or "timestamp" not in linhas[0]:
        return None
    try:
        segs = [int(l["segment"]) for l in linhas]
        inicio = datetime.fromisoformat(linhas[0]["timestamp"])
        timeouts = {round(float(l.get("timeout_ms") or 0), 1) for l in linhas}
        retx = sum(int(float(l.get("retransmissions") or 0)) for l in linhas)
        sim = sum(int(float(l.get("simulated_loss") or 0)) for l in linhas)
        proto = (linhas[0].get("protocol") or "").strip().lower()
        janela = int(float(linhas[0].get("window_size") or 1))
    except Exception:
        return None
    if proto not in ("saw", "gbn", "sr"):
        return None
    total = max(segs) + 1
    return {
        "proto": proto, "janela": janela, "inicio": inicio, "retx": retx,
        "arquivo_srv": "large" if total > 5000 else "small",
        "completo": total in (2048, 20480) and len(set(segs)) == total,
        "timeout": f"fixo {min(timeouts):g} ms" if len(timeouts) == 1 else "adaptativo",
        "perda_estimada": round(100 * sim / total),
    }


def perda_do_nome(nome):
    m = re.search(r"loss(\d+)", nome)
    return int(m.group(1)) if m else None


arquivos = sorted(set(glob.glob("*.csv") + glob.glob("CSVs/*.csv") + glob.glob("entrega3/*.csv")
                      + glob.glob("rascunhos/*.csv") + glob.glob("CSVs/entrega*/*.csv")))
ignorar = {"resultados_resumo.csv", "tabela_comparativa.csv", "CSVs/indice_csvs.csv"}

vistos = {}
plano = []      # (origem, destino, linha_do_indice ou None)
for caminho in arquivos:
    if os.path.basename(caminho) in ignorar or caminho in ignorar:
        continue
    r = ler(caminho)
    if r is None:
        continue
    h = md5(caminho)
    if h in vistos:
        plano.append((caminho, os.path.join("rascunhos", "duplicado_" + os.path.basename(caminho)), None))
        continue
    vistos[h] = caminho

    entrega = None
    info = {}
    if r["inicio"].month == 10:                       # Entregas 1 e 2 foram em outubro
        if caminho.startswith("CSVs/") and r["completo"]:
            entrega = 1 if r["proto"] == "saw" else 2
            info = {"perda": perda_do_nome(caminho) if perda_do_nome(caminho) is not None else r["perda_estimada"],
                    "rede": "residencial", "uso": "Entrega 1" if entrega == 1 else "Entrega 2"}
    elif r["completo"] and r["retx"] in ENTREGA3 and r["proto"] in ("gbn", "sr") and ("large" in ENTREGA3[r["retx"]][0]) == (r["arquivo_srv"] == "large"):
        desc, perda, a, b, seed, rede = ENTREGA3[r["retx"]]
        entrega = 3
        info = {"perda": perda, "alpha": a, "beta": b, "seed": seed, "rede": rede, "uso": desc}

    if entrega is None:
        plano.append((caminho, os.path.join("rascunhos", os.path.basename(caminho)), None))
        continue

    novo = f"metrics_{GRUPO}_{r['proto']}_{r['inicio']:%Y%m%d_%H%M%S}.csv"
    destino = os.path.join("CSVs", f"entrega{entrega}", novo)
    linha = {
        "arquivo": f"entrega{entrega}/{novo}", "entrega": entrega, "protocolo": r["proto"],
        "janela": r["janela"], "arquivo_servidor": r["arquivo_srv"], "perda_simulada_pct": info.get("perda"),
        "timeout": r["timeout"], "alpha": info.get("alpha") or "", "beta": info.get("beta") or "",
        "seed": info.get("seed") or "", "rede": info.get("rede"), "retransmissoes": r["retx"],
        "inicio": r["inicio"].strftime("%Y-%m-%d %H:%M:%S"), "uso_no_relatorio": info.get("uso"),
        "nome_original": os.path.basename(caminho),
    }
    plano.append((caminho, destino, linha))

# ---------- relatório do que vai acontecer ----------
indice = [l for _, _, l in plano if l]
indice.sort(key=lambda l: (l["entrega"], l["inicio"]))
print(f"\n{'ORIGEM':60} -> DESTINO")
for origem, destino, linha in sorted(plano, key=lambda p: p[1]):
    print(f"{origem[:60]:60} -> {destino}")

print("\n=== CONFERÊNCIA DOS CENÁRIOS ===")
def tem(cond):
    return sum(1 for l in indice if cond(l))
checks = [
    ("Entrega 1: SAW 0%",  lambda l: l["entrega"] == 1 and l["perda_simulada_pct"] == 0),
    ("Entrega 1: SAW 5%",  lambda l: l["entrega"] == 1 and l["perda_simulada_pct"] == 5),
    ("Entrega 1: SAW 10%", lambda l: l["entrega"] == 1 and l["perda_simulada_pct"] == 10),
]
for p in ("gbn", "sr"):
    for w in (4, 8, 16):
        for perda in (0, 5, 10):
            checks.append((f"Entrega 2: {p.upper()} janela {w:2} perda {perda:2}%",
                           lambda l, p=p, w=w, perda=perda: l["entrega"] == 2 and l["protocolo"] == p
                           and l["janela"] == w and l["perda_simulada_pct"] == perda))
for retx, (desc, perda, a, b, seed, rede) in sorted(ENTREGA3.items(), key=lambda x: (x[1][0], x[1][1])):
    modo = "fixo" if a is None else f"adapt a={a} b={b}"
    checks.append((f"Entrega 3: {desc}, {perda}%, {modo}, seed {seed}, {rede}",
                   lambda l, retx=retx: l["entrega"] == 3 and l["retransmissoes"] == retx))
faltando = 0
for nome, cond in checks:
    n = tem(cond)
    print(("  OK      " if n else "  FALTA   ") + nome)
    faltando += (n == 0)
print(f"\nCSVs na entrega: {len(indice)} | cenários faltando: {faltando}")

if not APLICAR:
    print("\nNada foi alterado. Confira a lista e rode de novo com --aplicar para mover os arquivos.")
    sys.exit(0)

# ---------- aplicar ----------
for origem, destino, linha in plano:
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    if os.path.exists(destino):
        destino = destino.replace(".csv", "_2.csv")
    shutil.move(origem, destino)
    png = os.path.splitext(origem)[0] + ".png"          # gráfico da mesma rodada, se existir
    if os.path.exists(png):
        shutil.move(png, os.path.splitext(destino)[0] + ".png")
with open("CSVs/indice_csvs.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(indice[0].keys()))
    w.writeheader()
    w.writerows(indice)
print("\nPronto! Arquivos movidos e CSVs/indice_csvs.csv criado.")