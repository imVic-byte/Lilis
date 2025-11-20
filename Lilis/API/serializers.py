from rest_framework import serializers
from Products.models import Producto, Supplier

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'