from django.urls import path
from . import views

categorys = [
    path('category_list/', views.category_list, name='category_list'),
    path('category_create/', views.category_create, name='category_create'),
    path('category_update/<int:id>/', views.category_update, name='category_update'),
    path('category_delete/<int:id>/', views.category_delete, name='category_delete'),
]
    
products = [
    path('products_list/' , views.products_list ,name='products_list'),
    path('product_view<int:id>/', views.product_view, name='product_view'),
    path('product_create/' , views.product_create ,name='product_create'),
    path('product_delete/<int:id>/' , views.product_delete ,name='product_delete'),
    path('product_update/<int:id>/' , views.product_update ,name='product_update'),
    path('export_products_excel/', views.export_products_excel, name='export_products_excel'),
]

suppliers = [
    path('supplier_list/', views.supplier_list, name='supplier_list'),
    path('supplier_view/<int:id>/', views.supplier_view, name='supplier_view'),
    path('supplier_create/', views.supplier_create, name='supplier_create'),
    path('supplier_update/<int:id>/', views.supplier_update, name='supplier_update'),
    path('supplier_delete/<int:id>/', views.supplier_delete, name='supplier_delete'),
]

raw_materials = [
    path('raw_material_list/', views.raw_material_list, name='raw_material_list'),
    path('raw_material_view/<int:id>/', views.raw_material_view, name='raw_material_view'),
    path('raw_material_create/', views.raw_material_create, name='raw_material_create'),
    path('raw_material_update/<int:id>/', views.raw_material_update, name='raw_material_update'),
    path('raw_material_delete/<int:id>/', views.raw_material_delete, name='raw_material_delete'),
]

batchs =[
    path('product_batch_list/', views.product_batch_list, name='product_batch_list'),
    path('product_batch_view/<int:id>/', views.product_batch_view, name='product_batch_view'),
    path('product_batch_create/', views.product_batch_create, name='product_batch_create'),
    path('product_batch_update/<int:id>/', views.product_batch_update, name='product_batch_update'),
    path('product_batch_delete/<int:id>/', views.product_batch_delete, name='product_batch_delete'),
    path('raw_batch_list/', views.raw_batch_list, name='raw_batch_list'),
    path('raw_batch_view/<int:id>/', views.raw_batch_view, name='raw_batch_view'),
    path('raw_batch_create/', views.raw_batch_create, name='raw_batch_create'),
    path('raw_batch_update/<int:id>/', views.raw_batch_update, name='raw_batch_update'),
    path('raw_batch_delete/<int:id>/', views.raw_batch_delete, name='raw_batch_delete'),
]


urlpatterns = [
    *products,
    *raw_materials,
    *suppliers,
    *batchs,
    *categorys,
]