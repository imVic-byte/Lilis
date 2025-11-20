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


warehouses = [
    path('warehouse_list/', views.warehouse_list, name='warehouse_list'),
    path('warehouse_create/', views.warehouse_create, name='warehouse_create'),
    path('warehouse_update/<int:id>/', views.warehouse_update, name='warehouse_update'),
    path('warehouse_delete/<int:id>/', views.warehouse_delete, name='warehouse_delete'),
    path('warehouse_view/<int:id>/', views.warehouse_view, name='warehouse_view'),
    path('export_warehouse_excel/', views.export_warehouse_excel, name='export_warehouse_excel'),
    path('warehouses_by_client/', views.get_warehouses, name='warehouses_by_client'),
]

batches = [
    path('product_batch_list/', views.product_batch_list, name='product_batch_list'),
    path('product_batch_create/', views.product_batch_create, name='product_batch_create'),
]
urlpatterns = [
    *clients,
    *warehouses,
    *batches,
    path('transaction_list/', views.transaction, name='transaction_list'),
    path('transaction_update/<int:id>/', views.transaction_update, name='transaction_update'),
    path('export_transaction_excel/', views.export_transaction_excel, name='export_transaction_excel'),
    path('get_stock_by_product/', views.get_stock_by_product, name='get_stock_by_product'),
    path('validate_code/', views.validate_code, name='validate_code'),
    path('get_by_type/', views.get_by_type, name='get_by_type'),
    path('get_raw_materials_by_supplier/', views.get_raw_materials_by_supplier, name='get_raw_materials_by_supplier'),

]