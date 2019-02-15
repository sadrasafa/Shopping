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
    random_code = models.CharField(max_length=10, null=True, blank=True)
    referral_code = models.CharField(max_length=10, null=True, blank=True, default='0')
    referrer_code = models.CharField(max_length=10, null=True, blank=True, default='0')

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
    status = models.CharField(max_length=30)  # 'for sale' or 'sold' or 'at auction'
    picture = models.FileField(upload_to='base/static', null=True)
    city = models.CharField(max_length=255, null=True)
    location = PlainLocationField(based_fields=['city'], zoom=7, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    categories = (('لپ تاپ', 'لپ تاپ'),
                  ('گوشی', 'گوشی'),
                  ('دوربین', 'دوربین'),
                  ('میز', 'میز'),
                  ('کیف', 'کیف'),
                  ('لوازم الکترونیکی', 'لوازم الکترونیکی'),
                  ('عینک', 'عینک'),
                  ('لباس', 'لباس'),
                  ('لوازم تزیینی', 'لوازم تزیینی'),
                  ('تابلو', 'تابلو'),
                  ('لوازم بهداشتی', 'لوازم بهداشتی'),
                  ('خودرو', 'خودرو'),
                  ('تلویزیون', 'تلویزیون'),
                  ('لوازم ورزشی', 'لوازم ورزشی'),
                  ('صندلی', 'صندلی'),
                  ('لوازم آشپزی', 'لوازم آشپزی'),
                  ('مسکن', 'مسکن'),
                  ('خوراکی', 'خوراکی'),
                  ('مبل', 'مبل'),
                  ('سایر', 'سایر'),
                  )
    category = models.CharField(max_length=140, null=True, choices=categories)
    # FOR AUCTION:

    def __str__(self):
        return self.name + ': ' + self.seller.__str__()


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(ShoppingUser, on_delete=models.CASCADE, null=True)
    text = models.TextField(null=True)
    stars = models.IntegerField(null=True)


class Auction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    auctioneer = models.ForeignKey(ShoppingUser, on_delete=models.CASCADE, null=True)
    base_price = models.IntegerField(null=True)
    end_date = models.DateTimeField(null=True)
    finished = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.product.__str__()


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, null=True)
    bidder = models.ForeignKey(ShoppingUser, on_delete=models.CASCADE, null=True)
    price = models.IntegerField(null=True)

    def __str__(self):
        return self.auction.__str__() + ' : ' + self.bidder.__str__()+', '+str(self.price)
