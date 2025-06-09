from django.urls import path
from .views import index, charts

urlpatterns = [
    path('', index, name='index'),
    path('charts/', charts, name='charts'),
]
