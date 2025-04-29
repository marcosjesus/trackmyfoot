import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime
import numpy as np
from math import pi

def gerar_graficos_avancados(csv_path):
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=False)
    df = df.dropna(subset=['Date'])
    df = df.sort_values(by='Date')
    df['Date_str'] = df['Date'].dt.strftime('%b %d')

    # Converte valores para numérico
    df['Value After'] = pd.to_numeric(df['Value After'], errors='coerce')
    df['Value Before'] = pd.to_numeric(df['Value Before'], errors='coerce')

    # ✅ Salvando os gráficos no local correto
    output_dir = os.path.join('static', 'dashboard')
    os.makedirs(output_dir, exist_ok=True)

    img_paths = []

    # 1. Leg Use (%) Over Time
    leg_df = df[df['description'].str.contains('Leg Use', na=False)]
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    for leg in ['L', 'R']:
        leg_data = leg_df[leg_df['description'].str.strip() == f"Leg Use (%) {leg}"]
        leg_data = leg_data.dropna(subset=['Value After'])
        if not leg_data.empty:
            ax1.plot(leg_data['Date'], leg_data['Value After'], label=f'Leg {leg}')
    ax1.set_title("Leg Use (%) Over Time")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Value After")
    ax1.legend()
    img1_path = os.path.join(output_dir, "grafico_leg_use.png")
    fig1.tight_layout()
    fig1.savefig(img1_path)
    img_paths.append(img1_path)
    plt.close(fig1)

    # 2. Barras Before vs After por Data
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    if not df.empty:
        grouped = df.groupby('Date_str')[['Value Before', 'Value After']].mean().dropna()
        if not grouped.empty:
            grouped.plot(kind='bar', ax=ax2)
            ax2.set_title("Média Before vs After por Dia")
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Value")
            ax2.legend()
    img2_path = os.path.join(output_dir, "grafico_before_after.png")
    fig2.tight_layout()
    fig2.savefig(img2_path)
    img_paths.append(img2_path)
    plt.close(fig2)

    # 3. Heatmap por description x Date
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    pivot_df = df.pivot_table(index='description', columns='Date_str', values='Value After', aggfunc='mean')
    if not pivot_df.empty:
        cax = ax3.imshow(pivot_df, aspect='auto', cmap='viridis')
        ax3.set_title("Heatmap - Média de Value After")
        ax3.set_xlabel("Date")
        ax3.set_ylabel("description")
        ax3.set_yticks(np.arange(len(pivot_df.index)))
        ax3.set_yticklabels(pivot_df.index)
        ax3.set_xticks(np.arange(len(pivot_df.columns)))
        ax3.set_xticklabels(pivot_df.columns, rotation=90)
        fig3.colorbar(cax)
    else:
        ax3.text(0.5, 0.5, 'No data to display', ha='center', va='center')
        ax3.set_title("Heatmap - No data")
    img3_path = os.path.join(output_dir, "grafico_heatmap.png")
    fig3.tight_layout()
    fig3.savefig(img3_path)
    img_paths.append(img3_path)
    plt.close(fig3)

    # 4. Radar Chart com último dia válido
    last_day = df['Date'].dropna().max()
    radar_df = df[df['Date'] == last_day].dropna(subset=['description', 'Value After'])
    radar_df = radar_df.drop_duplicates(subset='description')
    categories = radar_df['description'].tolist()
    values = radar_df['Value After'].tolist()
    if categories and values:
        values += values[:1]
        angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
        angles += angles[:1]
        fig4, ax4 = plt.subplots(subplot_kw={'polar': True}, figsize=(8, 6))
        ax4.plot(angles, values, linewidth=1, linestyle='solid')
        ax4.fill(angles, values, alpha=0.3)
        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(categories)
        ax4.set_title(f"Radar Chart - Perfil físico ({last_day.strftime('%b %d')})")
    else:
        fig4, ax4 = plt.subplots(figsize=(8, 6))
        ax4.text(0.5, 0.5, 'No data for radar chart', ha='center', va='center')
        ax4.set_title("Radar Chart - No data")
    img4_path = os.path.join(output_dir, "grafico_radar.png")
    fig4.tight_layout()
    fig4.savefig(img4_path)
    img_paths.append(img4_path)
    plt.close(fig4)    
    return img_paths if img_paths else []