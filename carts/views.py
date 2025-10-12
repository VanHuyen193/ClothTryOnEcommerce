from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []

    if request.method == 'POST':
        # Lọc bỏ csrf token và các trường không phải variation
        for key, value in request.POST.items():
            if key == 'csrfmiddlewaretoken':
                continue
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    # Tạo hoặc lấy cart
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    # Lấy tất cả cart items cho product này trong cart
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    # Chuẩn hóa product_variation thành tuple id đã sort để so sánh ổn định
    product_var_ids = tuple(sorted([v.id for v in product_variation])) if product_variation else ()

    if cart_items.exists():
        ex_var_list = []   # danh sách tuple ids
        id_list = []

        for cart_item in cart_items:
            existing_var_ids = tuple(sorted([v.id for v in cart_item.variations.all()]))
            ex_var_list.append(existing_var_ids)
            id_list.append(cart_item.id)

        # Nếu tồn tại item có cùng variation -> tăng quantity
        if product_var_ids in ex_var_list:
            index = ex_var_list.index(product_var_ids)
            item_id = id_list[index]
            existing_item = CartItem.objects.get(product=product, id=item_id)
            existing_item.quantity += 1
            existing_item.save()
        else:
            # Nếu chưa có -> tạo item mới và gán variation
            new_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if product_variation:
                new_item.variations.add(*product_variation)
            new_item.save()
    else:
        # Chưa có item nào -> tạo mới
        new_cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if product_variation:
            new_cart_item.variations.add(*product_variation)
        new_cart_item.save()

    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'carts/cart.html', context)