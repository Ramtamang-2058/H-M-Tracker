# serializers.py

from rest_framework import serializers


class AmazonProductSerializer(serializers.Serializer):
    title = serializers.CharField()
    images = serializers.ListField(child=serializers.CharField())
    price = serializers.CharField()
    rating = serializers.CharField()
    specs = serializers.ListField(child=serializers.DictField())
