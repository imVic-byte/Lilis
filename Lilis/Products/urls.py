from django.urls import path
from . import views


categorys = [
    path('category_list/', views.category_list, name='category_list'),
    path('category_create/', views.category_create, name='category_create'),
    path('category_update/<int:id>/', views.category_update, name='category_update'),
    path('category_delete/<int:id>/', views.category_delete, name='category_delete'),
    path('export_categories_excel/', views.export_categories_excel, name='export_categories_excel'),
]
    
products = [
    path('products_list/' , views.products_list ,name='products_list'),
    path('product_view/<int:id>/', views.product_view, name='product_view'),
    path('product_create/' , views.product_create ,name='product_create'),
    path('product_delete/<int:id>/' , views.product_delete ,name='product_delete'),
    path('product_update/<int:id>/' , views.product_update ,name='product_update'),
    path('export_product_excel/', views.export_product_excel, name='export_product_excel'),
    path('product_search/', views.product_search, name='product_search'),
]

suppliers = [
    path('supplier_list/', views.supplier_list, name='supplier_list'),
    path('supplier_view/<int:id>/', views.supplier_view, name='supplier_view'),
    path('supplier_create/', views.supplier_create, name='supplier_create'),
    path('supplier_update/<int:id>/', views.supplier_update, name='supplier_update'),
    path('supplier_delete/<int:id>/', views.supplier_delete, name='supplier_delete'),
    path('export_suppliers_excel/', views.export_suppliers_excel, name='export_suppliers_excel'),
    path('supplier_search/', views.supplier_search, name='supplier_search'),
]

raw_materials = [
    path('raw_material_list/', views.raw_material_list, name='raw_material_list'),
    path('raw_material_view/<int:id>/', views.raw_material_view, name='raw_material_view'),
    path('raw_material_create/', views.raw_material_create, name='raw_material_create'),
    path('raw_material_update/<int:id>/', views.raw_material_update, name='raw_material_update'),
    path('raw_material_delete/<int:id>/', views.raw_material_delete, name='raw_material_delete'),
    path('export_raw_materials_excel/', views.export_raw_materials_excel, name='export_raw_materials_excel'),
    path('raw_material_search/', views.raw_material_search, name='raw_material_search'),
]

batchs =[
    path('product_batch_list/', views.product_batch_list, name='product_batch_list'),
    path('product_batch_view/<int:id>/', views.product_batch_view, name='product_batch_view'),
    path('product_batch_create/', views.product_batch_create, name='product_batch_create'),
    path('product_batch_update/<int:id>/', views.product_batch_update, name='product_batch_update'),
    path('product_batch_delete/<int:id>/', views.product_batch_delete, name='product_batch_delete'),
    path('export_product_batches_excel/', views.export_product_batches_excel, name='export_product_batches_excel'),
    path('raw_batch_list/', views.raw_batch_list, name='raw_batch_list'),
    path('raw_batch_view/<int:id>/', views.raw_batch_view, name='raw_batch_view'),
    path('raw_batch_create/', views.raw_batch_create, name='raw_batch_create'),
    path('raw_batch_update/<int:id>/', views.raw_batch_update, name='raw_batch_update'),
    path('raw_batch_delete/<int:id>/', views.raw_batch_delete, name='raw_batch_delete'),
    path('export_raw_batches_excel/', views.export_raw_batches_excel, name='export_raw_batches_excel'),
]


urlpatterns = [
    *products,
    *raw_materials,
    *suppliers,
    *batchs,
    *categorys,
]