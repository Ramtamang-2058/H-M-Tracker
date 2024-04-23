# views.py
from .models import Product
import requests

from bs4 import BeautifulSoup
import requests

from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from background_task import background
import re


def check_and_update_product(product):
    
    try:
        product_price = scrap_price(product.url)
        product.current_price = product_price if product_price else product.user_price
        product.save()
        current_price = extract_integer_price(product_price)
        user_price = extract_integer_price(product.user_price)
        if current_price < user_price:
                notify_user(user=product.user, name=product.name, image=product.image, price=product_price)
        
        return
    
    except Exception as e:
        return

@background(schedule=3600)
def my_job():
    try:
        products = Product.objects.all()
        for product in products:
            product_price = scrap_price(product.url)
            product.current_price = product_price if product_price else product.user_price
            product.save()
            current_price = extract_integer_price(product_price)
            user_price = extract_integer_price(product.user_price)
            if current_price < user_price:
                notify_user(user=product.user, name=product.name, image=product.image, price=product_price)
        
        return
    
    except Exception as e:
        return


def notify_user(user, name, image, price):
    message = Message(
        notification=Notification(title=f"Price Drop Alert: {price}", body=name, image=image)
    )
    device = FCMDevice.objects.get(device_id=user)
    device.send_message(message)


def extract_integer_price(price_str):
   
    # Remove the dollar sign from the price string
    price_digits = price_str.replace('$', '')
    
    try:
        # Convert the cleaned price string to a float
        return float(price_digits)
    except ValueError:
        return None




def scrap_price(url):
    custom_headers = {
        "Accept-language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    }

    resp = requests.get(url, headers=custom_headers)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        try:
            price_span = soup.find("span", class_="price-value")
            price = price_span.get_text(strip=True)
            return price
        except:
            return


    else:
        return
