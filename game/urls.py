from django.urls import path
from .views import (
    players, create_game, play_move, get_game, possible_players,
    create_match, get_match, next_game, join_match, match_state
)

urlpatterns = [
    path('players/', players),
    path('create-game/', create_game),
    path('play-move/', play_move),
    path('game/<uuid:game_id>/', get_game),
    path('game/<uuid:game_id>/possible-players/', possible_players),
    path('create-match/', create_match),
    path('match/<uuid:match_id>/', get_match),
    path('match/<uuid:match_id>/join/', join_match),
    path('match/<uuid:match_id>/state/', match_state),
    path('next-game/', next_game),
]