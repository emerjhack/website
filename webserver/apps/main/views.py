from django.conf import settings
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

# TODO: Only allow UW or Laurier emails
def register(request):
    if request.method == 'POST':
        email = get_or_400(request.POST, 'email')
        if User.objects.filter(email = email).count() != 0:
            return HttpResponseRedirect('/register/?status=bademail')
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
        # TODO: Make an HTML email.
        send_mail('Confirm your account', 'Visit: ' + settings.BASE_URL + 'activation/?token=' + activation_token, 'no-reply@outbound.emerjhack.com', [email], fail_silently = False)
        return HttpResponseRedirect('/login/?status=registered')
    error = None
    status = request.GET.get('status')
    if status == 'bademail':
        error = 'Email already in use.'
    elif status == 'badtoken':
        error = 'Confirmation address invalid.'
    return render(request, 'register.html', {'error': error})

def activation(request):
    token = request.GET.get('token')
    if token:
        account = Account.objects.filter(activation_token = token)
        if account.count() == 0:
            return HttpResponseRedirect('/register/?status=badtoken')
        elif account.count() == 1:
            user = account[0].user
            user.is_active = True
            user.save()
            return HttpResponseRedirect('/login/?status=activated')
        else:
            # We have a token collision ...
            pass
    return HttpResponseRedirect('/register/?status=badtoken')

def login(request):
    if request.method == 'POST':
        email = get_or_400(request.POST, 'email')
        password = get_or_400(request.POST, 'pwd')
        username = User.objects.filter(email = email)
        if username.count() == 0:
            return HttpResponseRedirect('/login/?status=badlogin')
        if username.count() == 1:
            user = auth.authenticate(username = username[0], password = password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect('/account/')
                else:
                    return HttpResponseRedirect('/login/?status=unactive')
            else:
                return HttpResponseRedirect('/login/?status=badlogin')
        else:
            # This shouldn't ever happen ...
            # TODO: create admin notification with username.
            return HttpResponseRedirect('/login/?status=badlogin')
    status = request.GET.get('status')
    info = None
    error = None
    if status == 'registered':
        info = 'You have successfully registered. Please check your email for a confirmation email.'
    elif status == 'activated':
        info = 'Your account has been sucessfully activated. Please login with the credentials you used to register.'
    elif status == 'unactive':
        error = 'You are either banned or you did not confirm your account through your email yet.'
    elif status == 'badlogin':
        error = 'Email or password incorrect.'
    return render(request, 'login.html', {'info': info, 'error': error})

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

@login_required
def account(request):
    return render(request, 'account.html', {})
