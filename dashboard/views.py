from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
import os
import uuid
import sys
from .forms import UploadPDFForm, MensagemTecnicoForm, UserUpdateForm
from PDFReader import process_pdfs_in_folder as reader1_process
from PDFReader2 import process_pdfs_in_folder as reader2_process
from UniqueFile import combine_csv_files
from dashboard.utils import gerar_grafico_banco, gerar_grafico_before_after, gerar_grafico_heatmap, gerar_grafico_leg_use, gerar_grafico_radar
from .models import PDFData, MensagemTecnico, Curtida, GraficoCompartilhado, Favorito, PDFProcessLog
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.translation import get_language
from django.utils import timezone

User = get_user_model()

# View para favoritar atleta
@login_required
def favoritar_atleta(request, atleta_id):
    if request.user.user_type == 'coach':
        atleta = get_object_or_404(User, id=atleta_id, user_type='athlete')
        Favorito.objects.get_or_create(tecnico=request.user, atleta=atleta)
    posicao = request.GET.get('posicao', '')
    return redirect(f'/buscar-jogadores/?posicao={posicao}')

# View para remover favorito
@login_required
def remover_favorito(request, atleta_id):
    if request.user.user_type == 'coach':
        atleta = get_object_or_404(User, id=atleta_id, user_type='athlete')
        Favorito.objects.filter(tecnico=request.user, atleta=atleta).delete()

    posicao = request.GET.get('posicao')
    if posicao:
        return redirect(f'/buscar-jogadores/?posicao={posicao}')
    else:
        return redirect('buscar_jogadores')



# Página inicial personalizada
def landing_view(request):
    if not request.session.get('django_language'):
        request.session['django_language'] = 'pt'
        return redirect('/pt/')  # redireciona para URL com prefixo de idioma
    return render(request, 'dashboard/landing.html')

# View pública de gráficos por token (sem login)
def graficos_publicos_view(request, token):
    compartilhado = get_object_or_404(GraficoCompartilhado, token=token)
    atleta = compartilhado.atleta

    total_curtidas = Curtida.objects.filter(atleta=atleta).count()

    return render(request, 'dashboard/graficos_publicos.html', {
        'atleta': atleta,
        'total_curtidas': total_curtidas,
        'publico': True
    })

# Gerar ou recuperar link compartilhável para o atleta
@login_required
def compartilhar_graficos_view(request):
    compartilhado, created = GraficoCompartilhado.objects.get_or_create(atleta=request.user)
    return redirect('graficos_publicos', token=compartilhado.token)

# View para editar perfil do usuário
@login_required
def meu_perfil_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso.")
            return redirect('meu_perfil')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'dashboard/meu_perfil.html', {'form': form})

# View protegida para upload

