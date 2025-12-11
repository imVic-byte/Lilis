from django.urls import path
from . import views

clients = [
    path('client_list_all/', views.ClientListView.as_view(), name='client_list_all'),
    path('client_create/', views.ClientCreateView.as_view(), name='client_create'),
    path('client_update/<int:pk>/', views.ClientUpdateView.as_view(), name='client_update'),
    path('client_delete/<int:pk>/', views.ClientDeleteView.as_view(), name='client_delete'),
    path('client_view/<int:pk>/', views.ClientDetailView.as_view(), name='client_view'),
    path('export_clients_excel/', views.ClientExportView.as_view(), name='export_clients_excel'),
    path('client_search/', views.client_search, name='client_search'),
    path('client_all/', views.client_all, name='client_all'),
]


warehouses = [
    path('warehouse_list/', views.WarehouseListView.as_view(), name='warehouse_list'),
    path('warehouse_create/', views.WarehouseCreateView.as_view(), name='warehouse_create'),
    path('warehouse_update/<int:pk>/', views.WarehouseUpdateView.as_view(), name='warehouse_update'),
    path('warehouse_delete/<int:pk>/', views.WarehouseDeleteView.as_view(), name='warehouse_delete'),
    path('warehouse_view/<int:pk>/', views.WarehouseDetailView.as_view(), name='warehouse_view'),
    path('export_warehouse_excel/', views.WarehouseExportView.as_view(), name='export_warehouse_excel'),
    path('warehouse_unnasign/', views.WarehouseUnassignView.as_view(), name='warehouse_unnasign'),
    path('warehouse_list_without_this_client/', views.WarehouseListWithoutThisClientView.as_view(), name='warehouse_list_without_this_client'),
    path('warehouse_assign/', views.WarehouseAssignView.as_view(), name='warehouse_assign'),
]

batches = [
    path('product_batch_list/', views.product_batch_list, name='product_batch_list'),
    path('product_batch_create/', views.product_batch_create, name='product_batch_create'),
]
urlpatterns = [
    *clients,
    *warehouses,
    *batches,
    path('transaction_list/', views.TransactionView.as_view(), name='transaction_list'),
    path('transaction_update/<int:id>/', views.transaction_update, name='transaction_update'),
    path('export_transaction_excel/', views.TransactionExportView.as_view(), name='export_transaction_excel'),
    path('get_stock_by_product/', views.get_stock_by_product, name='get_stock_by_product'),
    path('get_by_type/', views.get_by_type, name='get_by_type'),
    path('get_raw_materials_by_supplier/', views.get_raw_materials_by_supplier, name='get_raw_materials_by_supplier'),
    path('warehouses_by_client/', views.warehouses_by_client, name='warehouses_by_client'),
    path('warehouses_by_inventory/', views.warehouses_by_inventory, name='warehouses_by_inventory'),
    path('get_stock_by_inventory/', views.get_stock_by_inventory, name='get_stock_by_inventory'),
    path('transaction_search/', views.transaction_search, name='transaction_search'),
    path('transaction_all/', views.transaction_all, name='transaction_all'),
]