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
    status = models.CharField(max_length=30)  # 'for sale' or 'sold' or 'at auction'
    picture = models.FileField(upload_to='base/static', null=True)
    city = models.CharField(max_length=255, null=True)
    location = PlainLocationField(based_fields=['city'], zoom=7, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    final_category = models.CharField(null=True, max_length=200)
    categories = (('category_id_1', 'لوازم دیجیتال'),
                  ('category_id_2', 'لوازم تزیینی'),
                  ('category_id_3', 'لوازم بهداشتی'),
                  ('category_id_4', 'خودرو'),
                  ('category_id_5', 'لوازم ورزشی'),
                  ('category_id_6', 'لوازم آشپزی'),
                  ('category_id_7', 'لوزام خانه'),
                  )

    digital_subcategories = (('لپ تاپ', 'لپ تاپ'),
                             ('تلفن همراه', 'تلفن همراه'),
                             ('دوربین', 'دوربین'),
                             ('تلویزیون', 'تلویزیون'),
                             ('بلندگو', 'بلندگو'),
                             ('تبلت', 'تبلت'),
                             ('هارد، فلش و SSD', 'هارد، فلش و SSD'),
                             ('مچ‌بند و ساعت هوشمند', 'مچ‌بند و ساعت هوشمند'),
                             ('هدفون، هدست', 'هدفون، هدست'),
                             )

    pretty_subcategories = (('تابلو', 'تابلو'),
                            ('مجسمه', 'مجسمه'),
                            ('شمع‌دونی', 'شمع‌دونی'),
                            ('آینه', 'آینه'),
                            ('پرده', 'پرده'),
                            )

    health_subcategories = (('لوازم آرایشی', 'لوازم آرایشی'),
                            ('کرم', 'کرم'),
                            ('شامپو', 'شامپو'),
                            ('ضد تعریق', 'ضد تعریق'),
                            ('دهان‌شوی', 'دهان‌شوی'),
                            )

    cars_subcategories = (('فرمان', 'فرمان'),
                          ('دنده', 'دنده'),
                          ('روکش صندلی', 'روکش صندلی'),
                          ('برف‌‌پاک‌کن', 'برف‌‌پاک‌کن'),
                          ('باتری ماشین', 'باتری ماشین'),
                          )

    sports_subcategories = (('توپ', 'توپ'),
                            ('گرم‌کن', 'گرم‌کن'),
                            ('دست‌کش دروازه‌بانی', 'دست‌کش دروازه‌بانی'),
                            ('لباس شنا', 'لباس شنا'),
                            ('عینک شنا', 'عینک شنا'),
                            )

    cooking_subcategories = (('قابلمه', 'قابلمه'),
                             ('ماهی‌تابه', 'ماهی‌تابه'),
                             ('کف‌گیر', 'کف‌گیر'),
                             ('قاشق‌چنگال', 'قاشق‌چنگال'),
                             ('بشفاب', 'بشفاب'),
                             )

    house_subcategories = (('یخچال', 'یخچال'),
                           ('مبل', 'مبل'),
                           ('پرده', 'پرده'),
                           ('میز', 'میز'),
                           ('صندلی', 'صندلی'),
                           )
    category = models.CharField(max_length=140, null=True, choices=categories)
    digital_subcategory = models.CharField(max_length=140, null=True, blank=True, choices=digital_subcategories)
    pretty_subcategory = models.CharField(max_length=140, null=True, blank=True, choices=pretty_subcategories)
    health_subcategory = models.CharField(max_length=140, null=True, blank=True, choices=health_subcategories)
    cars_subcategory = models.CharField(max_length=140, null=True, blank=True, choices=cars_subcategories)
    sports_subcategory = models.CharField(max_length=140, null=True, blank=True, choices=sports_subcategories)
    cooking_subcategory = models.CharField(max_length=140, null=True, blank=True, choices=cooking_subcategories)
    house_subcategory = models.CharField(max_length=140, null=True, blank=True, choices=house_subcategories)

    # digital_subcategory = models.CharField(max_length=140, null=True, choices=digital_subcategories)

    # subcategory_2 = models.CharField(max_length=140, null=True)

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
        return self.auction.__str__() + ' : ' + self.bidder.__str__() + ', ' + str(self.price)


class Message(models.Model):
    text = models.TextField(null=True)
    sender = models.ForeignKey(ShoppingUser, on_delete=models.CASCADE, related_name='sent_messages', null=True)
    receiver = models.ForeignKey(ShoppingUser, on_delete=models.CASCADE, related_name='received_messages', null=True)