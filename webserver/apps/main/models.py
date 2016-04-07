from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


def upload_to_handler(instance, filename):
    return '{0}/{1}'.format(instance.user.email, filename)


# Create your models here.
class Team(models.Model):
    code = models.CharField(max_length=256)
    members = models.TextField(default='{}')

    def __str__(self):
        return self.code


class Account(models.Model):
    user = models.OneToOneField(User)
    team = models.ForeignKey(Team, null=True, blank=True, default=None)
    activation_token = models.CharField(max_length=64, null=True, blank=True, default=None)

    school = models.CharField(max_length=64, blank=True, default='')
    program = models.CharField(max_length=64, blank=True, default='')
    year_of_study = models.CharField(max_length=64, blank=True, default='')

    want_to_do = models.TextField(blank=True, default='')
    already_done = models.TextField(blank=True, default='')

    resume = models.FileField(upload_to=upload_to_handler, blank=True, null=True)
    supporting_files = models.FileField(upload_to=upload_to_handler, blank=True, null=True)
    supporting_text = models.TextField(blank=True, default='')

    # Profile incomplete, Profile complete but not applied, Applied, ...
    application_status = models.CharField(max_length=64, blank=True, default='Profile incomplete')

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' <' + self.user.email + '>'
