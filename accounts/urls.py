from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('verify/', views.verify, name='verify'), 
    path('forgetpassword/', views.forgetpassword, name='forgetpassword'),
    path('reset/<uidb64>/<token>/', views.newpassword, name='newpassword'),

]
