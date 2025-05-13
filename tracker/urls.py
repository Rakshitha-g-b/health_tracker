from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add-mood/', views.add_mood, name='add_mood'),
    path('add-symptom/', views.add_symptom, name='add_symptom'),
    path('add-habit/', views.add_habit, name='add_habit'),
    path('delete-mood/<int:mood_id>/', views.delete_mood, name='delete_mood'),
    path('delete-symptom/<int:symptom_id>/', views.delete_symptom, name='delete_symptom'),
    path('delete-habit/<int:habit_id>/', views.delete_habit, name='delete_habit'),
] 