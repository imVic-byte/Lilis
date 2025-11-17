from django.urls import path
from . import views

clients = [
    # Esta es la vista principal que usaremos, con paginación
    path('client_list_all/', views.client_list_all, name='client_list_all'),
    
    # Comentamos estas líneas para que no den error
    # path('client_list_actives', views.client_list_actives, name='client_list_actives'),
    # path('client_list_inactives', views.client_list_inactives, name='client_list_inactives'),
    
    # El resto de tus vistas de cliente
    path('client_create/', views.client_create, name='client_create'),
    path('client_update/<int:id>/', views.client_update, name='client_update'),
    path('client_delete/<int:id>/', views.client_delete, name='client_delete'),
    path('client_view/<int:id>/', views.client_view, name='client_view'),
    path('export_clients_excel/', views.export_clients_excel, name='export_clients_excel'),
    path('client_search/', views.client_search, name='client_search'),
]

locations = [
    path('location_list/', views.location_list, name='location_list'),
    path('location_create/', views.location_create, name='location_create'),
    path('location_update/<int:id>/', views.location_update, name='location_update'),
    path('location_delete/<int:id>/', views.location_delete, name='location_delete'),
    path('location_view/<int:id>/', views.location_view, name='location_view'),
    path('export_locations_excel/', views.export_locations_excel, name='export_locations_excel'),
]

warehouses = [
    path('warehouse_list/', views.warehouse_list, name='warehouse_list'),
    path('warehouse_create/', views.warehouse_create, name='warehouse_create'),
    path('warehouse_update/<int:id>/', views.warehouse_update, name='warehouse_update'),
    path('warehouse_delete/<int:id>/', views.warehouse_delete, name='warehouse_delete'),
    path('warehouse_view/<int:id>/', views.warehouse_view, name='warehouse_view'),
    path('export_warehouse_excel/', views.export_warehouse_excel, name='export_warehouse_excel'),
    path('warehouses_by_client/', views.get_warehouses, name='warehouses_by_client'),
]

urlpatterns = [
    *clients,
    *locations,
    *warehouses,
    path('transaction_list/', views.transaction, name='transaction_list'),
    path('export_transaction_excel/', views.export_transaction_excel, name='export_transaction_excel'),
    path('get_stock_by_product/', views.get_stock_by_product, name='get_stock_by_product'),
    path('validate_code/', views.validate_code, name='validate_code'),
    path('get_by_type/', views.get_by_type, name='get_by_type'),
]