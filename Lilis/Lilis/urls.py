
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Accounts.urls')),
    path('products/', include('Products.urls')),
    path('main/', include('Main.urls')),
    path('sells/', include('Sells.urls'))
]
