# views.py
from .models import Product, ProductUrl, ProductUser
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import JsonResponse
import requests

from rest_framework.response import Response
from bs4 import BeautifulSoup
import requests

from django.views.decorators.csrf import csrf_exempt
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from background_task import background
from .task import check_and_update_product


@csrf_exempt
@api_view(['POST'])
def scrape_amazon(request):
    url = request.data.get('url')
    user = request.data.get("user")
    user_price = request.data.get("price")
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
            product_data = {"user": user, "user_price": user_price}

            try:
                title_h1 = soup.find("h1")
                product_data["title"] = title_h1.get_text(strip=True)
            except:
                product_data["title"] = None
            try:
                img_src = soup.find('div', class_='fcc68c a33b36 f6e252')
                if not img_src:
                    img_src = soup.find('div', class_='def5f0 fcc68c a33b36 f6e252')
                img_tag = img_src.find('img')
                image = img_tag['src']
                product_data["image"] = image
            except:
                product_data["image"] = None

            try:
                price_span = soup.find("span", class_="edbe20 ac3d9e d9ca8b")
                product_data["price"] = price_span.get_text(strip=True)
            except:
                product_data["price"] = None

            response = save_product_to_database(product_data, url)
            if response:
                return Response(product_data)
            else:
                return Response({"error": "Failed to save on database."}, status=500)
        else:
            return Response({"error": "Failed to fetch data from the URL."}, status=400)
    else:
        return Response({"error": "URL or user parameter is missing. OR user already associated with Product."},
                        status=400)


def save_product_to_database(product_data, url):
    """
    Save data of product to the database
    """
    product_instance = Product.objects.create(
        user=product_data.get("user"),
        name=product_data.get("title"),
        image=product_data.get("image"),
        price=product_data.get("price"),
        user_price=product_data.get("user_price"),
        current_price=product_data.get("price"),
        url=url
    )
    return product_instance


@csrf_exempt
@api_view(['POST'])
def register_user(request):
    """
    Register user with token
    """
    user = request.data.get('user')
    token = request.data.get('token')
    status = request.data.get('status')

    if user and token:
        # Check if the username already exists
        if ProductUser.objects.filter(user=user).exists():
            user_data = ProductUser.objects.get(user=user)
            user_data.user = user
            user_data.token = token
            user_data.status = status
            user_data.save()
            device = FCMDevice()
            device.name = user
            device.registration_id = token
            device.device_id = user
            device.type = "android"
            device.save()
            products = Product.objects.filter(user=user)
            for product in products:
                check_and_update_product(product=product)
            return Response({"message": "Successfull"}, status=200)

        # Create the user
        user = ProductUser(user=user, token=token, status=status)
        user.save()
        return Response({"message": "Successfull"}, status=200)
    else:
        return Response({"message": "Token and User Invalid"}, status=301)


@csrf_exempt
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
    """
    validate user exist or not.
    """
    if ProductUrl.objects.filter(user=user, url=url).exists():
        return False
    else:
        product_instance = ProductUrl(
            user=user,
            url=url
        )
        product_instance.save()
        return True


def get_products_by_user(request):
    """
    Get all products by the user.
    """
    user = request.GET.get('user')
    products = Product.objects.filter(user=user)

    for product in products:
        check_and_update_product(product=product)
    data = [{
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'target_price': product.user_price,
        'current_price': product.current_price,
        'image': product.image,
        'url': product.url}
        for product in products]
    return JsonResponse(data, safe=False)


def get_product_details(request, product_id):
    """
    Get product details with product ID.
    """
    try:
        product = Product.objects.get(pk=product_id)
        check_and_update_product(product=product)
        data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'target_price': product.user_price,
            'current_price': product.current_price,
            'created_date': product.created_date,
            'modified_date': product.modified_date,
            'image': product.image,
            'url': product.url,
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


@csrf_exempt
@api_view(['POST'])
def delete_product(request):
    """
    Delete product.
    """
    id = request.data.get('id')

    if id:
        try:
            product = Product.objects.get(id=id)
            product.delete()
            return Response({"message": "Product deleted successfully"}, status=200)
        except Product.DoesNotExist:
            return Response({"message": "Product does not exist"}, status=404)
    else:
        return Response({"message": "Please provide product ID"}, status=400)


@csrf_exempt
@api_view(['POST'])
def update_product(request):
    """
    Update product.
    """
    product_id = request.data.get('id')
    user_price = request.data.get('target_price')

    if product_id and user_price:
        try:
            product = Product.objects.get(id=product_id)
            product.user_price = user_price
            product.save()
            check_and_update_product(product=product)
            return Response({"message": "Product Update successfully"}, status=200)
        except Product.DoesNotExist:
            return Response({"message": "Product does not exist"}, status=404)
    else:
        return Response({"message": "Bad request"}, status=400)


def notify(request):
    """
    Test notification.
    """
    # Assuming Message and Notification classes are defined somewhere
    message = Message(
        notification=Notification(title="Price Drop Alert: $78", body="Mne Man Gens  6/7 gen", image="https://play-lh.googleusercontent.com/yv-m6uiayzk8I95XavI3iANy1KsidyZapBgMxwMuIYERQUKbLJ0X5hfpzaNR8WfckrM=w240-h480-rw")
    )
    device = FCMDevice.objects.first()
    device.send_message(message)
    return Response(status=200)
