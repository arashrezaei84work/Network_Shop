from django.shortcuts import render
from shop.models import Product
# Create your views here.

def index(request):
    products = Product.objects.filter(is_available=True).order_by('-id')[:3]
    return render(request, 'website/index.html', {'products': products})

def contact_us(request):
    return render(request, 'website/contact_us.html')


def about(request):
    return render(request, 'website/About.html')
