from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from .serializers import ProductSerializer, SupplierSerializer


def health(request):
    return JsonResponse({'status': 'ok'})

def info(request):
    return JsonResponse({'name': 'Lilis', 'version': '1.0', 'autor': 'imVic'})


class producto_view_set(viewsets.ModelViewSet):
    queryset = ProductSerializer.Meta.model.objects.all()
    serializer_class = ProductSerializer

class supplier_view_set(viewsets.ModelViewSet):
    queryset = SupplierSerializer.Meta.model.objects.all()
    serializer_class = SupplierSerializer