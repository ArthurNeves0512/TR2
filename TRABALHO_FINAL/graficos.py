import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# guarda os gráficos individuais de cada arquivo CSV gerado pelo FSM (metrics_*.csv)
arquivos_csv = glob.glob('metrics_grupo09_*.csv')

for arquivo in arquivos_csv:
    df = pd.read_csv(arquivo)
    df = df.sort_values('segment')   
    
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    # Eixo do RTT (rosa)
    ax1.set_xlabel('Número do Segmento')
    ax1.set_ylabel('RTT (ms)', color="#ed24bb")
    ax1.plot(df['segment'], df['rtt_ms'], color="#ed24bb", alpha=0.7, linewidth=1)
    ax1.tick_params(axis='y', labelcolor="#ed24bb")
    
    # Eixo do Throughput (roxo)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Throughput (kbps)', color="#a01fb4")
    ax2.plot(df['segment'], df['throughput_kbps'], color="#a01fb4", alpha=0.7, linewidth=1)
    ax2.tick_params(axis='y', labelcolor="#a01fb4")
    
    # Extrai o protocolo do nome do arquivo para o título
    protocolo = arquivo.split('_')[2].upper()
    plt.title(f'Desempenho {protocolo} - {arquivo}')
    fig.tight_layout()
    
    nome_imagem = arquivo.replace('.csv', '.png')
    plt.savefig(nome_imagem, dpi=300)
    plt.close()

print(f"[{len(arquivos_csv)}] Gráficos individuais gerados.")

# Graficos comparativos - throughput médio e retransmissões
if os.path.exists("resultados_resumo.csv"):
    df_resumo = pd.read_csv("resultados_resumo.csv")
    # se você rodou o mesmo cenário mais de uma vez, tira a média
    df_resumo = df_resumo.groupby(['file', 'protocol', 'window', 'loss'], as_index=False).mean(numeric_only=True)
    
    # Gráfico de Throughput no cenário Ideal (0% Perda)
    df_0loss = df_resumo[df_resumo['loss'] == 0.0]
    plt.figure(figsize=(8, 5))
    for proto in ['saw', 'gbn', 'sr']:
        df_proto = df_0loss[df_0loss['protocol'] == proto].sort_values('window')
        if not df_proto.empty:
            plt.plot(df_proto['window'], df_proto['throughput_medio_kbps'], marker='o', label=proto.upper())

    plt.title("Throughput vs Tamanho da Janela (Sem Perda - 0%)")
    plt.xlabel("Tamanho da Janela")
    plt.ylabel("Throughput Médio (kbps)")
    plt.xticks([1, 4, 8, 16])
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.savefig("comparativo_throughput_0perda.png", dpi=300)
    plt.close()

    # Cenários com falhas (5% e 10% de perda)
    for perda in [5.0, 10.0]:
        df_loss = df_resumo[df_resumo['loss'] == perda]
        df_saw_loss = df_loss[df_loss['protocol'] == 'saw']

        plt.figure(figsize=(8, 5))
        for proto in ['gbn', 'sr']:
            df_proto = df_loss[df_loss['protocol'] == proto].sort_values('window')
            if not df_proto.empty:
                plt.plot(df_proto['window'], df_proto['throughput_medio_kbps'], marker='s', label=f"{proto.upper()} ({perda:g}% Perda)")

        if not df_saw_loss.empty:
            plt.scatter(df_saw_loss['window'], df_saw_loss['throughput_medio_kbps'], color='red', label=f"SAW ({perda:g}% Perda)", zorder=5)

        plt.title(f"Throughput vs Tamanho da Janela (Com {perda:g}% de Perda)")
        plt.xlabel("Tamanho da Janela")
        plt.ylabel("Throughput Médio (kbps)")
        plt.xticks([1, 4, 8, 16])
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.savefig(f"comparativo_throughput_{perda:g}perda.png", dpi=300)
        plt.close()

        # Retransmissões do GBN vs SR
        df_retx = df_loss[df_loss['protocol'].isin(['gbn', 'sr'])]
        if not df_retx.empty:
            df_pivot = df_retx.pivot(index='window', columns='protocol', values='retransmissoes')
            df_pivot.plot(kind='bar', figsize=(8, 5))

            plt.title(f"Total de Retransmissões: GBN vs SR ({perda:g}% de Perda)")
            plt.xlabel("Tamanho da Janela")
            plt.ylabel("Quantidade de Retransmissões")
            plt.xticks(rotation=0)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.legend(title="Protocolo")
            plt.tight_layout()
            plt.savefig(f"comparativo_retransmissoes_{perda:g}perda.png", dpi=300)
            plt.close()

    # Tabela comparativa do protocolo x janela x perda 
    ordem = [('saw', 1), ('gbn', 4), ('gbn', 8), ('gbn', 16), ('sr', 4), ('sr', 8), ('sr', 16)]
    medias = df_resumo.set_index(['protocol', 'window', 'loss'])
    linhas = []
    for proto, janela in ordem:
        linha = {'Protocolo': proto.upper(), 'Janela': janela}
        for perda in [0.0, 5.0, 10.0]:
            if (proto, janela, perda) in medias.index:
                m = medias.loc[(proto, janela, perda)]
                linha[f'{perda:g}% perda'] = (f"{m['throughput_medio_kbps']:.1f} kbps / "
                                              f"{m['retransmissoes']:.0f} retx / {m['tempo_total_s']:.1f} s")
            else:
                linha[f'{perda:g}% perda'] = '—'
        linhas.append(linha)
    tabela = pd.DataFrame(linhas)
    tabela.to_csv("tabela_comparativa.csv", index=False, encoding='utf-8-sig')
    print()
    print("Tabela comparativa (throughput médio / retransmissões / tempo total):")
    print(tabela.to_string(index=False))

    print("[3] Gráficos comparativos (Entrega 2) gerados com sucesso.")
