from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .services import ClientService, WarehouseService, TransactionService
from Main.decorator import permission_or_redirect
from Main.utils import generate_excel_response
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from Products.services import ProductService, RawMaterialService, SupplierService
from datetime import date
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Main.mixins import GroupRequiredMixin
import requests
from django.core.serializers import serialize
from django.db.models.functions import Coalesce
from django.template.defaultfilters import truncatechars

client_service = ClientService()
warehouse_service = WarehouseService()
transaction_service = TransactionService()
product_service = ProductService()
raw_material_service = RawMaterialService()
supplier_service = SupplierService()

API_ENDPOINT = 'http://3.228.61.121/api/lilis/'

# ===================================
# VISTAS DE CLIENTES
# ===================================

class ClientListView(GroupRequiredMixin, ListView):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    model = client_service.model
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().filter(is_active=True)
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(fantasy_name__icontains=q) |
                Q(bussiness_name__icontains=q) |
                Q(rut__icontains=q) |
                Q(email__icontains=q) |
                Q(phone__icontains=q)
            )
        allowed_sort_fields = ['fantasy_name', 'bussiness_name', 'rut', 'email', 'phone']
        sort_by = self.request.GET.get('sort_by', 'fantasy_name')
        order = self.request.GET.get('order', 'asc')
        if sort_by not in allowed_sort_fields:
            sort_by = 'fantasy_name'
        if order not in ['asc', 'desc']:
            order = 'asc'
            
        order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
        qs = qs.order_by(order_by_field)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        if 'page' in query:
            query.pop('page')
        context['querystring'] = query.urlencode()
        q = (self.request.GET.get("q") or "").strip()
        sort_by = self.request.GET.get('sort_by', 'fantasy_name')
        order = self.request.GET.get('order', 'asc')
        per_page = context['paginator'].per_page
        context.update({
            "q": q,
            "current_sort_by": sort_by,
            "current_order": order,
            "order_next": "desc" if order == "asc" else "asc",
            "per_page": per_page,
        })
        return context
    
    def get_paginate_by(self, queryset):
        default_per_page = 25
        per_page = self.request.GET.get('per_page')
        try:
            per_page = int(per_page) if per_page else default_per_page
        except ValueError:
            per_page = default_per_page
        if 0 < per_page <= 100:
            return per_page
        else:
            return default_per_page

class ClientCreateView(GroupRequiredMixin, CreateView):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion"
    )
    model = client_service.model
    form_class = client_service.form_class
    success_url = reverse_lazy('client_list_all')
    template_name = 'clients/client_create.html'

class ClientUpdateView(GroupRequiredMixin, UpdateView):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion"
    )
    model = client_service.model
    form_class = client_service.form_class
    success_url = reverse_lazy('client_list_all')
    template_name = 'clients/client_update.html'

class ClientDeleteView(GroupRequiredMixin, DeleteView):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion"
    )
    model = client_service.model
    success_url = reverse_lazy('client_list_all')

    def get(self, request, *args, **kwargs):
        return HttpResponse('Metodo no permitido')
    
    def form_valid(self, form):
        self.object = self.get_object()
        self.object.is_suspended = True
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class ClientExportView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        qs = client_service.list().order_by('fantasy_name')
        if q:
            qs = qs.filter(
                Q(fantasy_name__icontains=q) |
                Q(bussiness_name__icontains=q) |
                Q(rut__icontains=q) |
                Q(email__icontains=q) |
                Q(phone__icontains=q)
            )
        qs_limit = request.GET.get("limit")
        if qs_limit:
            try:
                limit = int(qs_limit)
                if limit > 0:
                    qs = qs[:limit] 
            except ValueError:
                pass
        headers = ["Nombre Fantasía", "Razón Social", "RUT", "Email", "Teléfono"]
        data_rows = []
        for c in qs:
            data_rows.append([
                c.fantasy_name,
                c.bussiness_name,
                c.rut,
                c.email,
                c.phone,
            ])
        return generate_excel_response(headers, data_rows, "Lilis_Clientes")

