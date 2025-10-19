
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Accounts.urls')),
    path('products/', include('Products.urls')),
    path('main/', include('Main.urls')),
    path('sells/', include('Sells.urls'))
]
