from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.models import User
from django.contrib import auth
from hashlib import sha256
from django.core.mail import send_mail
from random import randint
from .models import *
from django.contrib.auth.decorators import login_required

def get_or_400(data, key):
    res = data.get(key)
    if res is None: return HttpResponseBadRequest
    return res

# Create your views here.
def index(request):
    if request.user.is_authenticated():
        is_logged_in = True
    else:
        is_logged_in = False
    return render(request, 'index.html', {'is_logged_in': is_logged_in})

def register(request):
    if request.method == 'POST':
        email = get_or_400(request.POST, 'email')
        if User.objects.filter(email = email).count() != 0:
            return render(request, 'register.html', {'error': 'Email already in use'})
        first_name = get_or_400(request.POST, 'first_name')
        last_name = get_or_400(request.POST, 'last_name')
        password = get_or_400(request.POST, 'pwd')

        username = sha256((email + str(randint(-1000000000, 1000000000))).encode('utf-8')).hexdigest()[0:30]
        while User.objects.filter(username = username).count():
            username = sha256((email + str(randint(-1000000000, 1000000000))).encode('utf-8')).hexdigest()[0:30]
        user = User.objects.create_user(
            username = username,
            email = email,
            password = password,
            first_name = first_name,
            last_name = last_name,
            is_active = False
        )
        activation_token = sha256((email + str(randint(-1000000000, 1000000000))).encode('utf-8')).hexdigest()[0:64]
        while Account.objects.filter(activation_token = activation_token).count():
            activation_token = sha256((email + str(randint(-1000000000, 1000000000))).encode('utf-8')).hexdigest()[0:64]
        Account(user = user, activation_token = activation_token).save()
        send_mail('Confirm your account', 'Visit: https://emerjhack.com/activation/' + activation_token, 'no-reply@outbound.emerjhack.com', [email], fail_silently = False)
        return HttpResponseRedirect('/')

    return render(request, 'register.html', {})

def activation(request, token):
    account = Account.objects.filter(activation_token = token)
    if account.count() == 1:
        user = account[0].user
        user.is_active = True
        user.save()
    return render(request, 'index.html', {})

def login(request):
    error = []
    if request.method == 'POST':
        email = get_or_400(request.POST, 'email')
        password = get_or_400(request.POST, 'pwd')
        username = User.objects.filter(email = email)
        if username.count() == 1:
            user = auth.authenticate(username = username[0], password = password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect('/')
                else:
                    return render(request, 'login.html', {'error': 'You are either banned or you did not confirm your account through your email yet.'})
            else:
                return render(request, 'login.html', {'error': 'Email or password incorrect'})
        else:
            # This shouldn't ever happen ...
            # TO DO: create admin notification with username.
            return render(request, 'login.html', {'error': 'Email or password incorrect'})
    return render(request, 'login.html', {})

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

@login_required
def account(request):
    return render(request, 'account.html', {})