def client_search(request):
    q = request.GET.get('q', '')
    clients = client_service.model.objects.filter(is_active=True).filter(
        Q(fantasy_name__icontains=q) |
        Q(bussiness_name__icontains=q) |
        Q(rut__icontains=q)
    )
    data = []
    for s in clients:
        if s.trade_terms:
            trade_terms = truncatechars(s.trade_terms, 40)
        else:
            trade_terms = "-"
        data.append({
            'id': s.id,
            'bussiness_name': s.bussiness_name,
            'fantasy_name': s.fantasy_name,
            'rut': s.rut,
            'email': s.email,
            'phone': s.phone,
            'trade_terms': trade_terms,
            'is_active': s.is_active,
            'lead_time_days': s.lead_time_days,
            'address': s.address,
            'city': s.city,
            'country': s.country,
            'payment_terms_days': s.payment_terms_days,
            'discount_percentage': s.discount_percentage,
        })
    return JsonResponse({'data': data}, safe=False)

def client_all(request):
    clients = client_service.model.objects.filter(is_active=True)
    data = []
    for s in clients:
        if s.trade_terms:
            trade_terms = truncatechars(s.trade_terms, 40)
        else:
            trade_terms = "-"
        data.append({
            'id': s.id,
            'bussiness_name': s.bussiness_name,
            'fantasy_name': s.fantasy_name,
            'rut': s.rut,
            'email': s.email,
            'phone': s.phone,
            'trade_terms': trade_terms,
            'is_active': s.is_active,
            'lead_time_days': s.lead_time_days,
            'address': s.address,
            'city': s.city,
            'country': s.country,
            'payment_terms_days': s.payment_terms_days,
            'discount_percentage': s.discount_percentage,
        })
    return JsonResponse({'data': data}, safe=False)

class ClientDetailView(GroupRequiredMixin, DetailView):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    model = client_service.model
    template_name = 'clients/client_view.html'
    context_object_name = 'b'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.object
        warehouses = warehouse_service.filter_by_client(supplier)
        context['warehouses'] = warehouses
        print(warehouses)
        return context

# ===================================
# VISTAS DE WAREHOUSES (Indentación Corregida)
# ===================================
class WarehouseListView(GroupRequiredMixin, ListView):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    model = warehouse_service.model
    template_name = 'warehouses/warehouse_list.html'
    context_object_name = 'warehouses'    
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().filter(is_active=True)
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(address__icontains=q) |
                Q(location__name__icontains=q)
            )
        allowed_sort_fields = ['name', 'address', 'location__name', 'total_area']
        sort_by = self.request.GET.get('sort_by', 'name')
        order = self.request.GET.get('order', 'asc')
        if sort_by not in allowed_sort_fields:
            sort_by = 'name'
        if order not in ['asc', 'desc']:
            order = 'asc'
            
        order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
        qs = qs.order_by(order_by_field)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        if 'page' in query:
            query.pop('page')
        context['querystring'] = query.urlencode()
        q = (self.request.GET.get("q") or "").strip()
        sort_by = self.request.GET.get('sort_by', 'name')
        order = self.request.GET.get('order', 'asc')
        per_page = context['paginator'].per_page
        context.update({
            "q": q,
            "current_sort_by": sort_by,
            "current_order": order,
            "order_next": "desc" if order == "asc" else "asc",
            "per_page": per_page,
        })
        return context
    
    def get_paginate_by(self, queryset):
        default_per_page = 25
        per_page = self.request.GET.get('per_page')
        try:
            per_page = int(per_page) if per_page else default_per_page
        except ValueError:
            per_page = default_per_page
        if 0 < per_page <= 100:
            return per_page
        else:
            return default_per_page
        
class WarehouseDetailView(GroupRequiredMixin, DetailView):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    model = warehouse_service.model
    template_name = 'warehouses/warehouse_view.html'
    context_object_name = 'w'

