from django.shortcuts import redirect
from .services import CategoryService, ProductService, SupplierService, RawMaterialService
from django.contrib.auth.decorators import login_required
from Main.decorator import permission_or_redirect
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect 
from Main.utils import generate_excel_response
from Sells.services import InventarioService
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from Main.mixins import GroupRequiredMixin, StaffRequiredMixin
from datetime import date, timedelta
from django.template.defaultfilters import truncatechars

inventory_service = InventarioService()
category_service = CategoryService()
product_service = ProductService()
supplier_service = SupplierService()
raw_material_service = RawMaterialService()

class CategoryListView(GroupRequiredMixin, ListView):
    model = category_service.model
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    paginate_by = 25
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        'Acceso limitado a Produccion',
        'Acceso limitado a Finanzas'
    )

    def get_queryset(self):
        qs = super().get_queryset()
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
            )
        allowed_sort_fields = ['name', 'description']
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

class CategoryCreateView(GroupRequiredMixin, CreateView):
    model = category_service.model
    form_class = category_service.form_class
    success_url = reverse_lazy('category_list')
    template_name = 'products/category_create.html'
    required_group =('Acceso Completo', 'Acceso limitado a Compras', 'Acceso limitado a Inventario')

class CategoryUpdateView(GroupRequiredMixin, UpdateView):
    model = category_service.model
    form_class = category_service.form_class
    success_url = reverse_lazy('category_list')
    template_name = 'products/category_update.html'
    required_group =('Acceso Completo', 'Acceso limitado a Compras', 'Acceso limitado a Inventario', 'Acceso limitado a Produccion')

class CategoryDeleteView(GroupRequiredMixin, DeleteView):
    model = category_service.model
    success_url = reverse_lazy('category_list')
    required_group =('Acceso Completo', 'Acceso limitado a Compras', 'Acceso limitado a Inventario')

    def get(self, request, *args, **kwargs):
        return HttpResponse('Metodo no permitido')
    
    def form_valid(self, form):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
        
class CategoryExportView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        'Acceso limitado a Produccion',
        'Acceso limitado a Finanzas'
    )
    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        qs = category_service.list().order_by('name')
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            )

        qs_limit = request.GET.get("limit")
        if qs_limit:
            try:
                limit = int(qs_limit)
                if limit > 0:
                    qs = qs[:limit] 
            except ValueError:
                pass

        headers = ["Nombre", "Descripción"]
        data_rows = []

        for c in qs:
            data_rows.append([
                c.name,
                c.description
            ])

        return generate_excel_response(headers, data_rows, "Lilis_Categorias")

class ProductListView(GroupRequiredMixin, ListView):
    model = product_service.model
    template_name = 'products/products_list.html'
    context_object_name = 'products'
    paginate_by = 25
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        'Acceso limitado a Produccion',
        'Acceso limitado a Finanzas'
    )

    def get_queryset(self):
        qs = super().get_queryset().filter(is_active=True)
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
            )
        allowed_sort_fields = ['name', 'category__name', 'sku']
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
        
def product_search(request):
    q = request.GET.get('q', '')
    data = []
    products = product_service.model.objects.filter( is_active=True ).filter(
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    for p in products:
        data.append({
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'deficit': p.deficit,
            'description': p.description,
            'category': p.category.name,
            'is_perishable': p.is_perishable,
            'is_active': p.is_active,
            'batch_control': p.batch_control,
            'serie_control':p.serie_control,
            'ean_upc':p.ean_upc,
            'model':p.model,
            'brand':p.brand,
            'price':p.price,
            'iva':p.iva,
            'min_stock':p.min_stock,
        })
    return JsonResponse({'data':data}, safe=False)

def product_all(request):
    products = product_service.model.objects.filter(is_active=True)
    data = []
    for p in products:
        data.append({
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'deficit': p.deficit,
            'description': p.description,
            'category': p.category.name,
            'is_perishable': p.is_perishable,
            'is_active': p.is_active,
            'batch_control': p.batch_control,
            'serie_control':p.serie_control,
            'ean_upc':p.ean_upc,
            'model':p.model,
            'brand':p.brand,
            'price':p.price,
            'iva':p.iva,
            'min_stock':p.min_stock,
        })
    return JsonResponse({'data':data}, safe=False)

class ProductView(GroupRequiredMixin, DetailView):
    model = product_service.model
    template_name = 'products/product.html'
    context_object_name = 'p'
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        'Acceso limitado a Produccion',
        'Acceso limitado a Finanzas'
    )
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.batch_control:
            inventory_items = inventory_service.model.objects.filter(
                producto=self.object
            ).prefetch_related('lotes')
            context['inventory'] = inventory_items 
            context['control'] = 'lotes'
        else:
            inventory_items = inventory_service.model.objects.filter(
                producto=self.object
            ).prefetch_related('series')
            context['inventory'] = inventory_items 
            context['control'] = 'series'
        return context

