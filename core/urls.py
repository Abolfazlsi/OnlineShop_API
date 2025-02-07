from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('account/', include('account.urls')),
    path('product/', include('product.urls')),
    path('cart/', include('cart.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