class WarehouseCreateView(GroupRequiredMixin, CreateView):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
    )
    model = warehouse_service.model
    form_class = warehouse_service.form_class
    success_url = reverse_lazy('warehouse_list')
    template_name = 'warehouses/warehouse_create.html'

    def get_client_object(self):
        client_id = self.request.GET.get('client')
        if client_id:
            return client_service.get(client_id)
        else:
            return None
        
    def form_valid(self, form):
        response = super().form_valid(form)
        warehouse = self.get_object
        client = self.get_client_object()
        if client:
            try:
                success, warehouse = warehouse_service.warehouse_assign(client, warehouse.id)
                if success:
                    next = self.request.GET.get('next')
                    if next:
                        return redirect(next)
                    else:
                        return redirect(self.get_success_url())
                else:
                    return render(self.request, 'warehouses/warehouse_create.html', {'form': warehouse, 'error': 'No se pudo asignar la bodega.'})
            except Exception as e:
                return render(self.request, 'warehouses/warehouse_create.html', {'form': warehouse, 'error': str(e)})
        return response
    
class WarehouseUpdateView(GroupRequiredMixin, UpdateView):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
    )
    model = warehouse_service.model
    form_class = warehouse_service.form_class
    success_url = reverse_lazy('warehouse_list')
    template_name = 'warehouses/warehouse_update.html'

    def get_client_object(self):
        client_id = self.request.GET.get('client')
        if client_id:
            return client_service.get(client_id)
        else:
            return None
        
    def form_valid(self, form):
        response = super().form_valid(form)
        client = self.get_client_object()
        next_url = self.request.GET.get('next')
        if client or next_url:
            return redirect(next_url)
        return response
                    
    
class WarehouseDeleteView(GroupRequiredMixin, DeleteView):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
    )
    model = warehouse_service.model
    success_url = reverse_lazy('warehouse_list')

    def get(self, request, *args, **kwargs):
        return HttpResponse('Metodo no permitido')
    
    def form_valid(self, form):
        w = self.get_object()
        warehouse_service.delete_warehouse(w)
        return HttpResponseRedirect(self.get_success_url())

class WarehouseUnassignView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
    )
    wareclient_service = warehouse_service
    
    def get(self, request, *args, **kwargs):
        try:
            next = request.GET.get('next')
            client_id = request.GET.get('client')
            warehouse_id = request.GET.get('warehouse')
            success, obj = self.wareclient_service.warehouse_unassign(client_id, warehouse_id)
            if success:
                return redirect(next)
            else:
                return HttpResponse(f'No se pudo asignar la bodega: {obj}')
        except Exception as e:
            return HttpResponse(str(e))

class WarehouseAssignView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
    )
    wareclient_service = warehouse_service
    
    def get(self, request, *args, **kwargs):
        try:
            next = request.GET.get('next')
            client_id = request.GET.get('client')
            client = client_service.get(client_id)
            warehouse_id = request.GET.get('warehouse')
            success, obj = self.wareclient_service.warehouse_assign(client, warehouse_id)
            if success:
                return redirect(next)
            else:
                return HttpResponse(f'No se pudo asignar la bodega: {obj}')
        except Exception as e:
            return HttpResponse(str(e))
        
class WarehouseListWithoutThisClientView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    def get(self, request, *args, **kwargs):
        try:
            client_id = request.GET.get('client')
            warehouses = warehouse_service.warehouse_list_without_this_client(client_id)
            warehouses_list = []
            for w in warehouses:
                if w.is_active:
                    warehouses_list.append({
                        'id': w.id,
                        'name': w.name,
                        'address': w.address,
                        'location': w.location,
                        'is_active': w.is_active,
                    })
            return JsonResponse({'warehouses': warehouses_list})
        except Exception as e:
            return HttpResponse(str(e))

