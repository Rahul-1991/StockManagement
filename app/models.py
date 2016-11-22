"""
Definition of models.
"""

from django.db import models

# Create your models here.
class Users(models.Model):
    username = models.CharField(max_length=50)
    hash = models.CharField(max_length=50)
    cash = models.FloatField()
    id = models.AutoField(primary_key=True)

class Portfolio(models.Model):
    id = models.IntegerField()
    symbol = models.CharField(max_length=50)
    quantity = models.IntegerField()
    price = models.FloatField()
    portfolio_id = models.AutoField(primary_key=True)
    timestamp = models.TimeField()
    stock_name = models.CharField(max_length=50)
