from django.shortcuts import render
from Accounts.services import UserService
from Products.services import SupplierService, ProductService
from Sells.services import ClientService, TransactionService
from .mixins import GroupRequiredMixin
from django.views import View

user_service = UserService()
supplier_service = SupplierService()
product_service = ProductService()
client_service = ClientService()
transaction_service = TransactionService()


class DashboardView(GroupRequiredMixin, View):
    template_name = 'main/dashboard.html'
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas",
        "Acceso limitado a Compras"
    )
    
    def get(self, request):
        usuarios = user_service.count()
        proveedores_activos = supplier_service.count_actives()
        proveedores = supplier_service.count()
        productos = product_service.count()
        clientes_activos = client_service.count_actives()
        clientes= client_service.count()
        transacciones = transaction_service.list().order_by('-date')[:5]
        return render(request, 'main/dashboard.html',
                  {
                      'productos': productos,
                      'proveedores_activos': proveedores_activos,
                      'proveedores': proveedores,
                      'usuarios': usuarios,
                      'clientes_activos': clientes_activos,
                      'clientes': clientes,
                      'transacciones': transacciones
                  })

