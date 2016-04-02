from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Team(models.Model):
    code = models.CharField(max_length=256)
    members = models.TextField(default='{}')
    def __str__(self):
        return self.code

class Account(models.Model):
    user = models.OneToOneField(User)
    team = models.ForeignKey(Team, null=True, default=None)
    activation_token = models.CharField(max_length=64)

    school = models.CharField(max_length=64, blank=True, default='')
    program = models.CharField(max_length=64, blank=True, default='')
    year_of_study = models.CharField(max_length=64, blank=True, default='')

    want_to_do = models.TextField(blank=True, default='')
    already_done = models.TextField(blank=True, default='')

    resume = models.FileField(upload_to='uploaded/', blank=True, null=True)
    supporting_files = models.FileField(upload_to='uploaded/', blank=True, null=True)
    supporting_text = models.TextField(blank=True, default='')

    application_status = models.CharField(max_length=64, blank=True, default='Profile Incomplete')

    def __str__(self):
        return self.user.email