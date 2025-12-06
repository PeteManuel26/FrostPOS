from django.shortcuts import render, redirect
from .models import Product, Order, OrderItem, Category
from .cart import Cart
def product_list(request):
    products = Product.objects.all()
    return render(request, "products.html", {"products": products})


def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session["cart"] = cart
    return redirect("cart")


def cart_view(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total = 0

    for product_id, qty in cart.items():
        product = Product.objects.get(id=product_id)
        line_total = product.price * qty
        total += line_total

        cart_items.append({
            "product": product,
            "qty": qty,
            "line_total": line_total
        })

    return render(request, "cart.html", {"cart_items": cart_items, "total": total})


def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("products")

    order = Order.objects.create(total=0)
    total = 0

    for product_id, qty in cart.items():
        product = Product.objects.get(id=product_id)
        line_total = product.price * qty
        OrderItem.objects.create(order=order, product=product, qty=qty, line_total=line_total)

        product.stock -= qty
        product.save()

        total += line_total

    order.total = total
    order.save()

    request.session["cart"] = {}

    return render(request, "receipt.html", {"order": order})

def scan_barcode(request):
    barcode = request.GET.get("barcode")
    cart = Cart(request)

    if barcode:
        product = Product.objects.filter(barcode=barcode).first()
        if product:
            cart.add(product.id, 1)
            return redirect("cart")
        else:
            return render(request, "not_found.html", {"barcode":barcode})

    return render(request,"scan_barcode.html")

def inventory(request):
    products = Product.objects.all()
    return render(request, "inventory.html", {"products": products})

def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        barcode = request.POST.get("barcode")
        category_id = request.POST.get("category")
        category = Category.objects.get(id=category_id)

        Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            barcode=barcode,
            category=category
        )
        return redirect("inventory")

    categories = Category.objects.all()
    return render(request, "add_product.html", {"categories": categories})

def remove_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect("inventory")  

def update_cart(request, product_id):
    if request.method == "POST":
        action = request.POST.get("action")
        cart = Cart(request)
        product = Product.objects.get(id=product_id)

        if action == "increase":
            if cart.cart.get(str(product_id), 0) < product.stock:
                cart.add(product_id, 1)
        elif action == "decrease":
            if cart.cart.get(str(product_id), 0) > 1:
                cart.cart[str(product_id)] -= 1
                cart.save()
            else:
                cart.remove(product_id)
        elif action == "remove":
            cart.remove(product_id)

    return redirect("cart")
