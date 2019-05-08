from __future__ import unicode_literals

from django.db import models

# Create your models here.
class translate(models.Model):
    ip = models.CharField(max_length = 20)
    word = models.TextField()
    translate = models.TextField()
    updated = models.DateTimeField(auto_now = True)
