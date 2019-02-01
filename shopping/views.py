from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from elasticsearch import Elasticsearch

from .forms import *
from .models import *

# Create your views here.

error_not_authenticated = "ابتدا وارد شوید."
error_404_message = "چنین صفحه ای وجود ندارد"
error_already_sold = "محصول قبلا فروخته شده است"
error_product_not_found = "چنین محصولی وجود ندارد"
error_user_not_found = "چنین کاربری وجود ندارد"
shopping_index = 'shopping_index'


def home(request):
    for_sale = Product.objects.filter(status='for sale')

    template = ''
    if not request.user.is_authenticated:
        template = 'base/not_user_base.html'
    else:
        template = 'base/user_base.html'

    return render(request, 'shopping/home.html',
                  {'for_sale': for_sale,
                   'template': template})


def error404(request):
    return render(request, 'shopping/error.html', {'type_404': True, 'error_message': error_404_message})


def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            django_user = User.objects.create_user(username=form.cleaned_data['username'],
                                                   password=form.cleaned_data['password1'], )
            django_user.save()
            shopping_user = ShoppingUser(first_name=form.cleaned_data['first_name'],
                                         last_name=form.cleaned_data['last_name'],
                                         email=form.cleaned_data['email'], credit=0)

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


def add_location(request):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    locations = MyLocation.objects.filter(user=request.user.shopping_user)
    if request.method == 'POST':
        form = AddLocationForm(request.POST)
        if form.is_valid():
            django_user = request.user
            shopping_user = django_user.shopping_user
            loc = form.cleaned_data['location']
            lat = float(loc.split(',')[0])
            lon = float(loc.split(',')[1])
            mylocation = MyLocation(name=form.cleaned_data['name'],
                                    city=form.cleaned_data['city'],
                                    location=loc, latitude=lat, longitude=lon)
            mylocation.user = shopping_user
            mylocation.save()
            return HttpResponseRedirect('dashboard')
        else:

            return render(request, 'shopping/add_location.html', {'locations': locations, 'add_location_form': form})
    else:
        return render(request, 'shopping/add_location.html', {'locations': locations, 'add_location_form': AddLocationForm(label_suffix='')}, )


def add_product(request):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    locations = MyLocation.objects.filter(user=request.user.shopping_user)
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            django_user = request.user
            shopping_user = django_user.shopping_user
            loc = request.POST.get('addresses')
            # loc = form.cleaned_data['location']
            lat = float(loc.split(',')[0])
            lon = float(loc.split(',')[1])
            product = Product(name=form.cleaned_data['name'], price=form.cleaned_data['price'],
                              description=form.cleaned_data['description'], seller=shopping_user,
                              status='for sale', picture=form.cleaned_data['picture'],
                              location=loc, latitude=lat, longitude=lon,)
            product.save()
            es = Elasticsearch()
            es.create(index=shopping_index, doc_type='product', id=product.id,
                      body={'product': {'name': product.name, 'price': product.price,
                                        'description': product.description, 'location': {'lat': lat,
                                                                                         'lon': lon}}})

            return HttpResponseRedirect('dashboard')
        else:

            return render(request, 'shopping/add_product.html', {'locations' : locations, 'add_product_form': form})
    else:
        return render(request, 'shopping/add_product.html', {'locations' : locations, 'add_product_form': AddProductForm(label_suffix='')}, )


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

    if request.method == 'POST':
        form = UseCreditForm(request.POST)
        if form.is_valid():
            price = product.price
            credit = request.user.shopping_user.credit
            if form.cleaned_data['use_credit']:
                if credit < price:
                    amount = price - credit
                    request.user.shopping_user.credit = 0
                    request.user.shopping_user.save()
                else:
                    amount = 0
                    request.user.shopping_user.credit = credit - price
            else:
                amount = price
            product.buyer = request.user.shopping_user
            product.status = 'sold'
            product.save()
            return render(request, 'shopping/pay.html', {'amount': amount})
        else:
            return render(request, 'shopping/buy_product.html',
                      {'product': product, 'use_credit_form' : UseCreditForm})
    else:
        return render(request, 'shopping/buy_product.html', {'product': product, 'use_credit_form':UseCreditForm(label_suffix='')})


def search_product(request):
    if request.method == 'POST':
        form = SearchProductForm(request.POST, request.FILES)
        if form.is_valid():
            loc = form.cleaned_data['location']
            lat = float(loc.split(',')[0])
            lon = float(loc.split(',')[1])
            w_name = 2
            w_desc = 1
            w_price = 1
            es = Elasticsearch()
            results = es.search(index='shopping_index', doc_type='product',
                                body={'query':
                                          {'bool':
                                               {'should':
                                                    [{'match':
                                                          {'product.name': {'query': form.cleaned_data['name'],
                                                                            'boost': w_name}}},
                                                     {'match':
                                                         {'product.description': {
                                                             'query': form.cleaned_data['description'],
                                                             'boost': w_desc}}},
                                                     {'range':
                                                          {'product.price': {'lte': form.cleaned_data['price'],
                                                                             'boost': w_price}}},
                                                     ],
                                                'filter': {'geo_distance': {'distance': form.cleaned_data['distance'],
                                                                            'product.location': {
                                                                                'lat': lat,
                                                                                'lon': lon
                                                                            }}}}
                                           }})
            res = []
            for r in results['hits']['hits']:
                to_add = r['_source']['product']
                to_add['id'] = r['_id']
                to_add['picture'] = Product.objects.get(id=to_add['id']).picture
                res.append(to_add)
            return render(request, 'shopping/search_results.html', {'results': res})
        else:

            return render(request, 'shopping/search_product.html', {'search_product_form': form})
    else:
        return render(request, 'shopping/search_product.html',
                      {'search_product_form': SearchProductForm(label_suffix='')}, )


def increase_credit(request):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    if request.method == 'POST':
        form = IncreaseCreditForm(request.POST)
        if form.is_valid():
            django_user = request.user
            shopping_user = django_user.shopping_user
            shopping_user.credit += form.cleaned_data['amount']
            shopping_user.save()
            return HttpResponseRedirect('dashboard')
        else:

            return render(request, 'shopping/increase_credit.html', {'increase_credit_form': form})
    else:
        return render(request, 'shopping/increase_credit.html', {'increase_credit_form': IncreaseCreditForm(label_suffix='')}, )


def view_user(request, id):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    try:
        viewed_user = ShoppingUser.objects.get(id=id)
    except ObjectDoesNotExist:
        return render(request, 'shopping/error.html', {'error_message': error_user_not_found,
                                                       'type_user_not_found': True})
    return render(request, 'shopping/view_user.html', {'viewed_user': viewed_user})
