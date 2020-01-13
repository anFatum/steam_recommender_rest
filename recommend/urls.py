from django.urls import path
from recommend.views import test, game_recommend, update_games

urlpatterns = [
    path('test', test),
    path('user/<int:user_id>', game_recommend),
    path('update', update_games)
]
