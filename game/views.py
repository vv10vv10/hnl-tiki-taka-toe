from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Player, Game, Cell, RowRule, ColRule
from .serializer import PlayerSerializer


def apply_rule(qs, field, value):
    if field == "country":
        return qs.filter(country__name__iexact=value)
    if field == "club":
        return qs.filter(clubs__name__iexact=value)
    if field == "confederation":
        return qs.filter(country__confederation__name__iexact=value)
    return qs

def get_board(game):
    cells = Cell.objects.filter(game=game)
    board = [[None for _ in range(3)] for _ in range(3)]
    for cell in cells:
        board[cell.row][cell.col] = {
            "symbol": cell.symbol,
            "player": cell.player_name
        }
    return board

def check_win(board):
    lines = []
    lines.extend(board)
    lines.extend([[board[r][c] for r in range(3)] for c in range(3)])  # cols
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])
    for line in lines:
        if line[0].symbol and line[0].symbol == line[1].symbol == line[2].symbol:
            return line[0]
    return None

def is_draw(board):
    for row in board:
        for cell in row:
            if cell is None:
                return False
    return True

# Create your views here.
@api_view(['GET'])
def players(request):
    players = Player.objects.all()
    serializer = PlayerSerializer(players, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def play_move(request):
    game_id = request.data.get("game_id")
    row = int(request.data.get("row"))
    col = int(request.data.get("col"))
    player_name = request.data.get("player_name")

    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return Response({"valid": False, "reason": "Game not found"})
    if game.is_finished:
        return Response({"valid": False, "reason": "Game is finished"})
    if row is None or col is None or player_name is None:
        return Response({"valid": False, "reason": "Missing data"})
    if row < 0 or row > 2 or col < 0 or col > 2:
        return Response({"valid": False, "reason": "Invalid board position"})

    player = Player.objects.filter(name__iexact=player_name).first()
    if not player:
        return Response({"valid": False, "reason": "Player not found"})
    
    try:
        cell = Cell.objects.get(game=game, row=row, col=col)
    except Cell.DoesNotExist:
        return Response({"valid": False, "reason": "Cell not found"})
    if cell.symbol is not None:
        return Response({"valid": False, "reason": "Cell already taken"})

    qs = Player.objects.filter(id=player.id)
    row_rule = RowRule.objects.get(game=game, index=row)
    col_rule = ColRule.objects.get(game=game, index=col)
    qs = apply_rule(qs, row_rule.field, row_rule.value)
    qs = apply_rule(qs, col_rule.field, col_rule.value)
    if not qs.exists():
        return Response({"valid": False, "reason": "Invalid move"})

    cell = Cell.objects.get(game=game, row=row, col=col)
    cell.player_name = player.name
    cell.symbol = game.current_turn
    cell.save()

    game.current_turn = "O" if game.current_turn == "X" else "X"
    board = get_board(game)
    winner = check_win(board)
    if winner:
        game.is_finished = True
        game.winner = winner
    elif is_draw(board):
        game.is_finished = True
        game.winner = "draw"
    game.save()

    return Response({
        "valid": True,
        "board": board,
        "current_turn": game.current_turn,
        "is_finished": game.is_finished,
        "winner": game.winner
    })

@api_view(['POST'])
def create_game(request):
    game = Game.objects.create()
    RowRule.objects.bulk_create([
        RowRule(game=game, index=0, field="country", value="Hrvatska"),
        RowRule(game=game, index=1, field="club", value="Barcelona"),
        RowRule(game=game, index=2, field="country", value="Argentina"),
    ])
    ColRule.objects.bulk_create([
        ColRule(game=game, index=0, field="club", value="PSG"),
        ColRule(game=game, index=1, field="country", value="Brazil"),
        ColRule(game=game, index=2, field="club", value="Real Madrid"),
    ])
    for r in range(3):
        for c in range(3):
            Cell.objects.create(game=game, row=r, col=c)

    return Response({"game_id": str(game.id)})


@api_view(['GET'])
def get_game(request, game_id):
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return Response({
            "error": "Game not found"
        }, status=404)

    board = get_board(game)
    return Response({
        "game_id": str(game.id),
        "board": board,
        "is_finished": game.is_finished,
        "winner": game.winner
    })
