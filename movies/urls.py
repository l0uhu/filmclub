from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.film_list, name='film_list'),
    path('add/', views.film_add, name='film_add'),
    path('film/<int:film_id>/', views.film_detail, name='film_detail'),
    path('film/<int:film_id>/delete/', views.film_delete, name='film_delete'),
    path('update-order/', views.update_order, name='update_order'),
    path('films/reorder/', views.film_reorder, name='film_reorder'),
    path('classement/', views.classement, name='classement'),

    # Authentification
    path('accounts/login/', auth_views.LoginView.as_view(template_name='movies/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/signup/', views.signup, name='signup'),
]