class WarehouseExportView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        qs = warehouse_service.model.objects.all().order_by('name')
        limit = request.GET.get("limit")
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |  
                Q(address__icontains=q) 
            )
        if limit:
            try:
                limit = int(limit)
                qs = qs[:limit]
            except ValueError:
                pass
        headers = ["Nombre", "Dirección", "Ubicación", "Área Total", "Propietario"]
        data_rows = []
        for warehouse in qs:
            data_rows.append([
                warehouse.name,
                warehouse.address,
                warehouse.location,
                warehouse.total_area,
                warehouse.lilis,
            ])
        return generate_excel_response(headers, data_rows, "Lilis_Bodegas")

def get_warehouses(request): 
    id = request.GET.get('id')
    type = request.GET.get('type')
    if type == 'salida':
        warehouses_list = []
        if id:
            client = client_service.get(id)
            if client:
                warehouses = warehouse_service.filter_by_client(client)
                for w in warehouses:
                    warehouses_list.append({
                        'id': w.id,
                        'name': w.name,
                        'address': w.address,
                        'location': w.location,
                    })
        return JsonResponse({'warehouses': warehouses_list})
    elif type == 'ingreso':
        warehouses_list = []
        if id:
            suppliers = supplier_service.list_actives()
            for s in suppliers:
                warehouses = warehouse_service.filter_by_supplier(s)
                for w in warehouses:
                    warehouses_list.append({
                        'id': w.id,
                        'name': w.name,
                        'address': w.address,
                        'location': w.location,
                    })
            return JsonResponse({'warehouses': warehouses_list})    
    else:
        warehouses_list = []
        if id:
            clients = client_service.list_actives().filter(id=id)

def get_stock_by_product(request):
    product = request.GET.get('product_id')
    p, id = product.split('-')
    if p == 'product':
        stock = product_service.get_stock_by_product(id)
    else:
        stock = raw_material_service.get_stock_by_raw_material(id)
    return JsonResponse({'stock': stock})


def warehouse_to_dict(w):
    return {
        'id': w.id,
        'name': w.name,
        'address': w.address,
        'location': w.location,
    }


def raw_material_to_dict(rm):
    return {
        'id': rm.id,
        'name': rm.name,
        'sku': rm.sku,
        'measurement_unit': rm.measurement_unit,
    }


def supplier_base_dict(s):
    return {
        'id': s.id,
        'bussiness_name': s.bussiness_name,
        'rut': s.rut,
    }


def get_warehouses_for_client(client):
    warehouses = warehouse_service.filter_by_client(client)
    return [warehouse_to_dict(w) for w in warehouses]

def warehouses_by_client(request):
    id = request.GET.get('id')
    warehouses = warehouse_service.filter_by_client(id)
    return JsonResponse({'warehouses': [warehouse_to_dict(w) for w in warehouses]})

def handle_ingreso():
    data = {
        'warehouses': [],
        'suppliers': [],
    }
    warehouses = warehouse_service.list().filter(lilis=True).filter(is_active=True)
    for w in warehouses:
        warehouse_data = warehouse_to_dict(w)
        data['warehouses'].append(warehouse_data)
    print(data)
    suppliers = supplier_service.list_actives()
    for s in suppliers:
        supplier_data = supplier_base_dict(s)
        rms = transaction_service.inventario.raw_class.objects.filter(supplier_id=s.id)
        supplier_data['raw_materials'] = [raw_material_to_dict(rm) for rm in rms]
        data['suppliers'].append(supplier_data)
    return JsonResponse({'data': data})

def handle_salida():
    data = []
    clients = client_service.list_actives()
    for c in clients:
        client_data = {
            'id': c.id,
            'bussiness_name': c.bussiness_name,
            'rut': c.rut,
            'warehouses': get_warehouses_for_client(c),
        }
        data.append(client_data)

    return JsonResponse({'data': data})


