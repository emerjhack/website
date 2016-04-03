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
import json


def get_or_400(data, key):
    res = data.get(key)
    if res is None:
        return HttpResponseBadRequest
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
        email = get_or_400(request.POST, 'email').lower()
        if User.objects.filter(email=email).count() != 0:
            return HttpResponseRedirect('/register/?status=bademail')
        first_name = get_or_400(request.POST, 'first_name')
        last_name = get_or_400(request.POST, 'last_name')
        password = get_or_400(request.POST, 'pwd')

        username = sha256((email + str(randint(-1000000000, 1000000000))).encode('utf-8')).hexdigest()[0:30]
        while User.objects.filter(username=username).count():
            username = sha256((email + str(randint(-1000000000, 1000000000))).encode('utf-8')).hexdigest()[0:30]
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False
        )
        activation_token = sha256((email + str(randint(-1000000000, 1000000000))).encode('utf-8')).hexdigest()[0:64]
        while Account.objects.filter(activation_token=activation_token).count():
            activation_token = sha256((email + str(randint(-1000000000, 1000000000))).encode('utf-8')).hexdigest()[0:64]
        Account(user=user, activation_token=activation_token).save()
        # TODO: Make an HTML email.
        send_mail('Confirm your account', 'Visit: ' + settings.BASE_URL + 'activation/?token=' + activation_token, 'no-reply@outbound.emerjhack.com', [email], fail_silently=False)
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
        account = Account.objects.filter(activation_token=token)
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
        email = get_or_400(request.POST, 'email').lower()
        password = get_or_400(request.POST, 'pwd')
        username = User.objects.filter(email=email)
        remember_me = request.POST.get('remember_me')
        if username.count() == 0:
            return HttpResponseRedirect('/login/?status=badlogin')
        if username.count() == 1:
            user = auth.authenticate(username=username[0], password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    if remember_me is None:
                        request.session.set_expiry(0)
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


# TODO: After changing email, don't commit email change until user confirms new email address
@login_required
def my_account(request):
    user = request.user
    # Switched to get_or_create to fix issues regarding manually created accounts.
    account, created = Account.objects.get_or_create(user=user)
    profile = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'school': account.school,
        'program': account.program,
        'year_of_study': account.year_of_study,
        'want_to_do': account.want_to_do,
        'already_done': account.already_done,
        'supporting_text': account.supporting_text
    }
    old_team = None
    old_team_code = None
    if account.team:
        old_team = account.team
        old_team_code = old_team.code
        profile['team_code'] = old_team_code
        old_team_members = json.loads(old_team.members)
        profile['team_members'] = old_team_members

    if request.method == 'POST':
        errors = []

        first_name = get_or_400(request.POST, 'first_name')
        if not first_name:
            errors.append('You must have a first name')

        last_name = get_or_400(request.POST, 'last_name')
        if not last_name:
            errors.append('You must have a last name')

        email = get_or_400(request.POST, 'email').lower()

        if not email:
            errors.append('You must have an email')
        elif email != user.email and User.objects.filter(email=email).count() != 0:
            errors.append('Email already in use')

        school = get_or_400(request.POST, 'school')
        if school not in settings.SCHOOLS:
            errors.append('Invalid school')

        program = get_or_400(request.POST, 'program')

        year_of_study = get_or_400(request.POST, 'year_of_study')
        if year_of_study not in settings.YEARS:
            errors.append('Invalid year of study')

        team_code = get_or_400(request.POST, 'team_code')
        if team_code and team_code != old_team_code:
            if len(team_code) > 256:
                errors.append('Team code must be less than or equal to 256 character length')
            new_team, created = Team.objects.get_or_create(code=team_code)
            new_team_members = json.loads(new_team.members)
            if len(new_team_members) >= 4:
                errors.append('Team is full')

        if errors:
            return HttpResponseRedirect('/account/?errors='+'-'.join(errors).replace(' ', '_'))
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email

            account.school = school
            account.program = program
            account.year_of_study = year_of_study

            account.want_to_do = get_or_400(request.POST, 'want_to_do')
            account.already_done = get_or_400(request.POST, 'already_done')

            account.supporting_text = get_or_400(request.POST, 'supporting_text')

            if team_code != old_team_code:
                if old_team:
                    # Leave old team
                    account.team = None
                    old_team_members.pop(email, None)
                    if not old_team_members:
                        # Team is now empty, delete the team.
                        old_team.delete()
                    else:
                        old_team.members = json.dumps(old_team_members)
                        old_team.save()
                if team_code:
                    # Join new team
                    new_team_members[email] = first_name + ' ' + last_name
                    new_team.members = json.dumps(new_team_members)
                    new_team.save()
                    account.team = new_team
            user.save()
            account.save()
            return HttpResponseRedirect('/account/?status=success')
    status = request.GET.get('status')
    success = None
    errors = request.GET.get('errors')
    if status == 'success':
        success = 'Account successfully updated.'
    elif errors is not None:
        errors = errors.replace('_', ' ').split('-')
    return render(request, 'account.html', {
        'success': success,
        'errors': errors,
        'profile': profile,
        'schools': settings.SCHOOLS,
        'years': settings.YEARS
    })
