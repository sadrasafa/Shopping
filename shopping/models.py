from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.


class User(AbstractUser):
    pass


class ShoppingUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shopping_user')
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, validators=[
        RegexValidator(regex=r'^((\+|00)\d{11,12})|(09\d{9})$',
                       message="شماره تلفن نامعتبر است")], null=True)  # null=True and Blank=True if not required
    province = models.CharField(max_length=40)  # province should be a choice
    city = models.CharField(max_length=40)


class Product(models.Model):
    statuses = [('on-sale', 'on-sale'),
                ('sold', 'sold')]
    name = models.CharField(max_length=140)
    seller = models.ForeignKey(ShoppingUser, on_delete=models.SET_NULL, related_name='buyer', null=True)
    buyer = models.ForeignKey(ShoppingUser, on_delete=models.SET_NULL, related_name='seller', null=True)
    status = models.CharField(max_length=30, choices=statuses, )
