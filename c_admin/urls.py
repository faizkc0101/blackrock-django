from django.urls import path
from . import views

urlpatterns = [
    path('', views.c_login, name='c_login'),
    path('dashboard/', views.c_dashboard, name='c_dashboard'),
    path('users/', views.c_users, name='c_users'),
    path('user_status/<int:user_id>/', views.user_status, name='user_status'),
    
    # Product management
    path('products/', views.c_products, name='c_products'),
    path('products/add/', views.c_add_product, name='c_add_product'),
    path('products/<slug:slug>/update/', views.c_update_product, name='c_update_product'),
    path('products/<slug:slug>/delete/', views.c_delete_product, name='c_delete_product'),
    path('product/<slug:slug>/toggle/', views.toggle_availability, name='toggle_availability'),
    
    # Category management
    path('categories/add/', views.c_add_category, name='c_add_category'),
    path('categories/<int:id>/update/', views.c_update_category, name='c_update_category'),
    path('categories/<int:id>/delete/', views.c_delete_category, name='c_delete_category'),
    
    # Variation management
    path('variations/add/', views.c_add_variation, name='c_add_variation'),
    path('variations/<int:id>/update/', views.c_update_variation, name='c_update_variation'),
    path('variations/<int:id>/delete/', views.c_delete_variation, name='c_delete_variation'),
]
