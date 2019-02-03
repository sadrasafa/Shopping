from shopping.models import Product


def product_processor(request):
    all_products = Product.objects.all()
    return {'all_products': all_products}
