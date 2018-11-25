from django.db import models
from django.contrib.postgres.fields import ArrayField

class League(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    link = models.TextField(blank=True)
    woman = ArrayField(models.CharField(max_length=20))
    occasion = ArrayField(models.CharField(max_length=20))
    profile = ArrayField(models.CharField(max_length=20))
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)

class Board(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
