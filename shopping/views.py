from django.shortcuts import render
from .forms import UserSignupForm, AddProductForm
from .models import ShoppingUser, User, Product
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.

error_not_authenticated = "ابتدا وارد شوید."
error_404_message = "چنین صفحه ای وجود ندارد"
error_already_sold = "محصول قبلا فروخته شده است"
error_product_not_found = "چنین محصولی وجود ندارد"


def home(request):
    return render(request, 'shopping/home.html')


def error404(request):
    return render(request, 'shopping/error.html', {'type_404': True, 'error_message': error_404_message})


def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            django_user = User.objects.create_user(username=form.cleaned_data['username'],
                                                   password=form.cleaned_data['password1'], )
            django_user.save()
            shopping_user = ShoppingUser(first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'],
                                         email=form.cleaned_data['email'],)

            shopping_user.user = django_user
            shopping_user.save()

            return HttpResponseRedirect('signin')
        else:

            return render(request, 'shopping/signup.html', {'signup_form': form})
    else:
        return render(request, 'shopping/signup.html', {'signup_form': UserSignupForm(label_suffix='')})


def signin(request):
    if request.method == 'GET':
        return render(request, 'shopping/signin.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/shopping/dashboard')
        else:
            message = 'نام کاربری یا رمز عبور اشتباه است'
            return render(request, 'shopping/signin.html', {'message': message}, status=403)


def signout(request):
    logout(request)
    return HttpResponseRedirect('home')


def dashboard(request):  # , action):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    if not hasattr(request.user, 'shopping_user'):
        shopping_user = ShoppingUser(user=request.user)
        shopping_user.save()

    shopping_user = request.user.shopping_user
    for_sale = Product.objects.filter(seller=shopping_user).filter(status='for sale')
    bought = Product.objects.filter(buyer=shopping_user).filter(status='sold')
    all_products = Product.objects.all()
    return render(request, 'shopping/dashboard.html',
                  {'shopping_user': request.user.shopping_user,
                   'for_sale': for_sale,
                   'bought': bought,
                   'all_products': all_products})


def add_product(request):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})

    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            django_user = request.user
            shopping_user = django_user.shopping_user
            loc = form.cleaned_data['location']
            lat = float(loc.split(',')[0])
            lon = float(loc.split(',')[1])
            product = Product(name=form.cleaned_data['name'], price=form.cleaned_data['price'],
                              description=form.cleaned_data['description'], seller=shopping_user,
                              status='for sale', picture=form.cleaned_data['picture'],
                              location=loc, latitude=lat, longitude=lon)
            product.save()
            return HttpResponseRedirect('dashboard')
        else:

            return render(request, 'shopping/add_product.html', {'add_product_form': form})
    else:
        return render(request, 'shopping/add_product.html', {'add_product_form': AddProductForm(label_suffix='')},)


def view_product(request, id):
    try:
        product = Product.objects.get(id=id)
    except ObjectDoesNotExist:
        return render(request, 'shopping/error.html', {'error_message': error_product_not_found,
                                                       'type_product_not_found': True})
    return render(request, 'shopping/view_product.html',
                  {'product': product})


def buy_product(request, id):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    try:
        product = Product.objects.get(id=id)
    except ObjectDoesNotExist:
        return render(request, 'shopping/error.html', {'error_message': error_product_not_found,
                                                       'type_product_not_found': True})

    if product.status == 'sold':
        return render(request, 'shopping/error.html', {'error_message': error_already_sold,
                                                       'type_already_sold': True})
    shopping_user = request.user.shopping_user
    product.buyer = shopping_user
    product.status = 'sold'
    product.save()
    return render(request, 'shopping/view_product.html',
                  {'product': product})


#TODO search products