from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User, Group
from shop.models import Order, Address
# Create your views here.



def signup(request):
    pass





@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'users/user_orders.html', {'orders': orders})




@login_required
def user_addresses(request):
    if request.method == "POST":
        Address.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            state=request.POST.get("state"),
            city=request.POST.get("city"),
            address=request.POST.get("address"),
        )
        return redirect("users:user-addresses")

    addresses = Address.objects.filter(user=request.user).order_by("-id")

    return render(request, "users/user_addresses.html", {
        "addresses": addresses
    })


@login_required
def add_address(request):
    if request.method == "POST":
        Address.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            state=request.POST.get("state"),
            city=request.POST.get("city"),
            address=request.POST.get("address"),
        )
        return redirect("users:user-addresses")

    return render(request, "users/add_address.html")







@login_required(login_url='shop:login')
def user_panel(request):
    user = request.user

    orders = Order.objects.filter(user=user)
    paid_orders = orders.filter(status=Order.STATUS_PAID)
    pending_orders = orders.filter(status=Order.STATUS_PENDING)

    addresses = user.addresses.all()  # from Address model

    context = {
        "orders_count": orders.count(),
        "paid_orders_count": paid_orders.count(),
        "pending_orders_count": pending_orders.count(),
        "last_orders": orders[:5],
        "addresses": addresses,
    }

    return render(request, "users/user_panel.html", context)







@login_required(login_url='users:login')
def user_profile(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "رمز عبور با موفقیت تغییر کرد")
            return redirect("users:user-profile")
        else:
          
            messages.error(request, "لطفاً خطاهای زیر را برطرف کنید.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "users/user_profile.html", {"form": form})
