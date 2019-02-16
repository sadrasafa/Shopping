from shopping.models import Product, Auction


def product_processor(request):
    q1 = Product.objects.filter(status='for sale')
    q2 = Product.objects.filter(status='sold')
    # all_products = Product.objects.all()
    all_products = q1.union(q2)
    return {'all_products': all_products}


def auction_processor(request):
    all_auctions = Auction.objects.all()
    return {'all_auctions': all_auctions}


def new_message_processor(request):
    has_new_message = False
    try:
        has_new_message = request.user.shopping_user.has_new_messages
    except AttributeError:
        pass
    return {'has_new_message': has_new_message}