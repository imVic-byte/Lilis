from django.urls import path
from Accounts import views
from django.contrib.auth import views as views_auth

urlpatterns = [
    path('', views_auth.LoginView.as_view(template_name='login.html'),name='login'),
    path('logout/', views_auth.LogoutView.as_view(next_page='login'),name='logout'),
    path('registro/', views.registro,name='registro'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('user_list', views.user_list, name='user_list'),
    path('user_delete/<int:id>', views.user_delete, name='user_delete'),
    path('user_update/<int:id>', views.user_update, name='user_update'),
]
