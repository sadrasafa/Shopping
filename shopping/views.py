import hashlib
import random
import string
import requests

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
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
error_wrong_confirmation_code = "کد فعالسازی اشتباه است"
error_wrong_reset_password = "این لینک معتبر نیست"
error_payment_unsuccessful = 'پرداخت ناموفق'
error_auction_not_found = 'چنین مزایده ای وجود ندارد'
error_insufficient_credit = 'اعتبار شما برای شرکت در مزایده کافی نیست'
error_self_bid = 'نمی توانید در مزایده خود شرکت کنید'
error_self_buy = 'نمی توانید کالای خود را بخرید'
error_finish_other_auction = 'نمی توانید مزایده افراد دیگر را متوقف کنید'
shopping_index = 'shopping_index'

hash_salt = 'NeginAarashSadra'


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
            django_user.is_active = False
            django_user.save()
            shopping_user = ShoppingUser(first_name=form.cleaned_data['first_name'],
                                         last_name=form.cleaned_data['last_name'],
                                         email=form.cleaned_data['email'], credit=0)

            shopping_user.user = django_user
            shopping_user.random_code = ''.join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            shopping_user.save()
            eid = hashlib.sha1((hash_salt + shopping_user.email).encode()).hexdigest()
            link = 'http://127.0.0.1:8000/shopping/confirm/' + eid + '/' + shopping_user.random_code
            email = EmailMessage('Confirmation Email', 'Please confirm your email via this link: ' + link,
                                 to=[form.cleaned_data['email'], ])
            email.send()

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
            users = User.objects.filter(username=username)
            if len(users) > 0:
                if not users[0].is_active:
                    message = 'لطفا ایمیل خود را تایید کنید'

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
    # all_products = Product.objects.all()
    return render(request, 'shopping/dashboard.html',
                  {'shopping_user': request.user.shopping_user,
                   'for_sale': for_sale,
                   'bought': bought,})


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
        return render(request, 'shopping/add_location.html',
                      {'locations': locations, 'add_location_form': AddLocationForm(label_suffix='')}, )


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
                              location=loc, latitude=lat, longitude=lon, category=form.cleaned_data['category'])
            product.save()
            es = Elasticsearch()
            es.create(index=shopping_index, doc_type='product', id=product.id,
                      body={'product': {'name': product.name, 'price': product.price, 'category': product.category,
                                        'description': product.description, 'location': {'lat': lat,
                                                                                         'lon': lon}}})

            return HttpResponseRedirect('dashboard')
        else:

            return render(request, 'shopping/add_product.html', {'locations': locations, 'add_product_form': form})
    else:
        return render(request, 'shopping/add_product.html',
                      {'locations': locations, 'add_product_form': AddProductForm(label_suffix='')}, )


def view_product(request, id):
    try:
        product = Product.objects.get(id=id)
    except ObjectDoesNotExist:
        return render(request, 'shopping/error.html', {'error_message': error_product_not_found,
                                                       'type_product_not_found': True})

    template = ''
    if not request.user.is_authenticated:
        template = 'base/not_user_base.html'
    else:
        template = 'base/user_base.html'


    return render(request, 'shopping/view_product.html',
                  {'product': product,
                   'template': template})


