import time
import random
import udp

def receber(con, total, window, loss, registrar):
    timeout = con.gettimeout()
    arquivo = bytearray()
    base = 0          # menor segmento ainda não recebido
    nxt = 0           # próximo segmento a pedir
    envio = {}        # seq -> hora do último REQ
    retx = {}         # seq -> quantas vezes foi retransmitido
    perdido = {}      # seq -> quantas vezes o DATA foi descartado (perda simulada)
    retx_total = 0

    while base < total:
        while nxt < total and nxt < base + window:
            udp.sendREQ(nxt, con)
            envio[nxt] = time.time()
            retx[nxt] = 0
            perdido[nxt] = 0
            nxt += 1

        # timeout individual: reenvia SÓ o segmento que expirou
        resto = envio[base] + timeout - time.time()
        if resto <= 0:
            # timeout gbn envia todos os segmentos da janela novamente
            agora = time.time()
            for s in range(base, nxt):
                udp.sendREQ(s, con)
                envio[s] = agora
                retx[s] += 1
                retx_total += 1
            continue

        pacote = udp.recvDATA(con, resto)
        if pacote is None:
            continue
        seq, payload = pacote

        if seq < base or seq >= nxt:     
            continue
        if seq != base:                   # fora de ordem
            continue
        if random.random() < loss / 100:  # perda simulada
            perdido[seq] += 1
            continue

        # guarda, mesmo em ordem
        agora = time.time()
        rtt_ms = (agora - envio[base]) * 1000
        arquivo.extend(payload)
        #udp.sendACK(base, con)
        registrar(base, len(payload), rtt_ms, timeout * 1000,
                  retx[base], int(retx[base] > 0), perdido[base])
        base += 1

    return arquivo, retx_total