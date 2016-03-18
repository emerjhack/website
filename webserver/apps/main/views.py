from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import auth
from .forms import *
from hashlib import sha256
from django.core.mail import send_mail
from random import randint
from .models import *

# Create your views here.
def index(request):
    if request.user.is_authenticated():
        is_logged_in = True
    else:
        is_logged_in = False
    return render(request, 'index.html', {'is_logged_in': is_logged_in})

def register(request):
    error = []
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            error = []
            if form.cleaned_data['password'] != form.cleaned_data['password2']:
                error.append('Passwords do not match')
            if form.cleaned_data['email'] != form.cleaned_data['email2']:
                error.append('Emails do not match')
            if User.objects.filter(email = form.cleaned_data['email']).count() != 0:
                error.append('Email already in use')

            if len(error):
                form = NameForm()
            else:
                username = sha256(form.cleaned_data['email'] + str(randint(-1000000000,1000000000))).hexdigest()[0:30]
                while User.objects.filter(username = username).count():
                    username = sha256(username + str(randint(-1000000000,1000000000))).hexdigest()[0:30]
                user = User.objects.create_user(
                    username = username,
                    email = form.cleaned_data['email'],
                    password = form.cleaned_data['password'],
                    first_name = form.cleaned_data['first_name'],
                    last_name = form.cleaned_data['last_name'],
                    is_active = False
                )
                activation_token = sha256(form.cleaned_data['email'] + str(randint(-1000000000,1000000000))).hexdigest()[0:64]
                while Account.objects.filter(activation_token = activation_token).count():
                    activation_token = sha256(form.cleaned_data['email'] + str(randint(-1000000000,1000000000))).hexdigest()[0:64]
                Account(user=user, activation_token=activation_token).save()
                send_mail('Confirm your account', 'Visit: https://www.emerjhack.com/activation/' + activation_token, 'no-reply@emerjhack.com', [form.cleaned_data['email']], fail_silently=False)
                return HttpResponseRedirect('/')
    else:
        form = NameForm()

    return render(request, 'register.html', {'form': form, 'error': error})

def activation(request, token):
    account = Account.objects.filter(activation_token = token)
    if account.count() == 1:
        user = account[0].user
        user.is_active = True
        user.save()
    return render(request, 'activation.html', {})

def login(request):
    error = []
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = User.objects.filter(email = form.cleaned_data['email'])
            if username.count() == 1:
                user = auth.authenticate(username=username[0], password=form.cleaned_data['password'])
                if user is not None:
                    if user.is_active:
                        auth.login(request, user)
                        return HttpResponseRedirect('/')
                    else:
                        form = LoginForm()
                        error = ['You are either banned or you did not confirm your account through your email yet.']
                else:
                    form = LoginForm()
                    error = ['Email or password incorrect']
            else:
                form = LoginForm()
                error = ['Email or password incorrect']
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'error': error})

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

def me(request):
    return render(request, 'me.html', {})