def handle_devolucion():
    data = {
        'clients': [],
        'products': [],
        'raw_materials': [],
        'warehouses': [],
    }
    clients = client_service.list_actives()
    for c in clients:
        data['clients'].append(supplier_base_dict(c))
    suppliers = supplier_service.list_actives()
    for s in suppliers:
        data['clients'].append(supplier_base_dict(s))
    products = transaction_service.inventario.product_class.objects.all().filter(is_active=True)
    for p in products:
        data['products'].append(raw_material_to_dict(p))
    raw_materials = transaction_service.inventario.raw_class.objects.all().filter(is_active=True)
    for rm in raw_materials:
        data['raw_materials'].append(raw_material_to_dict(rm))
    warehouses = warehouse_service.list().filter(is_active=True).filter(lilis=True)
    for w in warehouses:
        data['warehouses'].append(warehouse_to_dict(w))
    return JsonResponse({'data': data})

def inventario_to_dict(i):
    if i.producto:
        return {
            'id': i.id,
            'name': i.producto.name,
            'sku': i.producto.sku,
            'measurement_unit': i.producto.measurement_unit
        }
    if i.materia_prima:
        return {
            'id': i.id,
            'name': i.materia_prima.name,
            'sku': i.materia_prima.sku,
            'measurement_unit': i.materia_prima.measurement_unit
        }

def warehouses_by_inventory(request):
    id_ = request.GET.get('id')
    p,id = id_.split('-')
    warehouses = warehouse_service.list().filter(is_active=True).filter(lilis=True).exclude(inventario=id)
    return JsonResponse({'warehouses': [warehouse_to_dict(w) for w in warehouses]})

def get_stock_by_inventory(request):
    id_ = request.GET.get('id')
    p,id = id_.split('-')
    i = transaction_service.inventario.get(id=id)
    stock = i.stock_total
    return JsonResponse({'stock': stock})

def handle_transfer():
    c = requests.get(API_ENDPOINT).json()[0]
    data = {
        'clients': [c],
        'inventory': [],
    }
    inventarios = transaction_service.inventario.list().filter(stock_total__gt=0)
    for i in inventarios:
        data['inventory'].append(inventario_to_dict(i))
    return JsonResponse({'data': data})

def handle_produccion():
    lilis = requests.get(API_ENDPOINT).json()[0]
    data = {
        'clients': [lilis],
        'products': [],
        'warehouses': [],
    }
    products = product_service.list_actives()
    for p in products:
        data['products'].append(raw_material_to_dict(p))
    warehouses = warehouse_service.list().filter(lilis=True).filter(is_active=True)
    for w in warehouses:
        data['warehouses'].append(warehouse_to_dict(w))
    return JsonResponse({'data': data})


def get_raw_materials_by_supplier(request):
    id = request.GET.get('id')
    type = request.GET.get('type')
    if type == 'ingreso':
        p = []
        raw_materials = transaction_service.inventario.raw_class.objects.filter(supplier_id=id).filter(is_active=True)
        for rm in raw_materials:
            p.append({
                'id': rm.id,
                'name': rm.name,
                'sku': rm.sku,
                'measurement_unit': rm.measurement_unit,
            })
        return JsonResponse({'p': p})
    elif type == 'salida':
        p = []
        products = transaction_service.inventario.product_class.objects.all().filter(is_active=True)
        for pr in products:
            p.append({
                'id': pr.id,
                'sku': pr.sku,
                'name': pr.name,
                'measurement_unit': pr.measurement_unit,
            })
        return JsonResponse({'p': p})

def get_by_type(request):
    tipo = request.GET.get('type')
    match tipo:
        case 'ingreso':
            return handle_ingreso()
        case 'salida':
            return handle_salida()
        case 'devolucion':
            return handle_devolucion()
        case 'transferencia':
            return handle_transfer()
        case 'produccion':
            return handle_produccion()
        