class ProductCreateView(GroupRequiredMixin, CreateView):
    model = product_service.model
    form_class = product_service.form_class
    success_url = reverse_lazy('products_list')
    template_name = 'products/product_create.html'
    required_group =('Acceso Completo', 'Acceso limitado a Compras', 'Acceso limitado a Inventario')

class ProductUpdateView(GroupRequiredMixin, UpdateView):
    model = product_service.model
    form_class = product_service.form_class
    success_url = reverse_lazy('products_list')
    template_name = 'products/product_update.html'
    required_group =('Acceso Completo', 'Acceso limitado a Compras', 'Acceso limitado a Inventario', "Acceso limitado a Produccion")

class ProductDeleteView(GroupRequiredMixin, DeleteView):
    model = product_service.model    
    success_url = reverse_lazy('products_list')
    required_group =('Acceso Completo', 'Acceso limitado a Compras', 'Acceso limitado a Inventario')
    
    def get(self, request, *args, **kwargs):
        return HttpResponse('Metodo no permitido')
    
    def form_valid(self, form):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
    
class ProductSearchView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    def get(self, *args, **kwargs):
        q = self.request.GET.get('q', '')
        products = product_service.model.objects.filter(is_active=True).filter(
            Q(name__icontains=q)
        ).values('id', 'name', 'description', 'category__name', 'is_perishable')    
        return JsonResponse(list(products), safe=False)

class ProductExportView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        qs = product_service.list().filter(is_active=True).select_related("category").order_by('name')
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q) |
                Q(category__name__icontains=q)
            )
        
        qs_limit = request.GET.get("limit")
        if qs_limit:
            try:
                limit = int(qs_limit)
                if limit > 0:
                    qs = qs[:limit] 
            except ValueError:
                pass 

        headers = [
            "Nombre",
            "SKU",
            "Deficit",
            "Categoría",
            "Control por lote",
            "Control por serie",
            "Perecible",
        ]
        data_rows = []
        
        for p in qs:
            is_perishable_str = "Sí" if p.is_perishable else "No"
            data_rows.append([
                p.name,
                p.sku,
                p.deficit,
                p.category.name,
                p.batch_control,
                p.serie_control,
                is_perishable_str,
            ])

        return generate_excel_response(headers, data_rows, "Lilis_Productos")

def supplier_search(request):
    q = request.GET.get('q', '')
    suppliers = supplier_service.model.objects.filter( is_active=True ).filter(
        Q(bussiness_name__icontains=q) |
        Q(fantasy_name__icontains=q) |
        Q(rut__icontains=q)
    )
    data = []
    for s in suppliers:
        if s.trade_terms:
            trade_terms = truncatechars(s.trade_terms, 10)
        else:
            trade_terms = '—'
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
    return JsonResponse({'data':data}, safe=False)

def supplier_all(request):
    suppliers = supplier_service.model.objects.filter(is_active=True)
    data = []
    for s in suppliers:
        if s.trade_terms:
            trade_terms = truncatechars(s.trade_terms, 10)
        else:
            trade_terms = '—'
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
    return JsonResponse({'data':data}, safe=False)

class SupplierDetailView(GroupRequiredMixin, DetailView):
    model = supplier_service.model
    template_name = 'suppliers/supplier_view.html'
    context_object_name = 'p'
    pk_url_kwarg = 'pk'
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.object
        raw_materials = raw_material_service.list().filter(supplier=supplier)
        context['raw_materials'] = raw_materials
        return context
        

class SupplierListView(GroupRequiredMixin, ListView):
    model = supplier_service.model
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 25
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )

    def get_queryset(self):
        qs = super().get_queryset().filter(is_active=True)
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(fantasy_name__icontains=q) |
                Q(bussiness_name__icontains=q) |
                Q(rut__icontains=q) |
                Q(email__icontains=q) |
                Q(phone__icontains=q) |
                Q(trade_terms__icontains=q)
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

class SupplierCreateView(GroupRequiredMixin, CreateView):
    model = supplier_service.model
    form_class = supplier_service.form_class
    success_url = reverse_lazy('supplier_list')
    template_name = 'suppliers/supplier_create.html'
    required_group =('Acceso Completo', 'Acceso limitado a Compras', 'Acceso limitado a Inventario')

