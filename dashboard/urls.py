from django.urls import path
from . import views, authviews
from .views import meu_perfil_view

urlpatterns = [
    path('', views.landing_view, name='landing'),  # Landing page
    path('upload/', views.index, name='index'),     # Upload de PDF (somente para atleta)
    path('result/<str:filename>/', views.result, name='result'),
    path('restart/', views.restart_analysis, name='restart'),

    # Novas rotas
    path('buscar-jogadores/', views.buscar_jogadores, name='buscar_jogadores'),
    path('graficos/<int:id>/', views.ver_graficos_atleta, name='ver_graficos'),
    path('publico/graficos/<uuid:token>/', views.graficos_publicos_view, name='graficos_publicos'),
    path('compartilhar/', views.compartilhar_graficos_view, name='compartilhar_graficos'),
    path('favoritar/<int:atleta_id>/', views.favoritar_atleta, name='favoritar_atleta'),
    path('remover-favorito/<int:atleta_id>/', views.remover_favorito, name='remover_favorito'),

    # Autenticação
    path('login/', authviews.login_view, name='login'),
    path('signup/', authviews.signup_view, name='signup'),
    path('logout/', authviews.logout_view, name='logout'),
    path('perfil/', meu_perfil_view, name='meu_perfil'),
    
    path('como-funciona/', views.como_funciona_view, name='como_funciona'),
    path('passo-a-passo/', views.passo_a_passo_view, name='passo_a_passo'),
    path('perguntas-frequentes/', views.perguntas_frequentes_view, name='perguntas_frequentes'),
    path('atleta/<slug:slug>/', views.athlete_profile, name='athlete_profile'),
]