class TransactionView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    allowed_per_page = [5, 25, 50, 100]
    default_per_page = 25
    allowed_sort_fields = ['date', 'type', 'client']

    def get(self, request, *args, **kwargs):
        q = (request.GET.get("q") or "").strip()
        sort_by = request.GET.get('sort_by', 'date')
        order = request.GET.get('order', 'desc')
        per_page = request.GET.get("per_page", self.default_per_page)
        if sort_by not in self.allowed_sort_fields:
            sort_by = 'date'
        if order not in ['asc', 'desc']:
            order = 'asc'
        if per_page not in self.allowed_per_page:
            per_page = self.default_per_page
        order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
        qs = transaction_service.list()
        if q:
            qs = qs.filter(
                Q(type__icontains=q)|
                Q(client__rut__startswith=q)|
                Q(client__bussiness_name__icontains=q)
            )
        qs = qs.order_by(order_by_field)
        paginator = Paginator(qs, per_page)
        page_number = request.GET.get("page")
        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        params_pagination = request.GET.copy()
        params_pagination.pop("page", None)
        querystring_pagination = params_pagination.urlencode()
        params_sorting = request.GET.copy()
        params_sorting.pop("page", None)
        params_sorting.pop("sort_by", None)
        params_sorting.pop("order", None)
        querystring_sorting = params_sorting.urlencode()
        products = transaction_service.inventario.product_class.objects.all().filter(is_active=True)
        raw_materials = transaction_service.inventario.raw_class.objects.all().filter(is_active=True)
        clients = client_service.list_actives()
        transactions = transaction_service.list()
        productos_unicos = len(products)
        stock = 0
        inventarios = transaction_service.inventario.list()
        for i in inventarios:
            stock += i.stock_total
        today = []
        for t in transactions:
            t.date = t.date.date()
            if t.date == date.today():
                today.append(t)
        transactions_today = len(today)
        return render(request,'transactions/transaction.html',{
            'products': products, 
            'raw_materials': raw_materials,
            'clients': clients, 
            'transactions': transactions, 
            'transactions_today': transactions_today,
            'stock': stock,
            'productos_unicos': productos_unicos,
            "page_obj": page_obj,  
            "q": q,
            "per_page": per_page,
            "total": qs.count(),
            "querystring": querystring_pagination, 
            "querystring_sorting": querystring_sorting,
            "current_sort_by": sort_by,
            "current_order": order,
            "order_next": "desc" if order == "asc" else "asc",
            })

    def post(self, request, *args, **kwargs):
        required_group =(
            'Acceso Completo',
            'Acceso limitado a Ventas',
            "Acceso limitado a Produccion",
        )
        user = request.user
        if not user.groups.filter(name__in=required_group).exists():
            return redirect('transaction_list')
        transaction_service.create_transaction(request)
        return redirect('transaction_list')
        
class TransactionExportView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        qs = transaction_service.list().order_by('date')
        limit = request.GET.get("limit")
        if q:
            qs = qs.filter(
                Q(type__icontains=q)|
                Q(client__rut__startswith=q)|
                Q(code__icontains=q)
            )
        if limit:
            try:
                limit = int(limit)
                qs = qs[:limit]
            except ValueError:
                pass
        data_rows = []
        for transaction in qs:
            if transaction.client:
                c = transaction.client.rut
            else:
                c = "Lilis"
            data_rows.append([
                transaction.type,
                c,
                transaction.code,
                transaction.date.strftime("%Y-%m-%d"),
                transaction.expiration_date.strftime("%Y-%m-%d") if transaction.expiration_date else "",
                transaction.notes,
            ])
        headers = ["Tipo", "Cliente", "Código", "Fecha", "Vencimiento", "Observaciones"]
        return generate_excel_response(headers, data_rows, "Lilis_Transacciones")

@login_required
@permission_or_redirect('Sells.change_transaction','dashboard', 'No teni permiso')
def transaction_update(request, id):
    original = transaction_service.model.objects.get(id=id)
    if request.method == 'POST':
        form = transaction_service.form_class(request.POST, base_transaction=original)
        if form.is_valid():
            form.save() 
            return redirect('transaction_list')
    else:
        form = transaction_service.form_class(base_transaction=original)
    return render(request, 'transactions/transaction_update.html', {'form': form})

