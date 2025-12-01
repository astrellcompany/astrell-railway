from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path("test-email/", views.send_test, name="test_email"),
    
   
]
