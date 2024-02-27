from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.messages_page,name='messages_page'),
    path('search_users/', views.search_users, name='search_users'),
    path('create_thread/', views.create_thread, name='create_thread'),
    path('create_group/', views.create_group, name='create_group'),
    path('search_users_add_to_group/<uuid:group_unique_id>/', views.search_users_add_to_group, name='search_users_add_to_group'),
    path('add_to_group/',views.add_to_group,name='add_to_group'),
]




