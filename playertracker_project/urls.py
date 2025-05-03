from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard import views
from dashboard.authviews import login_view, signup_view, logout_view
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

# SEO
from django.contrib.sitemaps.views import sitemap
from dashboard.sitemaps import AthleteSitemap
from django.http import HttpResponse

# Sitemap registry
sitemaps = {
    'atletas': AthleteSitemap,
}

# ✅ Fora do i18n_patterns
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),

    # SEO: sitemap.xml e robots.txt
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', lambda r: HttpResponse(
        "User-Agent: *\nDisallow:\nSitemap: https://www.trackmyfoot.com/sitemap.xml",
        content_type="text/plain"
    )),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('', views.landing_view, name='landing'),
    path('upload/', views.index, name='index'),
    path('result/<str:filename>/', views.result, name='result'),
    path('restart/', views.restart_analysis, name='restart'),
    path('buscar-jogadores/', views.buscar_jogadores, name='buscar_jogadores'),
    path('graficos/<int:id>/', views.ver_graficos_atleta, name='ver_graficos'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('perfil/', views.meu_perfil_view, name='meu_perfil'),
)

# Suporte a arquivos de mídia
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