def buy_product(request, id):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    try:
        product = Product.objects.get(id=id)
    except ObjectDoesNotExist:
        return render(request, 'shopping/error.html', {'error_message': error_product_not_found,
                                                       'type_product_not_found': True})
    if product.seller == request.user.shopping_user:
        return render(request, 'shopping/error.html', {'error_message': error_self_buy,
                                                       'type_self_buy': True})
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
                    code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
                    r = requests.post('https://tanakora.pythonanywhere.com/pay', data=code)
                    if r.content.decode('utf-8') == code:
                        request.user.shopping_user.credit = 0
                        request.user.shopping_user.save()
                    else:
                        return render(request, 'shopping/error.html', {'error_message': error_payment_unsuccessful,
                                                                       'type_payment_unsuccessful': True})
                else:
                    amount = 0
                    request.user.shopping_user.credit = credit - price
                    request.user.shopping_user.save()
            else:
                amount = price
                code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
                r = requests.post('https://tanakora.pythonanywhere.com/pay', data=code)
                if r.content.decode('utf-8') != code:
                    return render(request, 'shopping/error.html', {'error_message': error_payment_unsuccessful,
                                                                   'type_payment_unsuccessful': True})

            product.buyer = request.user.shopping_user
            product.status = 'sold'
            product.save()
            return HttpResponseRedirect('/shopping/dashboard')
        else:
            return render(request, 'shopping/buy_product.html',
                          {'product': product, 'use_credit_form': form})
    else:
        return render(request, 'shopping/buy_product.html',
                      {'product': product, 'use_credit_form': UseCreditForm(label_suffix='')})


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
                                                'filter': [{'geo_distance': {'distance': form.cleaned_data['distance'],
                                                                             'product.location': {
                                                                                 'lat': lat,
                                                                                 'lon': lon
                                                                             }}},
                                                           {'match': {
                                                               'product.category': form.cleaned_data['category']}}]}
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
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            r = requests.post('https://tanakora.pythonanywhere.com/pay', data=code)
            if r.content.decode('utf-8') == code:
                shopping_user.credit += form.cleaned_data['amount']
                shopping_user.save()
                return HttpResponseRedirect('dashboard')
            else:
                return render(request, 'shopping/error.html', {'error_message': error_payment_unsuccessful,
                                                               'type_payment_unsuccessful': True})
        else:

            return render(request, 'shopping/increase_credit.html', {'increase_credit_form': form})
    else:
        return render(request, 'shopping/increase_credit.html',
                      {'increase_credit_form': IncreaseCreditForm(label_suffix='')}, )


def edit_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    # locations = MyLocation.objects.filter(user=request.user.shopping_user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user.shopping_user)
        if form.is_valid():
            django_user = request.user
            shopping_user = django_user.shopping_user

            shopping_user.update(first_name=form.cleaned_data['first_name'],
                                 last_name=form.cleaned_data['last_name'],
                                 phone_number=form.cleaned_data[
                                     'phone_number'],
                                 city=form.cleaned_data['city'])
            django_user.save()
            shopping_user.save()

            return HttpResponseRedirect('dashboard')
        else:
            return render(request, 'shopping/edit_profile.html', {'edit_profile_form': form})

    else:
        return render(request, 'shopping/edit_profile.html',
                      {'edit_profile_form': EditProfileForm(instance=request.user.shopping_user)}, )


def change_password(request):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    # locations = MyLocation.objects.filter(user=request.user.shopping_user)
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            django_user = request.user
            shopping_user = django_user.shopping_user

            username = shopping_user.user
            password = request.POST['old_password']
            new_password = request.POST['new_password1']
            user = authenticate(username=username, password=password)

            if user is None:
                message = 'رمز عبور وارد شده اشتباه است.'
                return render(request, 'shopping/change_password.html', {'message': message}, status=403)
            else:
                django_user.set_password(new_password)
                django_user.save()
                user = authenticate(username=username, password=new_password)
                login(request, user)
                return HttpResponseRedirect('/shopping/dashboard')

        else:
            return render(request, 'shopping/change_password.html', {'change_password_form': form})

    else:
        return render(request, 'shopping/change_password.html',
                      {'change_password_form': ChangePasswordForm(label_suffix='')})


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


def add_comment(request, id):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    try:
        product = Product.objects.get(id=id)
    except ObjectDoesNotExist:
        return render(request, 'shopping/error.html', {'error_message': error_product_not_found,
                                                       'type_product_not_found': True})
    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():
            comment = Comment(product=product, user=request.user.shopping_user,
                              text=form.cleaned_data['text'], stars=form.cleaned_data['stars'])
            comment.save()
            return HttpResponseRedirect('/shopping/view_product/' + str(id))
        else:
            return render(request, 'shopping/add_comment.html', {'add_comment_form': form})
    else:
        return render(request, 'shopping/add_comment.html',
                      {'add_comment_form': AddCommentForm(label_suffix='')}, )


