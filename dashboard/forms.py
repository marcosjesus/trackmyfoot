from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import MensagemTecnico

User = get_user_model()

POSITION_CHOICES = [
    ('', 'Selecione a posição'),  # valor vazio como opção inicial
    ('Goleiro', 'Goleiro'),
    ('Zagueiro', 'Zagueiro'),
    ('Lateral', 'Lateral'),
    ('Meio-campista', 'Meio-campista'),
    ('Atacante', 'Atacante'),
]

GENDER_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Feminino'),
]

class UploadPDFForm(forms.Form):
    pdf_file = forms.FileField(
        label='Select PDF files',
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )

class UserSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.Select(),
        label='Tipo de usuário'
    )
    position = forms.ChoiceField(
        choices=POSITION_CHOICES,
        required=False,
        label='Posição'
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=False,
        label='Gênero'
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Data de nascimento'
    )
    city = forms.CharField(max_length=100, required=False, label='Cidade')
    state = forms.CharField(max_length=100, required=False, label='Estado')
    profile_photo = forms.ImageField(required=False, label='Foto de rosto')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type', 'position', 'gender', 'date_of_birth', 'city', 'state', 'profile_photo']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Criptografa a senha
        if commit:
            user.save()
        return user

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

class MensagemTecnicoForm(forms.ModelForm):
    class Meta:
        model = MensagemTecnico
        fields = ['texto']
        labels = {'texto': 'Mensagem do técnico'}
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Escreva uma mensagem para este atleta'})
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'position', 'gender', 'date_of_birth', 'city', 'state', 'profile_photo']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=GENDER_CHOICES),
            'position': forms.Select(choices=POSITION_CHOICES),
        }