@login_required
def index(request):
    if request.method == 'POST':
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('pdf_file')
            upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_path, exist_ok=True)

            # Salvar logs antes de processar
            logs = []
            for file in files:
                if PDFProcessLog.objects.filter(user=request.user, filename=file.name, success=True).exists():
                    messages.warning(request, f'O arquivo "{file.name}" já foi processado com sucesso anteriormente.')
                    continue

                unique_filename = f"{uuid.uuid4()}.pdf"
                pdf_path = os.path.join(upload_path, unique_filename)
                with open(pdf_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                log = PDFProcessLog.objects.create(
                    user=request.user,
                    filename=file.name,
                    success=True,
                    processed_at=timezone.now()
                )
                logs.append((log, pdf_path))

            # Processamento
            reader1_process(upload_path, request.user)
            reader2_process(upload_path, request.user)

            # Atualiza logs após o processamento
            for log, path in logs:
                if os.path.exists(path.replace('.pdf', '.csv')):  # verificação básica
                    log.status = 'sucesso'
                log.save()

            graph_paths = [
                gerar_grafico_banco(request.user, tipo=None),
                gerar_grafico_banco(request.user, tipo='before_after'),
                gerar_grafico_banco(request.user, tipo='heatmap'),
                gerar_grafico_banco(request.user, tipo='leg_use'),
                gerar_grafico_banco(request.user, tipo='radar'),
            ]
            graph_paths = [p for p in graph_paths if p]

            static_dir = os.path.join(settings.BASE_DIR, 'dashboard', 'static', 'dashboard')
            os.makedirs(static_dir, exist_ok=True)
            final_images = []
            for path in graph_paths:
                if os.path.exists(path):
                    final_img = os.path.join(static_dir, os.path.basename(path))
                    final_images.append(os.path.basename(final_img))
                else:
                    print(f"Arquivo não encontrado1: {path}")

            for filename in os.listdir(upload_path):
                if filename.endswith('.csv') or filename.endswith('.pdf'):
                    os.remove(os.path.join(upload_path, filename))

            if final_images:
                return redirect('result', filename=final_images[0])
            else:
                messages.error(request, "Nenhuma imagem foi gerada. Verifique os dados e tente novamente.")
                return redirect('index')
    else:
        form = UploadPDFForm()

    # Recupera os arquivos processados pelo usuário para exibir na tabela
    logs = PDFProcessLog.objects.filter(user=request.user).order_by('-processed_at')
    return render(request, 'dashboard/index.html', {'form': form, 'logs': logs})

@login_required
def result(request, filename):
    static_dir = os.path.join(settings.BASE_DIR, 'dashboard', 'static', 'dashboard')
    images = [f for f in os.listdir(static_dir) if f.startswith('grafico_') and f.endswith('.png')]
    return render(request, 'dashboard/result.html', {'image_files': images, 'user': request.user})

def delete_graph():
    static_dir = os.path.join(settings.BASE_DIR, 'dashboard', 'static', 'dashboard')
    for file in os.listdir(static_dir):
        if file.startswith("Grafico_") and file.endswith(".png"):
            try:
                os.remove(os.path.join(static_dir, file))
            except Exception as e:
                print(f"Erro ao remover gráfico: {e}")

@login_required
def restart_analysis(request):
    delete_graph()
    return redirect('index')

# View para busca de jogadores por posição (somente técnicos)
@login_required
def buscar_jogadores(request):
    if not request.user.user_type == 'coach':
        return redirect('landing')
    
    atletas = User.objects.filter(user_type='athlete')
    posicao = request.GET.get('posicao', '')

    if posicao:
        atletas = atletas.filter(position__iexact=posicao)      
    if request.GET.get('cidade'):
        atletas = atletas.filter(city__icontains=request.GET['cidade'])
    if request.GET.get('estado'):
        atletas = atletas.filter(state__icontains=request.GET['estado'])
    if request.GET.get('genero'):
        atletas = atletas.filter(gender=request.GET['genero'])
    if request.GET.get('ano_nascimento'):
        atletas = atletas.filter(birth_date__year=request.GET['ano_nascimento'])

 

    favoritos_qs = request.user.favoritos.select_related('atleta')
    if posicao:
        favoritos_qs = favoritos_qs.filter(atleta__position__iexact=posicao)
    favoritos_ids = set(favoritos_qs.values_list('atleta_id', flat=True))
    favoritos = favoritos_qs

    atletas = atletas.exclude(id__in=favoritos_ids)

    paginator = Paginator(atletas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/buscar_jogadores.html', {
        'atletas': page_obj,
        'favoritos_ids': favoritos_ids,
        'favoritos': favoritos,
    })

# Visualização dos gráficos de um jogador selecionado
@login_required
def ver_graficos_atleta(request, id):
    atleta = get_object_or_404(User, id=id, user_type='athlete')
    mensagem = None
    form = None
    ja_curtiu = Curtida.objects.filter(atleta=atleta, usuario=request.user).exists()
    total_curtidas = Curtida.objects.filter(atleta=atleta).count()

    if request.user.user_type == 'coach':
        mensagem, _ = MensagemTecnico.objects.get_or_create(tecnico=request.user, atleta=atleta)
        if request.method == 'POST' and 'mensagem_submit' in request.POST:
            form = MensagemTecnicoForm(request.POST, instance=mensagem)
            if form.is_valid():
                form.save()
                messages.success(request, "Mensagem salva com sucesso.")
                return redirect('ver_graficos', id=atleta.id)
    elif request.user.user_type == 'athlete' and request.user.id == atleta.id:
        mensagem = MensagemTecnico.objects.filter(atleta=atleta).first()

    if request.method == 'POST' and 'curtir' in request.POST and not ja_curtiu:
        Curtida.objects.create(atleta=atleta, usuario=request.user)
        return redirect('ver_graficos', id=atleta.id)

    static_dir = os.path.join(settings.BASE_DIR, 'dashboard', 'static', 'dashboard')
    grafico_keys = [
        "grafico_banco",
        "grafico_before_after",
        "grafico_heatmap",
        "grafico_leg_use",
        "grafico_radar",
    ]
    grafico_exists = {
        f"{key}_exists": os.path.exists(os.path.join(static_dir, f"{key}_{atleta.id}.png")) for key in grafico_keys
    }

    context = {
        'atleta': atleta,
        'mensagem': mensagem,
        'form': form,
        'ja_curtiu': ja_curtiu,
        'total_curtidas': total_curtidas,
        **grafico_exists
    }

    return render(request, 'dashboard/graficos_jogador.html', context)

def como_funciona_view(request):
    return render(request, 'dashboard/como_funciona.html')

def passo_a_passo_view(request):
    idioma = get_language() or 'pt'
    if idioma not in ['pt', 'en', 'es']:
        idioma = 'pt'
    return render(request, f'dashboard/passo_a_passo_{idioma}.html')

def perguntas_frequentes_view(request):
    return render(request, 'dashboard/perguntas_frequentes.html')


def athlete_profile(request, slug):
    jogador = get_object_or_404(User, slug=slug, user_type='athlete')
    return render(request, 'athlete_profile.html', {'jogador': jogador})