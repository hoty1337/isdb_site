from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about', views.about, name='about'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('doctors', views.doctors, name='doctors'),
    path('appointments', views.appointments, name='appointments'),
    path('get_reviews', views.get_reviews, name='get_reviews'),
    path('send_review', views.send_review, name='send_review'),
    path('get_free_time', views.get_free_time, name='get_free_time')
]