class SupplierUpdateView(GroupRequiredMixin, UpdateView):
    model = supplier_service.model
    form_class = supplier_service.form_class
    success_url = reverse_lazy('supplier_list')
    template_name = 'suppliers/supplier_update.html'
    required_group =('Acceso Completo', 'Acceso limitado a Compras', 'Acceso limitado a Inventario', "Acceso limitado a Produccion")

class SupplierDeleteView(GroupRequiredMixin, DeleteView):
    model = supplier_service.model
    success_url = reverse_lazy('supplier_list')
    required_group =('Acceso Completo', 'Acceso limitado a Compras', 'Acceso limitado a Inventario')

    def get(self, request, *args, **kwargs):
        return HttpResponse('Metodo no permitido')
    
    def form_valid(self, form):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
    
class SupplierExportView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        qs = supplier_service.list().order_by('fantasy_name')
        if q:
            qs = qs.filter(
                Q(fantasy_name__icontains=q) |
                Q(bussiness_name__icontains=q) |
                Q(rut__icontains=q) |
                Q(email__icontains=q) |
                Q(phone__icontains=q) |
                Q(trade_terms__icontains=q)
            )
        qs_limit = request.GET.get("limit")
        if qs_limit:
            try:
                limit = int(qs_limit)
                if limit > 0:
                    qs = qs[:limit] 
            except ValueError:
                pass
        headers = ["Nombre Fantasía", "Razón Social", "RUT", "Email", "Teléfono", "Términos"]
        data_rows = []
        for s in qs:
            data_rows.append([
                s.fantasy_name,
                s.bussiness_name,
                s.rut,
                s.email,
                s.phone,
                s.trade_terms
            ])
        return generate_excel_response(headers, data_rows, "Lilis_Proveedores")

class RawMaterialListView(GroupRequiredMixin, ListView):
    model = raw_material_service.model
    template_name = 'raw_material/raw_material_list.html'
    context_object_name = 'raw_materials'
    paginate_by = 25
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )

    def get_queryset(self):
        qs = super().get_queryset().filter(is_active=True)
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            )
        allowed_sort_fields = ['name', 'supplier__fantasy_name']
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

