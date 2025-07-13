from django.urls import path
from . import views

urlpatterns = [
    path('api/initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('api/verify-payment/<str:booking_reference>/', views.verify_payment, name='verify_payment'),
]