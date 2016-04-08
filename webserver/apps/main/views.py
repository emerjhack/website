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
from ipware.ip import get_ip

import json
import requests
import os
import errno
import shutil


# http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def tmp_serve_file(location, username, classifier):
    if not location:
        return None

    path = os.path.join(settings.STATIC_SERVE, 'tmp/')
    mkdir_p(path)

    filename, file_extension = os.path.splitext(location)
    tmp_name = sha256((username + classifier).encode('utf-8')).hexdigest()[0:64] + file_extension
    tmp_location = os.path.join(path, tmp_name)

    shutil.copyfile(location, tmp_location)

    return '/static/tmp/' + os.path.basename(tmp_location)


def get_or_400(data, key):
    res = data.get(key)
    if res is None:
        return HttpResponseBadRequest
    return res


def encode_list(l):
    return '-'.join(l).replace(' ', '_')


def decode_list(l):
    return l.replace('_', ' ').split('-')


def user_profile_complete(user, account):
    if not user.first_name:
        return False
    if not user.last_name:
        return False
    if not user.email:
        return False

    if not account.user:
        return False
    if not account.school:
        return False
    if not account.program:
        return False
    if not account.year_of_study:
        return False
    if not account.want_to_do:
        return False
    if not account.resume:
        return False

    return True

# Create your views here.
def index(request):
    if request.user.is_authenticated():
        is_logged_in = True
    else:
        is_logged_in = False
    return render(request, 'index.html', {'is_logged_in': is_logged_in})


def register(request):
    if request.method == 'POST':
        errors = []
        captcha = request.POST.get('g-recaptcha-response')
        if captcha:
            payload = {
                'secret': settings.CAPTCHA_SECRET_KEY,
                'response': captcha
            }
            ip = get_ip(request)
            if ip is not None:
                payload['remoteip'] = ip
            r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
            if not r.json()['success']:
                errors.append('Failure verifying captcha')
        else:
            errors.append('Failure verifying captcha')
        email = get_or_400(request.POST, 'email').lower()
        if email:
            if User.objects.filter(email=email).count() != 0:
                errors.append('Email already in use')
        else:
            errors.append('Email cannot be empty')
        first_name = get_or_400(request.POST, 'first_name')
        if not first_name:
            errors.append('First name cannot be empty')
        last_name = get_or_400(request.POST, 'last_name')
        if not last_name:
            errors.append('Last name cannot be empty')
        password = get_or_400(request.POST, 'pwd')
        if not password:
            errors.append('Password cannot be empty')

        if errors:
            return HttpResponseRedirect('/register/?errors=' + encode_list(errors))

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

    errors = request.GET.get('errors')
    if errors:
        errors = decode_list(errors)
    return render(request, 'register.html', {'errors': errors})


def activation(request):
    token = request.GET.get('token')
    if token:
        account = Account.objects.filter(activation_token=token)
        if account.count() == 0:
            return HttpResponseRedirect('/register/?errors=Invalid_activation_token')
        elif account.count() == 1:
            user = account[0].user
            user.is_active = True
            user.save()
            return HttpResponseRedirect('/login/?status=activated')
        else:
            # We have a token collision ...
            pass
    return HttpResponseRedirect('/register/?errors=Invalid_activation_token')


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

    if account.resume:
        current_resume = os.path.join(settings.MEDIA_ROOT, str(account.resume))
    else:
        current_resume = None

    if account.supporting_files:
        current_supporting_files = os.path.join(settings.MEDIA_ROOT, str(account.supporting_files))
    else:
        current_supporting_files = None

    profile = {
        'status': account.application_status,
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
        resume = request.FILES.get('resume')
        supporting_files = request.FILES.get('supporting_files')
        if resume:
            account.resume = resume
        if supporting_files:
            account.supporting_files = supporting_files

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
            return HttpResponseRedirect('/account/?errors='+encode_list(errors))
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

            delete_resume = request.POST.get('delete_resume')
            delete_supporting_files = request.POST.get('delete_supporting_files')

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

            if delete_resume is not None:
                account.resume = None

            if delete_supporting_files is not None:
                account.supporting_files = None

            if user_profile_complete(user, account):
                if 'save_apply' in request.POST:
                    account.application_status = 'Applied'
                else:
                    account.application_status = 'Profile complete but not applied'
            else:
                account.application_status = 'Profile incomplete'

            user.save()
            account.save()

            # Delete files on disk after saving to prevent deleting files if save wasn't successful.
            if delete_resume is not None:
                os.remove(current_resume)

            if delete_supporting_files is not None:
                os.remove(current_supporting_files)

            if not user_profile_complete(user, account) and 'save_apply' in request.POST:
                return HttpResponseRedirect('/account/?errors=' + encode_list(['Could not apply because your profile is incomplete ... but we saved what you changed', ]))
            return HttpResponseRedirect('/account/?status=success')
    status = request.GET.get('status')
    success = None
    errors = request.GET.get('errors')
    if status == 'success':
        success = 'Account successfully updated.'
    elif errors is not None:
        errors = decode_list(errors)

    return render(request, 'account.html', {
        'current_resume': tmp_serve_file(current_resume, user.username, 'current_resume'),
        'current_supporting_files': tmp_serve_file(current_supporting_files, user.username, 'current_supporting_files'),
        'success': success,
        'errors': errors,
        'profile': profile,
        'schools': settings.SCHOOLS,
        'years': settings.YEARS,
        'is_logged_in': request.user.is_authenticated()
    })
