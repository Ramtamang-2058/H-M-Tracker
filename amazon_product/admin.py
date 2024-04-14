from django.contrib import admin
from . models import Product, ProductUrl

admin.site.register(Product)
admin.site.register(ProductUrl)