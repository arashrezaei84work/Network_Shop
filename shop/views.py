from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json

from .models import Product, Category, Order, OrderItem, Address, Review


def base(request):
    return render(request, 'base.html')


def index(request):
    products = Product.objects.filter(is_available=True).order_by('-id')[:3]
    return render(request, 'shop/index.html', {'products': products})


def shop_view(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    price_range = request.GET.get('price_range')

    if price_range:
        try:
        
            min_p, max_p = price_range.split(',')
            products = products.filter(price__gte=min_p, price__lte=max_p)
        except ValueError:
            pass

    return render(request, 'shop/shop.html', {
        'products': products,
        'categories': categories,
        'selected_range': price_range
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    reviews = product.reviews.all()
    return render(request, 'shop/product_details.html', {'product': product, "reviews": reviews})


@login_required(login_url='shop:login')
def cart(request):
    order = Order.objects.filter(
        user=request.user,
        status=Order.STATUS_PENDING
    ).first()

    items = order.items.all() if order else []
    total_price = order.get_total_price() if order else 0

    return render(request, 'shop/cart.html', {
        'order': order,
        'items': items,
        'total_price': total_price
    })


@login_required
def checkout(request):
    order = Order.objects.filter(user=request.user, status=Order.STATUS_PENDING).first()

    if not order:
        messages.info(request, "سبد خرید شما خالی است.")
        return redirect("shop:cart")

    items = order.items.select_related("product")
    if not items.exists():
        return redirect("shop:cart")

    addresses = Address.objects.filter(user=request.user)
    SHIPPING_COST = 50000
    items_total = order.get_total_price()
    final_total = items_total + SHIPPING_COST

    if request.method == "POST":
        address_id = request.POST.get("address_id")
        if address_id:
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            address = Address.objects.create(
                user=request.user,
                full_name=request.POST.get("full_name"),
                phone=request.POST.get("phone"),
                state=request.POST.get("state"),
                city=request.POST.get("city"),
                address=request.POST.get("address"),
            )

        order.full_name = address.full_name
        order.phone = address.phone
        order.state = address.state
        order.city = address.city
        order.address = address.address
        order.status = Order.STATUS_PAID
        order.save()

        return redirect("shop:order_success")

    return render(request, "shop/checkout.html", {
        "order": order,
        "items": items,
        "addresses": addresses,
        "items_total": items_total,
        "shipping_cost": SHIPPING_COST,
        "final_total": final_total,
    })










@require_POST
@login_required
def add_to_cart(request, product_id):
    data = json.loads(request.body)
    quantity = int(data.get('quantity', 1))

    product = get_object_or_404(Product, id=product_id, is_available=True)

    if quantity > product.stock:
        return JsonResponse({'success': False, 'error': 'OUT_OF_STOCK'}, status=400)

    order, _ = Order.objects.get_or_create(
        user=request.user,
        status=Order.STATUS_PENDING
    )

    item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={'quantity': quantity, 'price': product.price}
    )

    if not created:
        if item.quantity + quantity > product.stock:
            return JsonResponse({'success': False, 'error': 'OUT_OF_STOCK'}, status=400)
        item.quantity += quantity
        item.save()

    return JsonResponse({'success': True})




@login_required
def order_success(request):
    return render(request, 'shop/order_success.html')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user,
        order__status=Order.STATUS_PENDING
    )
    item.delete()
    return redirect('shop:cart')


@login_required
def increase_item(request, item_id):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user,
        order__status=Order.STATUS_PENDING
    )

    if item.quantity + 1 <= item.product.stock:
        item.quantity += 1
        item.save()

    return redirect('shop:cart')


@login_required
def decrease_item(request, item_id):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user,
        order__status=Order.STATUS_PENDING
    )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('shop:cart')


def contact_us(request):
    return render(request, 'shop/contact_us.html')


def about(request):
    return render(request, 'shop/About.html')





