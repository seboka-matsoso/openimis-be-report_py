from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('<str:module_name>/<str:report_name>/<str:report_format>/', views.report, name='report'),
    path('<str:module_name>/<str:report_name>/<str:report_format>/<str:alternate>/', views.report, name='report'),
    path("designer", views.report_designer, name="reportbro_designer"),
    path(
        "preview",
        csrf_exempt(views.preview_report),
        name="reportbro_previewer",
    ),
