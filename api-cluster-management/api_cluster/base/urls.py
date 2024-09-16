from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.create_user, name='create-user'),  # POST
    path('users/<int:pk>/', views.retrieve_user, name='retrieve-user'),  # GET
    path('users/<int:pk>/update/', views.update_user, name='update-user'),  # PUT
    path('users/<int:pk>/delete/', views.delete_user, name='delete-user'),  # DELETE
    path('clusters/', views.create_cluster, name='create-cluster'),  # POST
    path('clusters/<int:pk>/', views.retrieve_cluster, name='retrieve-cluster'),  # GET
    path('clusters/<int:pk>/update/', views.update_cluster, name='update-cluster'),  # PUT
    path('clusters/<int:pk>/delete/', views.delete_cluster, name='delete-cluster'),  # DELETE
    path('clusters/<int:pk>/switchover/', views.switchover, name='switchover'),  # POST
    path('clusters/<int:pk>/failover/', views.failover, name='failover'),  # POST
    # path('clusters/<int:pk>/restart/', views.delete_cluster, name='delete-cluster'),  # POST
]