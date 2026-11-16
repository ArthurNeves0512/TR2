import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("metrics_09_gbn_w4_small_loss60_1794188480.csv")

plt.figure(figsize=(16, 6))

plt.scatter(
    df['segment'],
    df["rtt_ms"],
    c=np.arange(len(df)),
    cmap="viridis",
    s=8,
    alpha=0.8,
    label="RTT medido"
)

plt.plot(
    df['segment'],
    df["rtt_estimated_ms"],
    color="red",
    linewidth=1,
    label="RTT estimado (SRTT)"
)

plt.plot(
    df['segment'],
    df["timeout_ms"],
    color="orange",
    linewidth=1,
    label="Timeout calculado (RTO)"
)

plt.xlabel("Índice do segmento")
plt.ylabel("Tempo (ms)")
plt.title("RTT medido, RTT estimado e Timeout por segmento")

plt.colorbar(label="Índice da amostra")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()