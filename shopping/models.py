from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from location_field.models.plain import PlainLocationField


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
                       message="شماره تلفن نامعتبر است")], null=True,
                                    blank=True)  # null=True and Blank=True if not required
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
    status = models.CharField(max_length=30)  # 'for sale' or 'sold'
    picture = models.FileField(upload_to='base/static', null=True)
    city = models.CharField(max_length=255, null=True)
    location = PlainLocationField(based_fields=['city'], zoom=7, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    categories = (('لوازم دیجیتال', 'لوازم دیجیتال'),
                  ('لوازم تزیینی', 'لوازم تزیینی'),
                  ('لوازم بهداشتی', 'لوازم بهداشتی'),
                  ('خودرو', 'خودرو'),
                  ('لوازم ورزشی', 'لوازم ورزشی'),
                  ('لوازم آشپزی', 'لوازم آشپزی'),
                  ('مسکن', 'مسکن'),
                  ('لوازم برقی', 'لوازم برقی'),
                  )

    digital_subcategories = (('لپ تاپ', 'لپ تاپ'),
                             ('تلفن همراه', 'تلفن همراه'),
                             ('دوربین', 'دوربین'),
                             ('تلویزیون', 'تلویزیون'),
                             ('بلندگو', 'بلندگو'),
                             ('تلویزیون', 'تلویزیون'),
                             ('تبلت', 'تبلت'),
                             ('هارد، فلش و SSD', 'تلویزیون'),
                             ('مچ‌بند و ساعت هوشمند', 'تلویزیون'),
                             ('هدفون، هدست', 'تلویزیون'),
                             )

    health_subcategories = (('لوازم آرایشی', 'لوازم آرایشی'),
                            ('لوازم بهداشتی', 'لوازم بهداشتی'),
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

    # sub_category_1 = models.CharField(max_length=140, null=True, choices=sub_categories_1)

    def __str__(self):
        return self.name + ': ' + self.seller.__str__()


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(ShoppingUser, on_delete=models.CASCADE, null=True)
    text = models.TextField(null=True)
    stars = models.IntegerField(null=True)