else:
    print("Aviso: 'resultados_resumo.csv' não encontrado. Rode os testes primeiro.")

# gráficos comparativos por segmento (GBN vs SR) para janela 8 e 16, perdas de 5% e 10%
def ultimo_csv(proto, janela, perda):
    achados = glob.glob(f'metrics_grupo09_{proto}_w{janela}_small_loss{perda:g}_*.csv')
    return max(achados) if achados else None   

for perda in [5.0, 10.0]:
    for janela in [8, 16]:
        arq_gbn = ultimo_csv('gbn', janela, perda)
        arq_sr = ultimo_csv('sr', janela, perda)
        if not arq_gbn or not arq_sr:
            continue

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        for nome, arq, cor in [('GBN', arq_gbn, "#a90821"), ('SR', arq_sr, "#ed1b7a")]:
            d = pd.read_csv(arq).sort_values('segment')
            ax1.plot(d['segment'], d['throughput_kbps'], color=cor, alpha=0.6, linewidth=0.8, label=nome)
            ax2.plot(d['segment'], d['retransmissions'].cumsum(), color=cor, linewidth=1.5, label=nome)

        ax1.set_ylabel('Throughput por segmento (kbps)')
        ax1.set_title(f'GBN vs SR por segmento (janela {janela}, {perda:g}% de perda)')
        ax1.grid(True, linestyle='--', alpha=0.5)
        ax1.legend()
        ax2.set_xlabel('Número do Segmento')
        ax2.set_ylabel('Retransmissões acumuladas')
        ax2.grid(True, linestyle='--', alpha=0.5)
        ax2.legend()
        fig.tight_layout()
        plt.savefig(f'segmentos_gbn_vs_sr_w{janela}_loss{perda:g}.png', dpi=300)
        plt.close()

# quantas retransmissões por perda simulada
print()
print("Questão (b): 10% de perda, janela 16")
for proto in ['gbn', 'sr']:
    arq = ultimo_csv(proto, 16, 10.0)
    if arq:
        d = pd.read_csv(arq)
        erros = int(d['simulated_loss'].sum())
        retx = int(d['retransmissions'].sum())
        if erros:
            print(f"  {proto.upper()}: {erros} perdas simuladas, {retx} retransmissões "
                  f"-> {retx / erros:.1f} retransmissões por erro  ({arq})")