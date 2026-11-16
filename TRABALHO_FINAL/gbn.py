import time
import random
import udp

def receber(con, total, window, loss, registrar):
    timeout = con.gettimeout()

    alpha = 0.125
    beta = 0.25

    rtt_est = None
    dev_rtt = None

    arquivo = bytearray()
    base = 0
    nxt = 0
    envio = {}
    print("to em gbn")
    retx = {}
    perdido = {}
    retx_total = 0

    while base < total:
        while nxt < total and nxt < base + window:
            udp.sendREQ(nxt, con)
            envio[nxt] = time.time()
            retx[nxt] = 0
            perdido[nxt] = 0
            nxt += 1

        resto = envio[base] + timeout - time.time()

        if resto <= 0:
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

        if seq != base:
            continue

        if random.random() < loss / 100:
            perdido[seq] += 1
            continue

        agora = time.time()
        rtt_ms = (agora - envio[base]) * 1000
        rtt = rtt_ms / 1000

        if rtt_est is None:
            rtt_est = rtt
            dev_rtt = rtt / 2
        else:
            dev_rtt = (
                (1 - beta) * dev_rtt
                + beta * abs(rtt - rtt_est)
            )

            rtt_est = (
                (1 - alpha) * rtt_est
                + alpha * rtt
            )

        timeout = rtt_est + 4 * dev_rtt
        con.settimeout(timeout)

        arquivo.extend(payload)

        registrar(
            base,
            len(payload),
            rtt_ms,
            timeout * 1000,
            retx[base],
            int(retx[base] > 0),
            perdido[base],
            rtt_est * 1000
        )

        base += 1

    print("RTT estimado:", rtt_est * 1000)


    return arquivo, retx_total