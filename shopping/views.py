from django.shortcuts import render
from .forms import UserSignupForm
from .models import ShoppingUser, User, Product
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout


# Create your views here.

not_authenticated_error = "ابتدا وارد شوید."


def home(request):
    return render(request, 'shopping/home.html')


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
        message = not_authenticated_error
        return render(request, 'shopping/not_authenticated.html', {'error_m': message,
                                                                   })
    if not hasattr(request.user, 'shopping_user'):
        shopping_user = ShoppingUser(user=request.user)
        shopping_user.save()

    shopping_user = request.user.shopping_user
    on_sale = Product.objects.filter(seller=shopping_user).filter(status='on-sale')
    bought = Product.objects.filter(buyer=shopping_user).filter(status='sold')
    all_products = Product.objects.all()
    return render(request, 'shopping/dashboard.html',
                  {'user': request.user.shopping_user,
                   'on_sale': on_sale,
                   'bought': bought,
                   'all_products': all_products})
