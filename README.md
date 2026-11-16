**RDT-UnB — Transferência confiável sobre UDP (Grupo 09)**

Implementamos um cliente que baixa arquivos de um servidor UDP com confiabilidade reconstruída na aplicação: número de sequência, timeout, retransmissão, reordenação e checagem de integridade por MD5. São três protocolos: Stop-and-Wait (SAW), Go-Back-N (GBN) e Selective Repeat (SR), com timeout fixo ou adaptativo (EWMA, como no TCP).

* Onde está a entrega final

A versão final do trabalho (código, CSVs de todas as entregas, captura do Wireshark e relatório) está na branch entrega-final, dentro da pasta TRABALHO_FINAL/.

**Estrutura**

TRABALHO_FINAL/
├── client.py              # ponto de entrada (linha de comando)
├── fsm.py                 # sessão: HELLO, SAW, métricas, FIN
├── gbn.py                 # Go-Back-N (timeout fixo ou adaptativo)
├── sr.py                  # Selective Repeat (timeout fixo ou adaptativo)
├── udp.py                 # envio/recebimento de pacotes UDP
├── rdt_diagnostico.py     # testa se o servidor está respondendo
├── graficos.py            # gráficos da Entrega 2
├── organizar_csvs.py      # renomeia/organiza os CSVs no padrão do enunciado
├── resultados_resumo.csv  # uma linha por execução (tempo, vazão, RTT, retransmissões, MD5)
├── CSVs/
│   ├── entrega1/          # SAW
│   ├── entrega2/          # GBN e SR, janelas 4/8/16, perdas 0/5/10%
│   ├── entrega3/          # RTT adaptativo, α/β, arquivo large
│   └── indice_csvs.csv    # o que é cada CSV (protocolo, janela, perda, timeout, α, β, seed, rede)
├── wireshark/
│   ├── captura_gbn_large.pcapng
│   └── flow_graph.pdf
└── relatorio/
    └── RelatorioF_grupo09.pdf

**Testar o servidor**

python3 rdt_diagnostico.py --group grupo09
Deve terminar com os testes OK (PING/PONG, HELLO/OK, REQ/DATA).

**Rodar os protocolos**
python3 client.py --group grupo09 --protocol <saw|gbn|sr> --window x --loss x --seed 1 (caso seja fixo acrescrentar --fixo)
Aonde tem x trocar pelo valor de variável que você deseja.

ex:. python3 client.py --group grupo09 --protocol gbn --window 8 -- loss 5 --seed 1 --fixo
