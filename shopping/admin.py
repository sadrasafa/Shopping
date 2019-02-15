from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.


admin.site.register(User, UserAdmin)
admin.site.register(Product)
admin.site.register(ShoppingUser)
admin.site.register(Comment)
admin.site.register(MyLocation)
admin.site.register(Auction)
admin.site.register(Bid)
