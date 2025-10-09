from django.shortcuts import redirect, render, get_object_or_404
from .cart import Cart
from productos.models import Producto

def add_item(request, producto_id):
    prod = get_object_or_404(Producto, id=producto_id, activo=True)
    qty = int(request.POST.get('qty', 1))
    Cart(request).add(prod, qty=qty)
    return redirect('carrito:ver')

def update_item(request, producto_id):
    qty = int(request.POST.get('qty', 1))
    prod = get_object_or_404(Producto, id=producto_id)
    Cart(request).add(prod, qty=qty, override=True)
    return redirect('carrito:ver')

def remove_item(request, producto_id):
    Cart(request).remove(producto_id)
    return redirect('carrito:ver')

def clear(request):
    Cart(request).clear()
    return redirect('carrito:ver')

def ver_carrito(request):
    cart = Cart(request)
    ids = list(cart.cart.keys())
    productos = Producto.objects.filter(id__in=ids)
    contexto = {
        "items": list(cart.items(productos)),
        "total": cart.total(),
    }
    return render(request, 'carrito/ver.html', contexto)

# Create your views here.
