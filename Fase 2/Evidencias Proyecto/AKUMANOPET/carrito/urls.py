from django.urls import path
from . import views

urlpatterns = [
    path('', views.ver_carrito, name='ver'),
    path('add/<int:producto_id>/', views.add_item, name='add'),
    path('update/<int:producto_id>/', views.update_item, name='update'),
    path('remove/<int:producto_id>/', views.remove_item, name='remove'),
    path('clear/', views.clear, name='clear'),
]
