import time
import random
import udp

def receber(con, total, window, loss, registrar):
    timeout = con.gettimeout()
    arquivo = bytearray()
    buffer = {}       # segmentos recebidos fora de ordem: seq -> payload
    base = 0
    nxt = 0
    envio = {}
    retx = {}
    perdido = {}
    retx_total = 0

    while base < total:
        # enche a janela
        while nxt < total and nxt < base + window:
            udp.sendREQ(nxt, con)
            envio[nxt] = time.time()
            retx[nxt] = 0
            perdido[nxt] = 0
            nxt += 1

        # timeout individual: reenvia SÓ o segmento que expirou
        agora = time.time()
        for s in range(base, nxt):
            if s not in buffer and agora - envio[s] >= timeout:
                udp.sendREQ(s, con)
                envio[s] = agora
                retx[s] += 1
                retx_total += 1

        # espera até o próximo prazo
        pendentes = [envio[s] for s in range(base, nxt) if s not in buffer]
        resto = min(pendentes) + timeout - time.time()
        pacote = udp.recvDATA(con, resto)
        if pacote is None:
            continue
        seq, payload = pacote

        if seq < base or seq >= nxt or seq in buffer:   # duplicata
            continue
        if random.random() < loss / 100:                # perda simulada
            perdido[seq] += 1
            continue

        # guarda, mesmo fora de ordem
        agora = time.time()
        rtt_ms = (agora - envio[seq]) * 1000
        buffer[seq] = payload
        #udp.sendACK(seq, con)
        registrar(seq, len(payload), rtt_ms, timeout * 1000,
                  retx[seq], int(retx[seq] > 0), perdido[seq])

        # reordena: entrega em ordem e desliza a janela
        while base in buffer:
            arquivo.extend(buffer.pop(base))
            base += 1

    return arquivo, retx_total