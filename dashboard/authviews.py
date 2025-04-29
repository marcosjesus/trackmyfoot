from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import UserSignupForm
from django import forms

# Formulário de login
class LoginForm(forms.Form):
    username = forms.CharField(label='Usuário')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)

# Página de login
def login_view(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing')
            else:
                messages.error(request, "Usuário ou senha inválidos.")

    return render(request, 'dashboard/login.html', {'form': form})

# Página de cadastro
def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('landing')
    else:
        form = UserSignupForm()

    return render(request, 'dashboard/signup.html', {'form': form})

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')
