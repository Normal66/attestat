from django.urls import path
from . import views

app_name = 'adminwrap'
urlpatterns = [
 # post views
 path('', views.get_category, name='category_list'),
 path('getexcel/<int:pk>', views.get_excel_by_categ, name='get_excel'),
  ]
