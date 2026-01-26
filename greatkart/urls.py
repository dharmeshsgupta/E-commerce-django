from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='home'),
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    # ORDERS APP URL
    path('orders/', include('orders.urls')),
    # Check these two lines carefully:
    path('accounts/', include('allauth.urls')),  # This handles the google login
    path('accounts/', include('accounts.urls')), # This handles your register/login views
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