def product_batch_list(request):
    q = (request.GET.get("q") or "").strip()
    default_per_page = 25
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    if per_page > 101 or per_page <= 0:
        per_page = default_per_page
    allowed_sort_fields = ['inventario__producto__name', 'inventario__producto__category__name', 'inventario__producto__sku']
    sort_by = request.GET.get('sort_by', 'inventario__producto__name')
    order = request.GET.get('order', 'asc')

    if sort_by not in allowed_sort_fields:
        sort_by = 'inventario__producto__name'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    qs = transaction_service.inventario.lote.objects.all().filter(inventario__producto__is_active=True)

    if q:
        qs = qs.filter(
            Q(inventario__producto__name__icontains=q) |
            Q(inventario__producto__description__icontains=q)|
            Q(inventario__producto__sku__icontains=q)
        )
        
    qs = qs.order_by(order_by_field)

    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page")

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    params_pagination = request.GET.copy()
    params_pagination.pop("page", None)
    querystring_pagination = params_pagination.urlencode()

    params_sorting = request.GET.copy()
    params_sorting.pop("page", None)
    params_sorting.pop("sort_by", None)
    params_sorting.pop("order", None)
    querystring_sorting = params_sorting.urlencode()

    context = {
        "page_obj": page_obj,  
        "q": q,
        "per_page": per_page,
        "total": qs.count(),
        
        "querystring": querystring_pagination, 
        
        "querystring_sorting": querystring_sorting,
        "current_sort_by": sort_by,
        "current_order": order,
        "order_next": "desc" if order == "asc" else "asc",
    }
    return render(request, 'batches/product_batch_list.html', context)

def product_batch_create(request):
    l = client_service.search_by_rut(LILIS_RUT)[0]
    warehouses = get_warehouses_for_client(l)
    products = product_service.list_actives()
    if request.method == 'POST':
        print(request.POST)
        success, obj = transaction_service.inventario.agregar_lote_producto(request.POST)

        if success:
            return redirect('product_batch_list')
        context = {
            'warehouses': warehouses,
            'products': products,
        }

        if isinstance(obj, str):
            context['error_message'] = obj
            context['form'] = transaction_service.inventario.lote_form_class(request.POST)  
        else:
            context['form'] = obj

        return render(request, 'batches/product_batch_create.html', context)

    return render(request, 'batches/product_batch_create.html', {
        'form': transaction_service.inventario.lote_form_class(),
        'warehouses': warehouses,
        'products': products,
    })

def transaction_search(request):
    q = (request.GET.get("q") or "").strip()
    filtros = Q(client__fantasy_name__icontains=q) | \
              Q(client__bussiness_name__icontains=q) | \
              Q(client__rut__icontains=q) | \
              Q(type__icontains=q) | \
              Q(code__icontains=q) | \
              Q(details__batch__inventario__producto__sku__icontains=q) | \
              Q(details__batch__inventario__producto__name__icontains=q) | \
              Q(details__batch__inventario__material__sku__icontains=q) | \
              Q(details__batch__inventario__material__name__icontains=q) | \
              Q(details__serie__inventario__producto__sku__icontains=q) | \
              Q(details__serie__inventario__producto__name__icontains=q) | \
              Q(details__serie__inventario__material__sku__icontains=q) | \
              Q(details__serie__inventario__material__name__icontains=q)
    
    qs_ids = transaction_service.model.objects.filter(filtros).values_list('id', flat=True).distinct()
    
    transactions = transaction_service.model.objects.filter(id__in=qs_ids)
    data = []
    for t in transactions:
        data.append({
            'id': t.id,
            'fecha': t.date.strftime("%Y-%m-%d") if hasattr(t, 'date') else 'N/A',
            'tipo': t.type,
            'codigo': t.code,
            'cliente': t.client.fantasy_name,
            'producto_info': obtener_info_producto_material(t),
        })
        
    return JsonResponse({'data': data}, safe=False)

