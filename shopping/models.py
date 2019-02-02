from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from location_field.models.plain import PlainLocationField
from django.utils.translation import ugettext_lazy as _
# from osm_field.fields import LatitudeField, LongitudeField, OSMField

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
                       message="شماره تلفن نامعتبر است")], null=True, blank=True)  # null=True and Blank=True if not required
    province = models.CharField(max_length=40, null=True, blank=True)  # province should be a choice
    city = models.CharField(max_length=40, null=True, blank=True)
    credit = models.IntegerField(null=True, default=0)

    def __str__(self):
        return self.user.username + ' ' + self.first_name + ' ' + self.last_name


class MyLocation(models.Model):
    name = models.CharField(max_length=140)
    user = models.ForeignKey(ShoppingUser, on_delete=models.SET_NULL, null=True)
    city = models.CharField(max_length=255, null=True)
    location = PlainLocationField(based_fields=['city'], zoom=7, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def __str__(self):
        return self.user.__str__() + ": " + self.name


class Product(models.Model):
    name = models.CharField(max_length=140)
    price = models.IntegerField(null=True)
    description = models.CharField(max_length=500, null=True)
    seller = models.ForeignKey(ShoppingUser, on_delete=models.SET_NULL, related_name='seller', null=True)
    buyer = models.ForeignKey(ShoppingUser, on_delete=models.SET_NULL, related_name='buyer', null=True)
    status = models.CharField(max_length=30)  # 'for sale' or 'sold'
    picture = models.FileField(upload_to='base/static', null=True)
    city = models.CharField(max_length=255, null=True)
    location = PlainLocationField(based_fields=['city'], zoom=7, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    categories = (('لپ تاپ', 'لپ تاپ'),
                  ('گوشی', 'گوشی'),
                  ('دوربین', 'دوربین'),
                  ('میز', 'میز'),)
    category = models.CharField(max_length=140, null=True, choices=categories)

    def __str__(self):
        return self.name + ': ' + self.seller.__str__()


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(ShoppingUser, on_delete=models.CASCADE, null=True)
    text = models.TextField(null=True)
    stars = models.IntegerField(null=True)



