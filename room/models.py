from django.db import models
from django.contrib.postgres.fields import ArrayField


class Board(models.Model):
    leagueId = models.IntegerField(default=0)
    name = models.CharField(max_length=30, default="anonymous")
    body = models.TextField(max_length=100)
    datetime = models.DateTimeField(auto_now=True)
