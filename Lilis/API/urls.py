from django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register(r'productos', views.producto_view_set)
router.register(r'proveedores', views.supplier_view_set)

urlpatterns = [
    path('health/', views.health, name='health'),
    path('info/', views.info, name='info'),
    path('', include(router.urls)),
    path('login/', obtain_auth_token, name='api_login')
]