from django.urls import path

from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('add_location', views.add_location, name='add_location'),
    path('add_product', views.add_product, name='add_product'),
    path('view_product/<int:id>', views.view_product, name='view_product'),
    path('buy_product/<int:id>', views.buy_product, name='buy_product'),
    path('search_product', views.search_product, name='search_product'),
    path('increase_credit', views.increase_credit, name='increase_credit')
]