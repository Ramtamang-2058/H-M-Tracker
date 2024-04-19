from django.db import models

class Product(models.Model):
    user = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    price = models.CharField(max_length=255, null=True, blank=True)
    user_price = models.CharField(max_length=255, null=True, blank=True)
    current_price = models.CharField(default='0.00', max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

  
class ProductUrl(models.Model):
    user = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user


class ProductUser(models.Model):
    user = models.CharField(max_length=255, null=True, blank=True)
    token = models.CharField(max_length=8000, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user