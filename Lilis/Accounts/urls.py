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
    path('user_view/<int:id>', views.user_view, name='user_view'),
    path('edit_field/', views.edit_field, name='edit_field'),
    path('password_change/', views.password_change, name='password_change'),
    path('token_verify/', views.token_verify, name='token_verify'),
    path('password_recover/', views.password_recover, name='password_recover'),
    path('role_changer/', views.role_changer, name='role_changer'),
    path('user_picture/<int:id>', views.user_picture, name='user_picture'),
]
