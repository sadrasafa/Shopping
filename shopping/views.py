from django.shortcuts import render
from .forms import UserSignupForm, AddProductForm
from .models import ShoppingUser, User, Product
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout


# Create your views here.

error_not_authenticated = "ابتدا وارد شوید."
error_404_message = "چنین صفحه ای وجود ندارد"
error_already_sold = "محصول قبلا فروخته شده است"


def home(request):
    return render(request, 'shopping/home.html')


def error404(request):
    return render(request, 'shopping/error.html', {'error_404': True, 'error_message': error_404_message})


def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            django_user = User.objects.create_user(username=form.cleaned_data['username'],
                                                   password=form.cleaned_data['password1'], )
            django_user.save()
            shopping_user = ShoppingUser(first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'],
                                         email=form.cleaned_data['email'], phone_number=form.cleaned_data['phone_number'],
                                         province=form.cleaned_data['province'], city=form.cleaned_data['city'])  # Shouldn't we set the value of account_confirmed as well?

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
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated})
    if not hasattr(request.user, 'shopping_user'):
        shopping_user = ShoppingUser(user=request.user)
        shopping_user.save()

    shopping_user = request.user.shopping_user
    for_sale = Product.objects.filter(seller=shopping_user).filter(status='for sale')
    bought = Product.objects.filter(buyer=shopping_user).filter(status='sold')
    all_products = Product.objects.all()
    return render(request, 'shopping/dashboard.html',
                  {'user': request.user.shopping_user,
                   'for_sale': for_sale,
                   'bought': bought,
                   'all_products': all_products})


def add_product(request):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated, })

    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            django_user = request.user
            shopping_user = django_user.shopping_user
            product = Product(name=form.cleaned_data['name'], price=form.cleaned_data['price'],
                              description=form.cleaned_data['description'], seller=shopping_user,
                              status='for sale', picture=form.cleaned_data['picture'])
            product.save()
            return HttpResponseRedirect('dashboard')
        else:

            return render(request, 'shopping/add_product.html', {'add_product_form': form})
    else:
        return render(request, 'shopping/add_product.html', {'add_product_form': AddProductForm(label_suffix='')})


def view_product(request, id):
    product = Product.objects.get(id=id)
    return render(request, 'shopping/view_product.html',
                  {'product': product})


def buy_product(request, id):
    product = Product.objects.get(id=id)
    if product.status == 'sold':
        return render(request, 'shopping/error.html', {'error_message': error_already_sold})
    shopping_user = request.user.shopping_user
    product.buyer = shopping_user
    product.status = 'sold'
    product.save()
    return render(request, 'shopping/view_product.html',
                  {'product': product})
