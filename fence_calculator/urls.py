from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('calculate/', views.calculate, name='calculate'),
    path('calculation/<int:pk>', views.calculation_detail, name='calculation_detail'),
    path('export_pdf/<int:pk>', views.export_pdf, name='export_pdf'),
    path('export_excel/<int:pk>', views.export_excel, name='export_excel'),

    # APIs
    path('api/fence-types', views.api_fence_types, name='api_fence_types'),
    path('api/materials', views.api_materials, name='api_materials'),

    # Settings
    path('settings', views.settings_view, name='settings'),
    path('settings/api/materials', views.settings_api_materials, name='settings_api_materials'),
    path('settings/api/update-material', views.settings_api_update_material, name='settings_api_update_material'),
    path('settings/api/scrape', views.settings_api_scrape, name='settings_api_scrape'),
]
