from django.urls import path
from . import views

clients = [
    path('client_list_all/', views.ClientListView.as_view(), name='client_list_all'),
    path('client_create/', views.ClientCreateView.as_view(), name='client_create'),
    path('client_update/<int:pk>/', views.ClientUpdateView.as_view(), name='client_update'),
    path('client_delete/<int:pk>/', views.ClientDeleteView.as_view(), name='client_delete'),
    path('client_view/<int:pk>/', views.ClientDetailView.as_view(), name='client_view'),
    path('export_clients_excel/', views.ClientExportView.as_view(), name='export_clients_excel'),
    path('client_search/', views.ClientSearchView.as_view(), name='client_search'),
]


warehouses = [
    path('warehouse_list/', views.WarehouseListView.as_view(), name='warehouse_list'),
    path('warehouse_create/', views.WarehouseCreateView.as_view(), name='warehouse_create'),
    path('warehouse_update/<int:pk>/', views.WarehouseUpdateView.as_view(), name='warehouse_update'),
    path('warehouse_delete/<int:pk>/', views.WarehouseDeleteView.as_view(), name='warehouse_delete'),
    path('warehouse_view/<int:pk>/', views.WarehouseDetailView.as_view(), name='warehouse_view'),
    path('export_warehouse_excel/', views.WarehouseExportView.as_view(), name='export_warehouse_excel'),
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