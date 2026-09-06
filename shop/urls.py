from django.urls import path
from .views import *

app_name = 'shop'

urlpatterns = [
    path('base/', base, name='base'),
    path('', index, name='home'),



    path('chatbot-api/', chatbot_api, name='chatbot_api'),


    path('shop/', shop_view, name='shop'),
    path('shop/product/<str:slug>/', product_detail, name='product-detail'),

    path('shop/cart/', cart, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove-from-cart'),
    path('cart/increase/<int:item_id>/', increase_item, name='increase-item'),
    path('cart/decrease/<int:item_id>/', decrease_item, name='decrease-item'),
    path("review/add/", add_review, name="add_review"),


    path('checkout/', checkout, name='checkout'),
    path('order/success/', order_success, name='order_success'),


    # path('product/<int:product_id>/add-review/', add_review, name='add_review'),
    # path('vote-review/', vote_review, name='vote_review'),
    # path('review/<int:review_id>/dislike/', dislike_review, name='dislike_review'),

    path('contact-us/', contact_us, name='contact-us'),
    path('About/', about, name='About'),
]

