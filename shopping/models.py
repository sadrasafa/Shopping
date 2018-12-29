from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class MyUser(AbstractUser):
    pass


class Product(models.Model):
    name = models.CharField(max_length=140)