def confirm(request, eid, code):
    try:
        shopping_user = ShoppingUser.objects.filter(random_code=code)[0]
    except IndexError:
        return render(request, 'shopping/error.html', {'error_message': error_wrong_confirmation_code,
                                                       'type_wrong_confirmation': True})

    hashed = hashlib.sha1((hash_salt + shopping_user.email).encode()).hexdigest()
    if hashed == eid:
        shopping_user.user.is_active = True
        if len(shopping_user.referrer_code) == 10:
            referrer = ShoppingUser.objects.filter(referral_code=shopping_user.referrer_code)[0]
            referrer.credit += 12345
            referrer.save()
        shopping_user.user.save()
        return HttpResponseRedirect('/shopping/signin')
    else:
        return render(request, 'shopping/error.html', {'error_message': error_wrong_confirmation_code,
                                                       'type_wrong_confirmation': True})


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                shopping_user = User.objects.filter(username=username)[0].shopping_user
            except IndexError:
                return render(request, 'shopping/forgot_password.html', {'forgot_password_form': form,
                                                                         'Done': True})

            shopping_user.random_code = ''.join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            shopping_user.save()
            eid = hashlib.sha1((hash_salt + hash_salt + shopping_user.email).encode()).hexdigest()
            link = 'http://127.0.0.1:8000/shopping/reset_password/' + eid + '/' + shopping_user.random_code
            email = EmailMessage('Password Reset', 'To Change Your Password Go To The Following Link: ' + link,
                                 to=[shopping_user.email, ])
            email.send()
            return render(request, 'shopping/forgot_password.html', {'forgot_password_form': form,
                                                                     'Done': True})
        else:

            return render(request, 'shopping/forgot_password.html', {'forgot_password_form': form})
    else:
        return render(request, 'shopping/forgot_password.html',
                      {'forgot_password_form': ForgotPasswordForm(label_suffix='')}, )


def reset_password(request, eid, code):
    try:
        shopping_user = ShoppingUser.objects.filter(random_code=code)[0]
    except IndexError:
        return render(request, 'shopping/error.html', {'error_message': error_wrong_reset_password,
                                                       'type_wrong_reset_password': True})

    hashed = hashlib.sha1((hash_salt + hash_salt + shopping_user.email).encode()).hexdigest()
    if hashed == eid:
        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                shopping_user.user.set_password(form.cleaned_data['password1'])
                shopping_user.user.save()
                return HttpResponseRedirect('/shopping/signin')
            else:
                return render(request, 'shopping/reset_password.html', {'reset_password_form': form})
        else:
            return render(request, 'shopping/reset_password.html',
                          {'reset_password_form': ResetPasswordForm(label_suffix='')}, )
    else:
        return render(request, 'shopping/error.html', {'error_message': error_wrong_reset_password,
                                                       'type_wrong_reset_password': True})


def referral(request):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    shopping_user = request.user.shopping_user
    if len(shopping_user.referral_code) != 10:
        shopping_user.referral_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        shopping_user.save()
    return render(request, 'shopping/referral.html',{'code': shopping_user.referral_code})


def signup_with_referral(request, code):
    if request.method == 'POST':
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            django_user = User.objects.create_user(username=form.cleaned_data['username'],
                                                   password=form.cleaned_data['password1'], )
            django_user.is_active = False
            django_user.save()
            shopping_user = ShoppingUser(first_name=form.cleaned_data['first_name'],
                                         last_name=form.cleaned_data['last_name'],
                                         email=form.cleaned_data['email'], credit=0)

            shopping_user.user = django_user
            shopping_user.random_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            shopping_user.referrer_code = code
            shopping_user.save()
            eid = hashlib.sha1((hash_salt+shopping_user.email).encode()).hexdigest()
            link = 'http://127.0.0.1:8000/shopping/confirm/' + eid + '/' + shopping_user.random_code
            email = EmailMessage('Confirmation Email', 'Please confirm your email via this link: ' + link,
                                 to=[form.cleaned_data['email'], ])
            email.send()

            return HttpResponseRedirect('/shopping/signin')
        else:

            return render(request, 'shopping/signup.html', {'signup_form': form})
    else:
        return render(request, 'shopping/signup.html', {'signup_form': UserSignupForm(label_suffix='')})


def create_auction(request):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    locations = MyLocation.objects.filter(user=request.user.shopping_user)
    if request.method == 'POST':
        form = CreateAuctionForm(request.POST, request.FILES)
        if form.is_valid():
            django_user = request.user
            shopping_user = django_user.shopping_user
            loc = request.POST.get('addresses')
            # loc = form.cleaned_data['location']
            lat = float(loc.split(',')[0])
            lon = float(loc.split(',')[1])
            product = Product(name=form.cleaned_data['name'], price=form.cleaned_data['price'],
                              description=form.cleaned_data['description'], seller=shopping_user,
                              status='at auction', picture=form.cleaned_data['picture'],
                              location=loc, latitude=lat, longitude=lon, category=form.cleaned_data['category'])
            product.save()
            auction = Auction(product=product, auctioneer=shopping_user, base_price=product.price,
                              end_date=form.cleaned_data['end_date'], finished=False)
            auction.save()
            # es = Elasticsearch()
            # es.create(index=shopping_index, doc_type='product', id=product.id,
            #           body={'product': {'name': product.name, 'price': product.price, 'category': product.category,
            #                             'description': product.description, 'location': {'lat': lat,
            #                                                                              'lon': lon}}})

            return HttpResponseRedirect('dashboard')
        else:

            return render(request, 'shopping/create_auction.html', {'locations': locations, 'create_auction_form': form})
    else:
        return render(request, 'shopping/create_auction.html',
                      {'locations': locations, 'create_auction_form': CreateAuctionForm(label_suffix='')}, )


