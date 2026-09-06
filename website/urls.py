from django.urls import path
from website import views


app_name = 'website'

urlpatterns = [
    path('', views.index, name='home'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('about/', views.about, name='about'),
]
