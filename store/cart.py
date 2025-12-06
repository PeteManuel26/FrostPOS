class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product_id, qty=1):
        pid = str(product_id)
        self.cart[pid] = self.cart.get(pid, 0) + int(qty)
        self.save()

    def remove(self, product_id):
        pid = str(product_id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def save(self):
        self.session.modified = True

    def items(self):
        from .models import Product
        products = Product.objects.filter(id__in=[int(k) for k in self.cart.keys()])
        for p in products:
            yield {
                'product': p,
                'qty': self.cart[str(p.id)],
                'line_total': p.price * self.cart[str(p.id)]
            }

    def clear(self):
        self.session['cart'] = {}
        self.save()
