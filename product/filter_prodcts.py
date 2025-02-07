from product.models import Product


# filter product by (color, size, price, cheapest and the most expensive)
def filter_product(request):
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    # filter product (cheapest adn the most expensive)
    filter = request.GET.get("filter")
    colors = request.GET.getlist("color")
    sizes = request.GET.getlist("size")
    products = Product.objects.all()

    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price).distinct()

    if filter == "cheapest":
        products = products.order_by("price")
    elif filter == "expensive":
        products = products.order_by("-price")

    if colors:
        products = products.filter(color__name__in=colors).distinct()

    if sizes:
        products = products.filter(size__name__in=sizes).distinct()

    return products