@login_required
@require_POST
def add_review(request):
    """
    Handles AJAX request to add a new product review.
    Uses JSON body instead of form data.
    """
    try:
        # 1. Parse JSON data from request body
        data = json.loads(request.body)
        comment = data.get("comment", "").strip()
        product_id = data.get("product_id")

        # 2. Basic validation
        if not comment:
            return JsonResponse({"error": "empty"}, status=400)
        
        if not product_id:
            return JsonResponse({"error": "Product ID is missing"}, status=400)

        # 3. Create the review object in the database
        # Note: product_id is used directly as a foreign key field
        review = Review.objects.create(
            user=request.user,
            product_id=product_id,
            comment=comment
        )

        # 4. Return success response with Persian relative time
        return JsonResponse({
            "username": request.user.username,
            "comment": review.comment,
            "created": "همین الان"
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        # Catch any unexpected errors
        return JsonResponse({"error": str(e)}, status=500)
    

@csrf_exempt
def chatbot_api(request):
    # Check if the request method is POST
    if request.method != "POST":
        return JsonResponse({"reply": "درخواست نامعتبر است"})

    data = json.loads(request.body)
    message = data.get("message", "").strip()
    if not message:
        return JsonResponse({"reply": "لطفاً سوال خود را وارد کنید 😊"})

    msg = message.lower()
    
    # greeting
    greetings = ["سلام", "درود", "صبح بخیر", "عصر بخیر", "hi", "hello"]
    if any(greet in msg for greet in greetings):
        return JsonResponse({"reply": "سلام! خوش آمدید. چطور می‌توانم در خرید تجهیزات شبکه به شما کمک کنم؟"})

    # baresi nazarat    
    review_keywords = ["نظر", "تجربه", "کامنت", "نظرات", "review"]
    if any(word in msg for word in review_keywords):
        search_query = msg
        for word in review_keywords:
            search_query = search_query.replace(word, "")
        
        product = Product.objects.filter(name__icontains=search_query.strip()).first()
        
        if product:
            reviews = Review.objects.filter(product=product).order_by('-created_at')[:3]
            
            if reviews.exists():
                reply = f"💬 <b>آخرین نظرات برای {product.name}:</b><br><br>"
                for rev in reviews:
                    reply += f"👤 <b>{rev.user.username}:</b> {rev.comment[:100]}...<br>"
                    reply += f"🗓️ <small>{rev.created_at.strftime('%Y-%m-%d')}</small><br><hr>"
                
                reply += f"<a href='/shop/product/{product.slug}/'>مشاهده همه نظرات</a>"
                return JsonResponse({"reply": reply})
            else:
                return JsonResponse({"reply": f"هنوز نظری برای <b>{product.name}</b> ثبت نشده است."})

    #  (logic)
    category_keywords = {
        "روتر": ["روتر", "router", "wifi"],
        "سوییچ": ["سوییچ", "switch"],
        "کابل": ["کابل", "cat", "lan"],
        "مودم": ["مودم", "فیبر", "ont"]
    }

    products = Product.objects.none()
    for category, keywords in category_keywords.items():
        if any(k in msg for k in keywords):
            products = Product.objects.filter(Q(name__icontains=category) | Q(category__title__icontains=category), is_available=True)[:3]
            break

    if not products.exists():
        products = Product.objects.filter(name__icontains=message, is_available=True)[:3]

    if products.exists():
        reply = "🔍 این محصولات پیشنهاد می‌شوند:<br><br>"
        for p in products:
            reply += f"🔹 <b>{p.name}</b><br>💰 قیمت: {p.price:,} ریال<br><a href='/shop/product/{p.slug}/' target='_blank'>مشاهده و خرید</a><br><br>"
    else:
        reply = "😕 متوجه نشدم. می‌توانید درباره محصولات (مثل سوییچ یا روتر) بپرسید یا نام محصول را برای دیدن نظرات وارد کنید."

    return JsonResponse({"reply": reply})