def post_process_transaction_results(qs_values):
    resultados_finales = {}
    
    for row in qs_values:
        t_id = row['id']
        
        if t_id not in resultados_finales:
            resultados_finales[t_id] = {
                'id': t_id,
                'type': row.get('type'),
                'code': row.get('code'),
                'client': row.get('client__fantasy_name') or row.get('client__bussiness_name'),
                'producto': '',
                'vencimiento': 'N/A',
                'stock': 'N/A',
            }
        
        prod_sku = row.get('details__batch__inventario__producto__sku')
        if prod_sku and not resultados_finales[t_id]['producto']:
            resultados_finales[t_id]['producto'] = row.get('details__batch__inventario__producto__name')
        
        mat_sku = row.get('details__batch__inventario__materia_prima__sku')
        if mat_sku and not resultados_finales[t_id]['producto']:
            resultados_finales[t_id]['producto'] = row.get('details__batch__inventario__materia_prima__name')
            
        prod_sku = row.get('details__serie__inventario__producto__sku')
        if prod_sku and not resultados_finales[t_id]['producto']:
            resultados_finales[t_id]['producto'] = row.get('details__serie__inventario__producto__name')
        
        mat_sku = row.get('details__serie__inventario__materia_prima__sku')
        if mat_sku and not resultados_finales[t_id]['producto']:
            resultados_finales[t_id]['producto'] = row.get('details__serie__inventario__materia_prima__name')
        
    return list(resultados_finales.values())


def obtener_info_producto_material(t):
    item = None
    details = transaction_service.transaction_detail.objects.filter(transaction=t).select_related('batch', 'serie').first()
    if details:
        if details.batch:
            item = details.batch.inventario
        if details.serie:
            item = details.serie.inventario
    else:
        return None
    if item:
        try:
            return item.producto.sku
        except:
            return item.materia_prima.sku
    return None

def transaction_search(request):
    q = (request.GET.get("q") or "").strip()
    qs = transaction_service.model.objects.filter(
        Q(client__fantasy_name__icontains=q) |
        Q(client__bussiness_name__icontains=q) |
        Q(client__rut__icontains=q)|
        Q(type__icontains=q)|
        Q(code__icontains=q)|
        Q(details__batch__inventario__producto__sku__icontains=q)|
        Q(details__batch__inventario__producto__name__icontains=q)|
        Q(details__batch__inventario__materia_prima__sku__icontains=q)|
        Q(details__batch__inventario__materia_prima__name__icontains=q)|
        Q(details__serie__inventario__producto__sku__icontains=q)|
        Q(details__serie__inventario__producto__name__icontains=q)|
        Q(details__serie__inventario__materia_prima__sku__icontains=q)|
        Q(details__serie__inventario__materia_prima__name__icontains=q)
    ).order_by('-date').distinct()
    data = []
    for t in qs:
        if t in data:
            continue
        try:
            rut = t.client.rut
        except:
            rut = "Lilis"
        data.append({
            'id': t.id,
            'fecha': t.date.strftime("%Y-%m-%d") if hasattr(t, 'date') else 'N/A',
            'tipo': t.type,
            'codigo': t.code,
            'cliente': rut,
            'sku': obtener_info_producto_material(t),
            'bodega': t.warehouse.name,
            'cantidad' : t.quantity,
            'vencimiento': t.expiration_date
        })
    return JsonResponse({'data': data}, safe=False)

def transaction_all(request):
    data = []
    transactions = transaction_service.list().order_by('-date')
    for t in transactions:
        try:
            rut = t.client.rut
        except:
            rut = "Lilis"
        data.append({
            'id': t.id,
            'fecha': t.date.strftime("%Y-%m-%d") if hasattr(t, 'date') else 'N/A',
            'tipo': t.type,
            'codigo': t.code,
            'cliente': rut,
            'sku': obtener_info_producto_material(t),
            'bodega': t.warehouse.name,
            'cantidad' : t.quantity,
            'vencimiento': t.expiration_date
        })
    return JsonResponse({'data': data}, safe=False)