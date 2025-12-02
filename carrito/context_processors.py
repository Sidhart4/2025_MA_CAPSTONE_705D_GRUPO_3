# carrito/context_processors.py

def cart_context(request):
    """
    Hace disponible en todas las plantillas:
      - cart_count: total de unidades en el carrito (sesión)
      - cart_total: total en $ (entero)
    No depende de carrito.views para evitar importaciones circulares.
    """
    cart = request.session.get("cart", {}) or {}

    # Suma segura
    count = 0
    total = 0
    for it in cart.values():
        try:
            qty = int(it.get("qty", 0))
            price = int(it.get("price", 0))
        except Exception:
            qty = 0
            price = 0
        count += qty
        total += qty * price

    return {
        "cart_count": count,
        "cart_total": total,
    }
