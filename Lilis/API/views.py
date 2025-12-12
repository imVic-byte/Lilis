from django.shortcuts import render, redirect
from django.http import JsonResponse
import Lilis
from Sells.services import WarehouseService
from django.views import View
from Sells.views import warehouse_to_dict
from rest_framework import viewsets
from .serializers import ProductSerializer, SupplierSerializer, LilisSerializer
from rest_framework.permissions import IsAuthenticated
from .forms import LilisForm
import requests
from Main.mixins import StaffRequiredMixin, GroupRequiredMixin

from API import serializers

API_ENDPOINT = 'http://3.228.61.121/api/lilis/'

def health(request):
    return JsonResponse({'status': 'ok'})

def info(request):
    return JsonResponse({'name': 'Lilis', 'version': '1.0', 'autor': 'imVic'})


class producto_view_set(viewsets.ModelViewSet):
    queryset = ProductSerializer.Meta.model.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class supplier_view_set(viewsets.ModelViewSet):
    queryset = SupplierSerializer.Meta.model.objects.all()
    serializer_class = SupplierSerializer

class LilisViewSet(viewsets.ModelViewSet):
    queryset = LilisSerializer.Meta.model.objects.all()
    serializer_class = LilisSerializer

class LilisDetailView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas",
        "Acceso limitado a Compras"
    )
    warehouse_service = WarehouseService()

    def get(self, request):
        try:
            response = requests.get(API_ENDPOINT)
            if response.status_code == 200:
                lilis_data = response.json()
                data = {
                    'rut': lilis_data[0]['rut'],
                    'bussiness_name': lilis_data[0]['bussiness_name'],
                    'fantasy_name': lilis_data[0]['fantasy_name'],
                    'email': lilis_data[0]['email'],
                    'phone': lilis_data[0]['phone'],
                    'address': lilis_data[0]['address'],
                    'web_site': lilis_data[0]['web_site'],
                    'warehouse': self.warehouse_service.list().filter(lilis=True)
                }
                context = {'b': data}
                return render(request, 'lilis_detail.html', context)
            else:
                return render(request, 'lilis_detail.html', {'error': 'Error fetching data from API.'})
        except requests.exceptions.RequestException as e:
            print("Request Exception:", e)
            return render(request, 'lilis_detail.html', {'error': 'Error connecting to API.'})
    
class LilisCreateView(StaffRequiredMixin, View):
    form_class = LilisForm
    template_name = 'lilis_create.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                response = requests.post(API_ENDPOINT, json=data)
                if response.status_code == 201:
                    return redirect('lilis_detail')
                else:
                    error_api = response.json()
                    print("Error API:", error_api)
                    context = {'form': form, 'api_error': error_api}
                    return render(request, self.template_name, context)
            except requests.exceptions.RequestException as e:
                print("Request Exception:", e)
                context = {'form': form, 'api_error': 'Error connecting to API.'}
                return render(request, self.template_name, context)
        else:
            context = {'form': form}
            return render(request, self.template_name, context)
        
class LilisUpdateView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
    )
    form_class = LilisForm
    template_name = 'lilis_update.html'

    def get(self, request, *args, **kwargs):
        try:
            response = requests.get(API_ENDPOINT)
            if response.status_code == 200:
                lilis_data = response.json()[0]
                form = self.form_class(initial=lilis_data)
                context = {'form': form}
                return render(request, self.template_name, context)
            else:
                return render(request, self.template_name, {'error': 'Error fetching data from API.'})
        except requests.exceptions.RequestException as e:
            print("Request Exception:", e)
            return render(request, self.template_name, {'error': 'Error connecting to API.'})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                API_DETAIL_ENDPOINT = f"{API_ENDPOINT}1/"
                response = requests.put(API_DETAIL_ENDPOINT, json=data)
                if response.status_code == 200:
                    return redirect('lilis_detail')
                else:
                    error_api = response.json()
                    print("Error API:", error_api)
                    context = {'form': form, 'api_error': error_api}
                    return render(request, self.template_name, context)
            except requests.exceptions.RequestException as e:
                print("Request Exception:", e)
                context = {'form': form, 'api_error': 'Error connecting to API.'}
                return render(request, self.template_name, context)
        else:
            context = {'form': form}
            return render(request, self.template_name, context)
        
class WarehouseListForLilisView(View):
    warehouse_service = WarehouseService()

    def get(self, request):
        warehouses = self.warehouse_service.list().filter(lilis=False)
        warehouses_list = []
        for w in warehouses:
            warehouses_list.append({
                'id': w.id,
                'name': w.name,
                'address': w.address,
                'total_area': str(w.total_area),
                'location': w.location,
                'is_active': w.is_active,
            })
        return JsonResponse({'warehouses': warehouses_list})
    
class WarehouseAssignView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        "Acceso limitado a Produccion",
    )
    warehouse_service = WarehouseService()

    def get(self, request):
        warehouse_id = request.GET.get('warehouse')
        warehouse = self.warehouse_service.get(warehouse_id)
        if warehouse:
            warehouse.lilis = True
            warehouse.save()
            return redirect('lilis_detail')
        else:
            return redirect('lilis_detail')
        
class WarehouseUnassignView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        "Acceso limitado a Produccion",
    )
    warehouse_service = WarehouseService()

    def get(self, request):
        warehouse_id = request.GET.get('warehouse')
        warehouse = self.warehouse_service.get(warehouse_id)
        if warehouse:
            warehouse.lilis = False
            warehouse.save()
            return redirect('lilis_detail')
        else:
            return redirect('lilis_detail')