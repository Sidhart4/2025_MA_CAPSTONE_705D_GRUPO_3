from decimal import Decimal

CART_KEY = 'cart'

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_KEY)
        if cart is None:
            cart = self.session[CART_KEY] = {}  # {producto_id: {"qty": n, "price": "9990"}}
        self.cart = cart

    def add(self, producto, qty=1, override=False):
        pid = str(producto.id)
        if pid not in self.cart:
            self.cart[pid] = {"qty": 0, "price": str(producto.precio)}
        self.cart[pid]["qty"] = qty if override else self.cart[pid]["qty"] + qty
        self.save()

    def remove(self, producto_id):
        self.cart.pop(str(producto_id), None)
        self.save()

    def clear(self):
        self.session[CART_KEY] = {}
        self.session.modified = True

    def items(self, productos_qs):
        # productos_qs: Producto.objects.filter(id__in=self.cart.keys())
        by_id = {str(p.id): p for p in productos_qs}
        for pid, data in self.cart.items():
            p = by_id.get(pid)
            if not p: 
                continue
            price = Decimal(data["price"])
            qty = int(data["qty"])
            yield {"producto": p, "qty": qty, "price": price, "subtotal": price * qty}

    def total(self):
        from decimal import Decimal
        return sum(Decimal(d["price"]) * int(d["qty"]) for d in self.cart.values())

    def save(self):
        self.session[CART_KEY] = self.cart
        self.session.modified = True
