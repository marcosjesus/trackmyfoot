import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def gerar_grafico_final(csv_path):
    df = pd.read_csv(csv_path)

    df['Date'] = pd.to_datetime(df['Date'] + ' 2025', format='%b %d %Y', errors='coerce')
    df['Date_str'] = df['Date'].dt.strftime('%b %d')

    # Ordenar por data
    df = df.sort_values(by='Date')

    unique_keywords = df['description'].unique()
    fig, axs = plt.subplots(len(unique_keywords), 1, figsize=(12, 4 * len(unique_keywords)))

    if len(unique_keywords) == 1:
        axs = [axs]

    for i, keyword in enumerate(unique_keywords):
        subset = df[df['description'] == keyword]
        x = range(len(subset))

        bars_before = axs[i].bar([j - 0.2 for j in x], subset["Value Before"], width=0.4,
                                 label="Value Before", align='center', color='steelblue')
        bars_after = axs[i].bar([j + 0.2 for j in x], subset["Value After"], width=0.4,
                                label="Value After", align='center', color='darkorange')

        axs[i].set_xticks(x)
        axs[i].set_xticklabels(subset["Date_str"], rotation=45, ha='right')
        axs[i].set_title(f"{keyword}")
        axs[i].set_ylabel("Values")
        axs[i].legend()
        axs[i].grid(axis='y')

        for bar in bars_before:
            height = bar.get_height()
            axs[i].annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points", ha='center', fontsize=8)

        for bar in bars_after:
            height = bar.get_height()
            axs[i].annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points", ha='center', fontsize=8)

    plt.tight_layout()

    # Gerar nome dinâmico do arquivo com data e hora
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_image = f"Grafico_{timestamp}.png"
    plt.savefig(output_image)
    plt.close()
    return output_image
