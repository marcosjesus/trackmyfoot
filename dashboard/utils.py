import os
import matplotlib
matplotlib.use('Agg')  # Use backend sem GUI
import matplotlib.pyplot as plt
import pandas as pd
from django.conf import settings
from dashboard.models import PDFData

# Salva os gráficos diretamente na pasta static/dashboard
UPLOAD_FOLDER = os.path.join(settings.BASE_DIR, 'dashboard', 'static', 'dashboard')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def gerar_grafico_banco(user, tipo=None):
    df = pd.DataFrame.from_records(
        PDFData.objects.filter(user=user).values(
            'description', 'value_before', 'value_after', 'date'
        )
    )
    if df.empty:
        return None

    df['value_before'] = pd.to_numeric(df['value_before'], errors='coerce')
    df['value_after'] = pd.to_numeric(df['value_after'], errors='coerce')
    df.dropna(subset=['value_before', 'value_after'], inplace=True)

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values(by='date')

    if tipo == 'before_after':
        return gerar_grafico_before_after(user)
    elif tipo == 'heatmap':
        return gerar_grafico_heatmap(user)
    elif tipo == 'leg_use':
        return gerar_grafico_leg_use(user)
    elif tipo == 'radar':
        return gerar_grafico_radar(user)
    else:
        grouped = df.groupby(['date'])[['value_before', 'value_after']].sum()
        grouped.plot(kind='bar', figsize=(10, 6))
        plt.title('Valores totais por Data')
        plt.xlabel('Data')
        plt.ylabel('Valores')
        plt.tight_layout()
        filename = f'grafico_banco_{user.id}.png'
        output_path = os.path.join(settings.BASE_DIR, 'dashboard', 'static', 'dashboard', filename)
        plt.savefig(output_path)
        
        plt.close()
        return f'dashboard/static/dashboard/{filename}'

def gerar_grafico_before_after(user):
    df = pd.DataFrame.from_records(
        PDFData.objects.filter(user=user).values(
            'description', 'value_before', 'value_after'
        )
    )
    if df.empty:
        return None

    df['value_before'] = pd.to_numeric(df['value_before'], errors='coerce')
    df['value_after'] = pd.to_numeric(df['value_after'], errors='coerce')
    df.dropna(subset=['value_before', 'value_after'], inplace=True)

    df = df.groupby('description')[['value_before', 'value_after']].mean()
    df.plot(kind='bar', figsize=(10, 6))
    plt.title('Antes e Depois - Média por Métrica')
    plt.xlabel('Métrica')
    plt.ylabel('Valor Médio')
    plt.tight_layout()
    filename = f'grafico_before_after_{user.id}.png'
    output_path = os.path.join(settings.BASE_DIR, 'dashboard', 'static', 'dashboard', filename)
    plt.savefig(output_path)
    plt.close()
    return f'dashboard/static/dashboard/{filename}'

def gerar_grafico_heatmap(user):
    df = pd.DataFrame.from_records(
        PDFData.objects.filter(user=user).values('description', 'date', 'value_after')
    )
    if df.empty:
        return None

    df['value_after'] = pd.to_numeric(df['value_after'], errors='coerce')
    df.dropna(subset=['value_after'], inplace=True)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)

    pivot = df.pivot_table(index='description', columns='date', values='value_after')
    plt.figure(figsize=(10, 6))
    plt.imshow(pivot, aspect='auto', cmap='viridis')
    plt.colorbar(label='Valor Após')
    plt.title('Heatmap de Performance por Data')
    plt.xlabel('Data')
    plt.ylabel('Métrica')
    plt.xticks(ticks=range(len(pivot.columns)), labels=[d.strftime('%Y-%m-%d') for d in pivot.columns], rotation=45)
    plt.tight_layout()
    filename = f'grafico_heatmap_{user.id}.png'
    output_path = os.path.join(settings.BASE_DIR, 'dashboard', 'static', 'dashboard', filename)
    plt.savefig(output_path)
    plt.close()
    return f'dashboard/static/dashboard/{filename}'

def gerar_grafico_leg_use(user):
    df = pd.DataFrame.from_records(
        PDFData.objects.filter(user=user, description__icontains='Leg Use').values('description', 'value_after')
    )
    if df.empty:
        return None

    df['value_after'] = pd.to_numeric(df['value_after'], errors='coerce')
    df.dropna(subset=['value_after'], inplace=True)

    df = df.groupby('description')['value_after'].mean()
    df.plot(kind='pie', autopct='%1.1f%%', figsize=(6, 6))
    plt.title('Distribuição do Uso das Pernas')
    plt.tight_layout()
    filename = f'grafico_leg_use_{user.id}.png'
    output_path = os.path.join(settings.BASE_DIR, 'dashboard', 'static', 'dashboard', filename)
    plt.savefig(output_path)
    plt.close()
    return f'dashboard/static/dashboard/{filename}'

def gerar_grafico_radar(user):
    from math import pi

    df = pd.DataFrame.from_records(
        PDFData.objects.filter(user=user).values('description', 'value_after')
    )
    if df.empty:
        return None

    df['value_after'] = pd.to_numeric(df['value_after'], errors='coerce')
    df.dropna(subset=['value_after'], inplace=True)

    df = df.groupby('description')['value_after'].mean().reset_index()
    if df.empty:
        return None

    labels = df['description'].tolist()
    stats = df['value_after'].tolist()

    angles = [n / float(len(labels)) * 2 * pi for n in range(len(labels))]
    stats += stats[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, stats, linewidth=2)
    ax.fill(angles, stats, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_title('Radar de Performance Média')
    plt.tight_layout()
    filename = f'grafico_radar_{user.id}.png'
    output_path = os.path.join(settings.BASE_DIR, 'dashboard', 'static', 'dashboard', filename)
    plt.savefig(output_path)
    plt.close()
    return f'dashboard/static/dashboard/{filename}'
