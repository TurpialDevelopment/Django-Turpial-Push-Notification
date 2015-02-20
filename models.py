from django.db import models
from chef.models import *

class Phone(models.Model):
  client = models.ManyToManyField(Clients)
  reg_id =  models.CharField(max_length=255, unique=True)
  os = models.CharField(max_length=10)
  version = models.CharField(max_length=20, null=True)
 
# Create your models here.
