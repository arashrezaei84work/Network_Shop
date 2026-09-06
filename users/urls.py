from django.urls import path
from users import views
from django.contrib.auth import views as auth_views
app_name = 'users'

urlpatterns = [

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('signup/', views.signup, name='signup'),

    path('panel/', views.user_panel, name='user-panel'),
    path('panel/orders/', views.user_orders, name='user-orders'),
    path("panel/addresses/", views.user_addresses, name="user-addresses"),
    path("panel/addresses/add/", views.add_address, name="add-address"),
    path('panel/profile/', views.user_profile, name='user-profile'),

]
