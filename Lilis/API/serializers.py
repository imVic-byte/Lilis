from rest_framework import serializers
from Products.models import Producto, Supplier
from Accounts.models import Lilis

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class LilisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lilis
        fields = ['bussiness_name', 'fantasy_name', 'rut', 'email', 'phone', 'address','web_site']