def view_auction(request, id):
    try:
        auction = Auction.objects.get(id=id)
        product = auction.product
    except ObjectDoesNotExist:
        return render(request, 'shopping/error.html', {'error_message': error_auction_not_found,
                                                       'type_auction_not_found': True})

    template = ''
    if not request.user.is_authenticated:
        template = 'base/not_user_base.html'
    else:
        template = 'base/user_base.html'
    return render(request, 'shopping/view_auction.html',
                  {'auction': auction,
                   'product': product,
                   'template': template})


def bid_auction(request, id):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    try:
        auction = Auction.objects.get(id=id)
    except ObjectDoesNotExist:
        return render(request, 'shopping/error.html', {'error_message': error_auction_not_found,
                                                       'type_auction_not_found': True})

    if auction.auctioneer == request.user.shopping_user:
        return render(request, 'shopping/error.html', {'error_message': error_self_bid,
                                                       'type_self_bid': True})

    if auction.finished:
        return render(request, 'shopping/error.html', {'error_message': error_already_sold,
                                                       'type_already_sold': True})

    if request.method == 'POST':
        form = BidAuctionForm(request.POST)
        if form.is_valid():
            shopping_user = request.user.shopping_user
            # 10% amanat:
            participated = False
            for bid in auction.bid_set.all():
                if bid.bidder == shopping_user:
                    participated = True
                    break
            if not participated:
                if shopping_user.credit < auction.base_price/10:
                    return render(request, 'shopping/error.html', {'error_message': error_insufficient_credit,
                                                                   'type_insufficient_credit': True})
                shopping_user.credit -= auction.base_price/10
                shopping_user.save()

            bid = Bid(auction=auction, bidder=shopping_user, price=form.cleaned_data['price'])
            bid.save()
            return HttpResponseRedirect('/shopping/dashboard')
        else:
            return render(request, 'shopping/bid_auction.html',
                          {'bid_auction_form': form})
    else:
        return render(request, 'shopping/bid_auction.html',
                      {'bid_auction_form': BidAuctionForm(label_suffix='')})


def finish_auction(request, id):
    if not request.user.is_authenticated:
        return render(request, 'shopping/error.html', {'error_message': error_not_authenticated,
                                                       'type_not_authenticated': True})
    try:
        auction = Auction.objects.get(id=id)
    except ObjectDoesNotExist:
        return render(request, 'shopping/error.html', {'error_message': error_auction_not_found,
                                                       'type_auction_not_found': True})

    if auction.auctioneer != request.user.shopping_user:
        return render(request, 'shopping/error.html', {'error_message': error_finish_other_auction,
                                                       'type_finish_other_auction': True})

    if auction.product.status == 'auction finished':
        return render(request, 'shopping/error.html', {'error_message': error_already_sold,
                                                       'type_already_sold': True})
    auction.finished = True
    auction.save()

    highest_bid = None
    bidders = set()
    for bid in auction.bid_set.all():
        bidders.add(bid.bidder)
        if highest_bid is None or bid.price > highest_bid.price:
            highest_bid = bid

    for bidder in bidders:
            bidder.credit += auction.base_price/10
            bidder.save()
    if highest_bid is not None:
        highest_bid.bidder.credit -= highest_bid.price
        highest_bid.bidder.save()

        auction.product.buyer = highest_bid.bidder
        auction.product.save()
        auction.save()
        email = EmailMessage('Auction Winner!', 'Congratulations ' +
                             highest_bid.bidder.first_name + '!!! You Have The Won The Auction of '+auction.product +
                             ' for ' + str(highest_bid.price),
                             to=[highest_bid.bidder.email, ])
        email.send()

    return render(request, 'shopping/auction_finished.html',
                  {'auction': auction})
