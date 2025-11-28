
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Accounts/', include('Accounts.urls')),
    path('products/', include('Products.urls')),
    path('', include('Main.urls')),
    path('sells/', include('Sells.urls')),
    path('api/', include('API.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)