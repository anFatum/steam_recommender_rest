from django.urls import path, include
from authenticate.views import login

urlpatterns = [
    path('login', login)
]
