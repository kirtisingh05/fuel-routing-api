# routing/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Maps to the get_route function in views.py
    path('route/', views.get_route, name='get_route'), 
]