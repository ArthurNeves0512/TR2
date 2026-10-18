import pandas as pd
import matplotlib.pyplot as plt
import glob

arquivos_csv = glob.glob('metrics_grupo09_saw_*.csv')

for arquivo in arquivos_csv:
    df = pd.read_csv(arquivo)
    
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    # Eixo do RTT (vermelho)
    ax1.set_xlabel('Número do Segmento')
    ax1.set_ylabel('RTT (ms)', color='#d62728')
    ax1.plot(df['segment'], df['rtt_ms'], color='#d62728', alpha=0.7, linewidth=1)
    ax1.tick_params(axis='y', labelcolor='#d62728')
    
    # Eixo do Throughput (azul)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Throughput (kbps)', color='#1f77b4')
    ax2.plot(df['segment'], df['throughput_kbps'], color='#1f77b4', alpha=0.7, linewidth=1)
    ax2.tick_params(axis='y', labelcolor='#1f77b4')
    
    plt.title(f'Desempenho Stop-and-Wait - {arquivo}')
    fig.tight_layout()
    
    nome_imagem = arquivo.replace('.csv', '.png')
    plt.savefig(nome_imagem, dpi=300)
    print(f"Gráfico salvo como: {nome_imagem}")
    plt.close()