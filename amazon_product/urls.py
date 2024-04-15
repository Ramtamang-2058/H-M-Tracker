# urls.py

from django.urls import path
from .views import (
    scrape_amazon,
    register_user,
    login_user,
    get_product_details,
    get_products_by_user,
    delete_product,
    update_product,
)


urlpatterns = [
    path('scrape/', scrape_amazon, name='scrape_amazon'),
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('products/', get_products_by_user, name='get_products_by_user'),
    path('products/<int:product_id>/', get_product_details, name='get_product_details'),
    path('products/delete/', delete_product, name='delete_product'),
    path('products/update/', update_product, name='update_product'),
]
