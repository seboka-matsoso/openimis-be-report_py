from django.urls import path
from . import views

urlpatterns = [
    path('<str:module_name>/<str:report_name>/<str:report_format>/', views.report, name='report'),
    path('<str:module_name>/<str:report_name>/<str:report_format>/<str:alternate>/', views.report, name='report'),
]