def raw_material_search(request):
    q = request.GET.get('q', '')
    data = []
    raw_materials = raw_material_service.model.objects.filter( is_active=True ).filter(
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    for rm in raw_materials:
        data.append({
            'id': rm.id,
            'sku': rm.sku,
            'name': rm.name,
            'description': rm.description,
            'category': rm.category.name,
            'is_perishable': rm.is_perishable,
            'is_active': rm.is_active,
            'batch_control': rm.batch_control,
            'serie_control':rm.serie_control,
            'ean_upc':rm.ean_upc,
            'model':rm.model,
            'brand':rm.brand,
            'price':rm.price,
            'iva':rm.iva,
            'min_stock':rm.min_stock,
        })
    return JsonResponse({'data':data}, safe=False)

def raw_material_all(request):
    raw_materials = raw_material_service.model.objects.filter(is_active=True)
    data = []
    for rm in raw_materials:
        data.append({
            'id': rm.id,
            'sku': rm.sku,
            'name': rm.name,
            'description': rm.description,
            'category': rm.category.name,
            'is_perishable': rm.is_perishable,
            'is_active': rm.is_active,
            'batch_control': rm.batch_control,
            'serie_control':rm.serie_control,
            'ean_upc':rm.ean_upc,
            'model':rm.model,
            'brand':rm.brand,
            'price':rm.price,
            'iva':rm.iva,
            'min_stock':rm.min_stock,
        })
    return JsonResponse({'data':data}, safe=False)

class RawMaterialView(GroupRequiredMixin, DetailView):
    model = raw_material_service.model
    template_name = 'raw_material/raw_material_view.html'
    context_object_name = 'p'
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.batch_control:
            inventory_items = inventory_service.model.objects.filter(
                materia_prima=self.object
            ).prefetch_related('lotes')
            context['inventory'] = inventory_items 
            context['control'] = 'lotes'
        else:
            inventory_items = inventory_service.model.objects.filter(
                materia_prima=self.object
            ).prefetch_related('series')
            context['inventory'] = inventory_items 
            context['control'] = 'series'
        return context

class RawMaterialCreateView(GroupRequiredMixin, CreateView):
    model = raw_material_service.model
    form_class = raw_material_service.form_class
    success_url = reverse_lazy('raw_material_list')
    template_name = 'raw_material/raw_material_create.html'
    required_group =('Acceso Completo', 'Acceso limitado a Compras', 'Acceso limitado a Inventario')

    def get_supplier_object(self):
        supplier_id = self.request.GET.get('supplier')
        if supplier_id:
            return supplier_service.model.objects.get(id=supplier_id)
        else:
            return None
    
    def get_inicial(self):
        initial = super().get_initial()
        supplier = self.get_supplier_object()
        if supplier:
            initial['supplier'] = supplier
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        supplier = self.get_supplier_object()
        if supplier:
            kwargs['supplier'] = supplier
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        supplier = self.get_supplier_object()
        next_url = self.request.GET.get('next')
        if supplier and next_url:
            return redirect(next_url)
        return response
    
class RawMaterialUpdateView(GroupRequiredMixin, UpdateView):
    model = raw_material_service.model
    form_class = raw_material_service.form_class
    success_url = reverse_lazy('raw_material_list')
    template_name = 'raw_material/raw_material_update.html'
    required_group =('Acceso Completo', 'Acceso limitado a Compras', 'Acceso limitado a Inventario', "Acceso limitado a Produccion")

    def get_supplier_object(self):
        supplier_id = self.request.POST.get('supplier')
        if supplier_id:
            return supplier_service.model.objects.get(id=supplier_id)
        else:
            return None
    
    def get_inicial(self):
        initial = super().get_initial()
        supplier = self.get_supplier_object()
        if supplier:
            initial['supplier'] = supplier
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        supplier = self.get_supplier_object()
        if supplier:
            kwargs['supplier'] = supplier
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        supplier = self.get_supplier_object()
        next_url = self.request.GET.get('next')
        if supplier and next_url:
            return redirect(next_url)
        return response

class RawMaterialDeleteView(GroupRequiredMixin, DeleteView):
    model = raw_material_service.model
    success_url = reverse_lazy('raw_material_list')
    required_group =('Acceso Completo', 'Acceso limitado a Compras', 'Acceso limitado a Inventario')

    def get(self, request, *args, **kwargs):
        return HttpResponse('Metodo no permitido')
    
    def form_valid(self, form):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
    
class RawMaterialExportView(GroupRequiredMixin, View):
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )
    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        qs = raw_material_service.list_actives().select_related(
            "supplier", 
            "category"
        ).order_by('name')

        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(supplier__fantasy_name__icontains=q) |
                Q(category__name__icontains=q)
            )
        
        qs_limit = request.GET.get("limit")
        if qs_limit:
            try:
                limit = int(qs_limit)
                if limit > 0:
                    qs = qs[:limit] 
            except ValueError:
                pass 

        headers = ["Nombre", "Proveedor", "Categoría", "Perecible", 'Unidad de medida']
        data_rows = []
        
        for rm in qs:
            data_rows.append([
                rm.name,
                rm.supplier.fantasy_name,
                rm.category.name,
                "Sí" if rm.is_perishable else "No",
                rm.measurement_unit,
            ])
        return generate_excel_response(headers, data_rows, "Lilis_Materias_Primas")

class InventoryListView(GroupRequiredMixin, ListView):
    model = inventory_service.model
    template_name = 'inventory/inventory_list.html'
    context_object_name = 'inventory'
    paginate_by = 25
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Compras',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas"
    )

    def get_queryset(self):
        qs = super().get_queryset()
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(materia_prima__name__icontains=q) |
                Q(materia_prima__sku__icontains=q) |
                Q(producto__name__icontains=q) |
                Q(producto__sku__icontains=q)
            )
        allowed_sort_fields = ['materia_prima__name','materia_prima__sku', 'producto__name', 'producto__sku', 'stock_total']
        sort_by = self.request.GET.get('sort_by', 'stock_total')
        order = self.request.GET.get('order', 'desc')
        if sort_by not in allowed_sort_fields:
            sort_by = 'stock_total'
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
        sort_by = self.request.GET.get('sort_by', 'stock_total')
        order = self.request.GET.get('order', 'desc')
        per_page = context['paginator'].per_page
        alerta_vencimiento = date.today() + timedelta(days=10)
        context.update({
            "q": q,
            "current_sort_by": sort_by,
            "current_order": order,
            "order_next": "desc" if order == "asc" else "asc",
            "per_page": per_page,
            "alerta_vencimiento": alerta_vencimiento,
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

def editar_inventario(request):
    inventario = inventory_service.model.objects.get(pk=request.GET.get('id'))
    stock = request.GET.get('stock')
    inventory_service.editar_stock(inventario, stock)
    return redirect('inventory_list')