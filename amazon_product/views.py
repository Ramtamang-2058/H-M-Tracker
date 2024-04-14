# views.py
from .models import Product, ProductUrl
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import requests
from bs4 import BeautifulSoup
import re

from rest_framework.decorators import api_view
from rest_framework.response import Response
from bs4 import BeautifulSoup
import requests
import re

@api_view(['POST'])
def scrape_amazon(request):
    url = request.data.get('url')
    user = request.data.get("user")
    if user and url and is_valid(user=user, url=url):
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
            product_data = {"user": user}

            try:
                title_h1 = soup.find("h1")
                product_data["title"] = title_h1.get_text(strip=True)
            except:
                product_data["title"] = None
            try:
                img_tag = soup.find('figure', class_='pdp-image').find('img')
                image = f"https:{img_tag['src']}"
                product_data["image"] = image
            except:
                product_data["image"] = None

            try:
                price_span = soup.find("span", class_="price-value")
                product_data["price"] = price_span.get_text(strip=True)
            except:
                product_data["price"] = None

            response = save_product_to_database(product_data, url)
            if response:
                return Response(product_data)
            else:
                return Response({"error":"Failed to save on database."}, status=500)
        else:
            return Response({"error": "Failed to fetch data from the URL."}, status=400)
    else:
        return Response({"error": "URL or user parameter is missing. OR user already associated with Product."}, status=400)

def save_product_to_database(product_data, url):
    user_instance =User.objects.get(username=product_data["user"])
    if user_instance:
        ProductUrl.objects.create(user=product_data["user"], url=url)

    product_instance = Product.objects.create(
        user=user_instance,
        name=product_data.get("title"),
        image=product_data.get("image"),
        price=product_data.get("price")
    )
    return product_instance


@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if username and password:
        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return Response({"message": "Username already exists"}, status=400)
        
        # Create the user
        user = User.objects.create_user(username=username, password=password)
        return Response({"message": "User created successfully"}, status=201)
    else:
        return Response({"message": "Username and password are required"}, status=400)



@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if username and password:
        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None:
            return Response({"message": "Login successful", "user": user.username}, status=200)
        else:
            return Response({"message": "Invalid username or password"}, status=400)
    else:
        return Response({"message": "Username and password are required"}, status=400)
    

def is_valid(user, url):
    if ProductUrl.objects.filter(user=user, url=url).exists():
        return False
    else:
        return True