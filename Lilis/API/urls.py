from django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register(r'productos', views.producto_view_set)
router.register(r'proveedores', views.supplier_view_set)
router.register(r'lilis', views.LilisViewSet)

urlpatterns = [
    path('health/', views.health, name='health'),
    path('info/', views.info, name='info'),
    path('', include(router.urls)),
    path('login/', obtain_auth_token, name='api_login'),
    path('lilis_detail/', views.LilisDetailView.as_view(), name='lilis_detail'),
    path('lilis_update/', views.LilisUpdateView.as_view(), name='lilis_update'),
    path('warehouse_list_for_lilis/', views.WarehouseListForLilisView.as_view(), name='warehouse_list_for_lilis'),
    path('lilis_warehouse_assign/', views.WarehouseAssignView.as_view(), name='lilis_warehouse_assign'),
    path('lilis_warehouse_unassign/', views.WarehouseUnassignView.as_view(), name='lilis_warehouse_unassign'),
]