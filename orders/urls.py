from django.urls import path
from . import views
from .views import track_order

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('', views.order_history, name='orders'),
     path('track_order/', views.track_order, name='track_order'),
     path('return_order/<int:order_id>/', views.return_order, name='return_order'),
]
