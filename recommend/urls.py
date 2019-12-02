from django.urls import path
from recommend.views import test, game_recommend

urlpatterns = [
    path('test', test),
    path('user/<int:user_id>', game_recommend)
]
