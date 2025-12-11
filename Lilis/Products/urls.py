from django.urls import path
from . import views


categorys = [
    path('category_list/', views.CategoryListView.as_view(), name='category_list'),
    path('category_create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category_update/<int:pk>/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('category_delete/<int:pk>/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('export_categories_excel/', views.CategoryExportView.as_view(), name='export_categories_excel'),
]
    
products = [
    path('products_list/' , views.ProductListView.as_view() ,name='products_list'),
    path('product_view/<int:pk>/', views.ProductView.as_view(), name='product_view'),
    path('product_create/' , views.ProductCreateView.as_view() ,name='product_create'),
    path('product_delete/<int:pk>/' , views.ProductDeleteView.as_view() ,name='product_delete'),
    path('product_update/<int:pk>/' , views.ProductUpdateView.as_view() ,name='product_update'),
    path('export_product_excel/', views.ProductExportView.as_view(), name='export_product_excel'),
    path('product_search/', views.product_search, name='product_search'),
    path('product_all/', views.product_all, name='product_all'),
]

suppliers = [
    path('supplier_list/', views.SupplierListView.as_view(), name='supplier_list'),
    path('supplier_view/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_view'),
    path('supplier_create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('supplier_update/<int:pk>/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('supplier_delete/<int:pk>/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    path('export_suppliers_excel/', views.SupplierExportView.as_view(), name='export_suppliers_excel'),
    path('supplier_search/', views.SupplierSearchView.as_view(), name='supplier_search'),
]

raw_materials = [
    path('raw_material_list/', views.RawMaterialListView.as_view(), name='raw_material_list'),
    path('raw_material_view/<int:pk>/', views.RawMaterialView.as_view(), name='raw_material_view'),
    path('raw_material_create/', views.RawMaterialCreateView.as_view(), name='raw_material_create'),
    path('raw_material_update/<int:pk>/', views.RawMaterialUpdateView.as_view(), name='raw_material_update'),
    path('raw_material_delete/<int:pk>/', views.RawMaterialDeleteView.as_view(), name='raw_material_delete'),
    path('export_raw_materials_excel/', views.RawMaterialExportView.as_view(), name='export_raw_materials_excel'),
    path('raw_material_search/', views.RawMaterialSearchView.as_view(), name='raw_material_search'),
]

inventory = [
    path('inventory_list/', views.InventoryListView.as_view(), name='inventory_list'),
]

urlpatterns = [
    *products,
    *raw_materials,
    *suppliers,
    *categorys,
    *inventory,
]