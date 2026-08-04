from django.urls import path
from .views import (
    players, players_meta, create_game, play_move, get_game, possible_players,
    create_match, get_match, next_game, join_match, match_state, join_by_code,
    request_draw, respond_draw, pass_turn
)

urlpatterns = [
    path('players/', players),
    path('players-meta/', players_meta),
    path('create-game/', create_game),
    path('play-move/', play_move),
    path('game/<uuid:game_id>/', get_game),
    path('game/<uuid:game_id>/possible-players/', possible_players),
    path('game/<uuid:game_id>/request-draw/', request_draw),
    path('game/<uuid:game_id>/respond-draw/', respond_draw),
    path('game/<uuid:game_id>/pass-turn/', pass_turn),
    path('create-match/', create_match),
    path('match/<uuid:match_id>/', get_match),
    path('match/<uuid:match_id>/join/', join_match),
    path('match/<uuid:match_id>/state/', match_state),
    path('join-by-code/', join_by_code),
    path('next-game/', next_game),
]