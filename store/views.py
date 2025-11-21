from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
from carts.models import CartItem
from django.db.models import Q

from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct

import os
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from .models import Product


# Create your views here.
def store(request, category_slug=None):
    categories = None

    # All products
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.filter(is_available=True).order_by("id")

    # Size
    size = request.GET.get("size")
    if size:
        products = products.filter(
            variation__variation_category="size",
            variation__variation_value__iexact=size,
            variation__is_active=True
        ).distinct()

    # Price
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Pagination
    paginator = Paginator(products, 6)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
        "products": paged_products,
        "product_count": product_count,
    }
    return render(request, "store/store.html", context)



def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product
        ).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(
                user=request.user, product_id=single_product.id
            ).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(
        product_id=single_product.id, status=True
    )

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(
        product_id=single_product.id
    )

    context = {
        "single_product": single_product,
        "in_cart": in_cart,
        "orderproduct": orderproduct,
        "reviews": reviews,
        "product_gallery": product_gallery,
    }
    return render(request, "store/product_detail.html", context)


def search(request):
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            products = Product.objects.order_by("-created_date").filter(
                Q(description__icontains=keyword)
                | Q(product_name__icontains=keyword)
            )
            product_count = products.count()
    context = {
        "products": products,
        "product_count": product_count,
    }
    return render(request, "store/store.html", context)


def submit_review(request, product_id):
    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id
            )
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(
                request, "Thank you! Your review has been updated."
            )
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data["subject"]
                data.rating = form.cleaned_data["rating"]
                data.review = form.cleaned_data["review"]
                data.ip = request.META.get("REMOTE_ADDR")
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(
                    request, "Thank you! Your review has been submitted."
                )
                return redirect(url)


@csrf_exempt
def try_on(request, product_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed"}, status=405)

    # Nếu muốn lưu ảnh input lại thì xử lý ở đây
    # uploaded = request.FILES.get("input_image")

    # ĐƯỜNG DẪN ĐÚNG ĐẾN mysite/static/images/test
    static_test_dir = os.path.join(
        settings.BASE_DIR, "mysite", "static", "images", "test"
    )

    if not os.path.isdir(static_test_dir):
        return JsonResponse(
            {"error": f"Folder not found: {static_test_dir}"}, status=500
        )

    exts = (".png", ".jpg", ".jpeg", ".gif")
    files = [
        f for f in os.listdir(static_test_dir) if f.lower().endswith(exts)
    ]
    if not files:
        return JsonResponse(
            {"error": "No result image in static/images/test"}, status=404
        )

    # Lấy file mới nhất
    latest_file = max(
        files,
        key=lambda f: os.path.getmtime(os.path.join(static_test_dir, f)),
    )

    # URL để browser load ảnh
    # STATIC_URL mặc định là "/static/"
    result_url = settings.STATIC_URL + f"images/test/{latest_file}"

    return JsonResponse({"result_url": result_url})
