# urls.py

from django.urls import path
from .views import scrape_amazon, register_user, login_user

urlpatterns = [
    path('scrape/', scrape_amazon, name='scrape_amazon'),
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
]
