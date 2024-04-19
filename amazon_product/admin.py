from django.contrib import admin
from . models import Product, ProductUrl, ProductUser

admin.site.register(Product)
admin.site.register(ProductUrl)
admin.site.register(ProductUser)