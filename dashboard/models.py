from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid
from django.utils import timezone
from django.utils.text import slugify

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('athlete', 'Atleta'),
        ('coach', 'Técnico'),
    )
    GENDER_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    )

    email = models.EmailField(unique=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='athlete')
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.user_type == 'athlete':
            base_slug = slugify(self.username)
            count = 1
            slug = base_slug
            while CustomUser.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)
        
class PDFKeyword(models.Model):
    description = models.CharField(max_length=255, unique=True)
    pattern = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.description


class PDFData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, null=True, blank=True)
    value_before = models.CharField(max_length=100, null=True, blank=True)
    value_after = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    playing_time = models.CharField(max_length=100, null=True, blank=True)
    start_time = models.CharField(max_length=100, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)

    # >>> NOVOS CAMPOS <<<
    activity_type = models.CharField(  # Tipo da atividade: 'Jogo' ou 'Treinamento'
        max_length=20,
        choices=[('Game', 'Game'), ('Training', 'Training')],
        default='Game'
    )
    session_number = models.PositiveIntegerField(default=1)  # 1 para primeiro jogo/treino, 2 para segundo, etc.

    class Meta:
        indexes = [
            models.Index(fields=['user', 'description', 'date', 'activity_type', 'session_number']),
        ]

    def __str__(self):
        return f"{self.user} - {self.description} ({self.date}) [{self.activity_type} {self.session_number}]"


class MensagemTecnico(models.Model):
    tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    atleta = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mensagens_recebidas')
    texto = models.TextField()
    data_envio = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('tecnico', 'atleta')

    def __str__(self):
        return f"Mensagem de {self.tecnico} para {self.atleta}"


class Curtida(models.Model):
    atleta = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='curtidas_recebidas')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='curtidas_feitas')
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('atleta', 'usuario')

    def __str__(self):
        return f"{self.usuario} curtiu {self.atleta}"


class GraficoCompartilhado(models.Model):
    atleta = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Link público de {self.atleta}"


class Favorito(models.Model):
    tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favoritos')
    atleta = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorito_por')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tecnico', 'atleta')

    def __str__(self):
        return f"{self.tecnico} favoritou {self.atleta}"
    
class PDFProcessLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    processed_at = models.DateTimeField(default=timezone.now)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.filename} - {'Sucesso' if self.success else 'Erro'}"