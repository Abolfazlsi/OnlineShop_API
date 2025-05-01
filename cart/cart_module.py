from product.models import Product

CART_SESSION_ID = "cart"


# cart
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}

        self.cart = cart

    def __iter__(self):
        cart = self.cart.copy()
        for item in cart.values():
            product = Product.objects.get(id=int(item["id"]))
            item["product"] = product
            item["total"] = int(item["quantity"]) * int(item["price"])
            item["unique_id"] = self.unique_id_generator(product.id, item["color"], item["size"])
            yield item

    # generate id for product
    def unique_id_generator(self, id, color, size):
        result = f"{id}-{color}-{size}"
        return result

    # add product to cart
    def add(self, product, quantity, color, size):
        unique = self.unique_id_generator(product.id, color, size)
        if unique not in self.cart:
            self.cart[unique] = {"quantity": 0, "price": str(product.price), "color": color, "size": size,
                                 "id": str(product.id)}
        self.cart[unique]["quantity"] += int(quantity)
        self.save()

    # remove all products from cart
    def remove_cart(self):
        del self.session["cart"]

    # total price of products in cart
    def final_total(self):
        total = sum((int(item["price"]) * int(item["quantity"]) for item in self.cart.values()))
        return total

    # number of products in cart
    def get_product_count(self):
        return len(self.cart)

    def item_exists(self, id):
        return str(id) in self.cart

    def is_empty(self):
        return len(self.cart) == 0

    # delete product from cart

    def delete(self, id):
        if id in self.cart:
            del self.cart[id]
            self.save()

    def save(self):
        self.session.modified = True
