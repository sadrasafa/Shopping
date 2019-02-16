from django.urls import path, re_path

from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    re_path('signup_with_referral/(?P<code>[a-zA-Z0-9]*)', views.signup_with_referral, name='signup_with_referral'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('add_location', views.add_location, name='add_location'),
    path('add_product', views.add_product, name='add_product'),
    path('view_product/<int:id>', views.view_product, name='view_product'),
    path('buy_product/<int:id>', views.buy_product, name='buy_product'),
    path('search_product', views.search_product, name='search_product'),
    path('increase_credit', views.increase_credit, name='increase_credit'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('change_password', views.change_password, name='change_password'),
    path('view_user/<int:id>', views.view_user, name='view_user'),
    path('add_comment/<int:id>', views.add_comment, name='add_comment'),
    re_path('confirm/(?P<eid>[a-fA-F0-9]*)/(?P<code>[a-zA-Z0-9]*)', views.confirm, name='confirm'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    re_path('reset_password/(?P<eid>[a-fA-F0-9]*)/(?P<code>[a-zA-Z0-9]*)', views.reset_password, name='reset_password'),
    path('referral', views.referral, name='referral'),
    path('create_auction', views.create_auction, name='create_auction'),
    path('view_auction/<int:id>', views.view_auction, name='view_auction'),
    path('bid_auction/<int:id>', views.bid_auction, name='bid_auction'),
    path('finish_auction/<int:id>', views.finish_auction, name='finish_auction'),
    path('send_message/<int:id>', views.send_message, name='send_message'),
    path('messages', views.messages, name='messages')



]