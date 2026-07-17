from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Player, Game, Cell, RowRule, ColRule, Country, Club, Confederation, Coach, Match
from .serializer import PlayerSerializer
import random
from functools import partial
from .engine.players import get_all_players
from .engine.rules import apply_rule
from .engine.board import get_board
from .engine.logic import check_win, is_draw

RULE_TYPES = [
    "country",
    "club",
    "confederation",
    "coach",
    "hnl_nastupi",
    "hnl_golovi"
]

VALID_COUNTRIES = [
    "Albania",
    #"Algeria", #
    "Argentina",
    "Australia",
    "Austria",
    #"Azerbaijan", #
    "Bosnia-Herzegovina",
    "Brazil",
    #"Bulgaria", #
    #"Colombia", #
    #"Cote d'Ivoire", #
    "Croatia", #(možda prelagano)
    #"Georgia", #
    #"Ghana", #
    #"Greece", #
    #"Hungary", #
    "Japan",
    "Kosovo",
    "Montenegro",
    #"Morocco", #
    #"Netherlands", #
    #"Nigeria", #
    "North Macedonia",
    #"Poland", #
    "Portugal",
    #"Senegal", #
    "Serbia",
    "Slovenia",
    "Spain",
    #"Sweden", #
    "Switzerland",
    #"The Gambia", #
    "Ukraine"
]
VALID_CONFEDERATIONS = [
    "AFC",
    "CAF",
    "CONMEBOL"
]
VALID_CLUBS = [
  "GNK Dinamo Zagreb",
  "HNK Hajduk Split",
  "HNK Rijeka",
  "HNK Sibenik",
  "NK Osijek",
  "NK Varazdin",
  "Slaven Belupo Koprivnica",
  #"NK Zagreb",
  "NK Istra 1961",
  #"NK Medjimurje Cakovec",
  #"NK Kamen Ingrad Velika",
  #"HNK Cibalia Vinkovci",
  #"NK Zadar",
  #"NK Inter Zapresic",
  #"NK Croatia Sesvete",
  #"NK Karlovac 1919",
  "NK Lokomotiva Zagreb",
  "RNK Split",
  "NK Hrvatski Dragovoljac",
  #"NK Lucko",
  "NK Rudes",
  "HNK Gorica",
  "HNK Vukovar 1991"
]

def random_rule(allowed_fields=None):
    fields = allowed_fields if allowed_fields else RULE_TYPES
    field = random.choice(fields)
    if field == "country":
        value = random.choice(VALID_COUNTRIES)
        display = value
    elif field == "club":
        value = random.choice(VALID_CLUBS)
        display = value
    elif field == "confederation":
        value = random.choice(VALID_CONFEDERATIONS)
        display = value
    elif field == "coach":
        value = random.choice(list(Coach.objects.values_list("name", flat=True)))
        display = value
    elif field == "hnl_nastupi":
        value = random.choice([100, 150, 200])
        display = f"{value}+ HNL nastupa"
    elif field == "hnl_golovi":
        value = str(random.choice([20,35,50]))
        display = f"{value}+ HNL golova"
    return field, value, display

def create_rules(game, allowed_fields=None):
    RowRule.objects.filter(game=game).delete()
    ColRule.objects.filter(game=game).delete()

    row_rules = []
    col_rules = []
    used = set()

    for i in range(3):
        while True:
            rule = random_rule(allowed_fields)
            field, value, display = rule
            if (field, value) in used:
                continue
            if field in ["hnl_nastupi", "hnl_golovi"]:
                if any(r[0] == field for r in row_rules):
                    continue
            elif field == "country":
                if any(r[0] == "confederation" and Country.objects.filter(name=value).first().confederation.name == r[1] for r in row_rules):
                    continue
            elif field == "confederation":
                if any(r[0] == "country" and Country.objects.filter(name=r[1]).first().confederation.name == value for r in row_rules):
                    continue
            break
        used.add((field, value))
        row_rules.append(rule)

    for i in range(3):
        while True:
            rule = random_rule(allowed_fields)
            field, value, display = rule
            if (field, value) in used:
                continue
            if field in ["hnl_nastupi", "hnl_golovi"]:
                if any(r[0] == field for r in row_rules + col_rules):
                    continue
            if rules_conflict(rule, row_rules):
                continue
            if rules_conflict(rule, col_rules):
                continue
            break
        used.add((field, value))
        col_rules.append(rule)

    for i, (field, value, display) in enumerate(row_rules):
        RowRule.objects.create(game=game,index=i,field=field,value=value,display=display)
    for i, (field, value, display) in enumerate(col_rules):
        ColRule.objects.create(game=game,index=i,field=field,value=value,display=display)

def rules_conflict(new_rule, existing_rules):
    new_field, new_value, _ = new_rule

    for field, value, _ in existing_rules:
        if new_field in ["hnl_nastupi", "hnl_golovi"] and new_field == field:
            return True

        if new_field == "confederation" and field == "confederation":
            return True

        if new_field == "country" and field == "country":
            return True

        if new_field == "country" and field == "confederation":
            country = Country.objects.filter(name=new_value).first()
            if country and country.confederation.name == value:
                return True

        if new_field == "confederation" and field == "country":
            country = Country.objects.filter(name=value).first()
            if country and country.confederation.name == new_value:
                return True
    return False

def board_is_valid(game):
    players = get_all_players()
    row_rules = list(RowRule.objects.filter(game=game).order_by("index"))
    col_rules = list(ColRule.objects.filter(game=game).order_by("index"))
    for r in range(3):
        for c in range(3):
            filtered = apply_rule(players, row_rules[r].field, row_rules[r].value)
            filtered = apply_rule(filtered, col_rules[c].field, col_rules[c].value)
            if len(filtered) == 0:
                return False
    return True

def generate_valid_game(allowed_fields, match=None, game_number=1):
    game = Game.objects.create(match=match, game_number=game_number)
    while True:
        create_rules(game, allowed_fields)
        if board_is_valid(game):
            break
        game.row_rules.all().delete()
        game.col_rules.all().delete()
    for r in range(3):
        for c in range(3):
            Cell.objects.create(game=game, row=r, col=c)
    return game

def resolve_allowed_fields(requested_categories):
    allowed_fields = None
    if requested_categories:
        allowed_fields = [f for f in requested_categories if f in RULE_TYPES]
    if not allowed_fields or len(allowed_fields) < 2:
        allowed_fields = RULE_TYPES
    return allowed_fields

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

    player = Player.objects.filter(name=player_name).first()
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
    valid_move = True
    if not qs:
        valid_move = False
    if valid_move:
        cell.player_name = player.name
        cell.symbol = game.current_turn
        cell.save()

    game.current_turn = "O" if game.current_turn == "X" else "X"
    cells = Cell.objects.filter(game=game)
    board = get_board(cells)
    winner_data = check_win(board)
    if winner_data:
        game.is_finished = True
        game.winner = winner_data["winner"]
        winning_line=winner_data["line"]
    elif is_draw(board):
        game.is_finished = True
        game.winner = "draw"
        winning_line=None
    else:
        winning_line=None
    game.save()

    match_data = None
    if game.is_finished and game.match:
        match = game.match
        if game.winner == "X":
            match.x_wins += 1
        elif game.winner == "O":
            match.o_wins += 1
        majority = match.best_of // 2 + 1
        if match.x_wins >= majority:
            match.is_finished = True
            match.winner = "X"
        elif match.o_wins >= majority:
            match.is_finished = True
            match.winner = "O"
        match.save()
        match_data = match_summary(match)

    return Response({
        "valid": valid_move,
        "board": board,
        "current_turn": game.current_turn,
        "is_finished": game.is_finished,
        "winner": game.winner,
        "winning_line": winning_line,
        "match": match_data
    })

@api_view(['POST'])
def create_game(request):
    allowed_fields = resolve_allowed_fields(request.data.get("categories"))
    game = generate_valid_game(allowed_fields)
    return Response({"game_id": str(game.id)})


def match_summary(match):
    return {
        "match_id": str(match.id),
        "best_of": match.best_of,
        "x_wins": match.x_wins,
        "o_wins": match.o_wins,
        "is_finished": match.is_finished,
        "winner": match.winner,
        "games_played": match.games.count(),
    }

@api_view(['POST'])
def create_match(request):
    best_of = request.data.get("best_of")
    if best_of not in [3, 5]:
        best_of = 3
    allowed_fields = resolve_allowed_fields(request.data.get("categories"))

    match = Match.objects.create(best_of=best_of, categories=allowed_fields)
    game = generate_valid_game(allowed_fields, match=match, game_number=1)

    return Response({
        "match": match_summary(match),
        "game_id": str(game.id)
    })

@api_view(['GET'])
def get_match(request, match_id):
    try:
        match = Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        return Response({"error": "Match not found"}, status=404)
    return Response(match_summary(match))

@api_view(['POST'])
def next_game(request):
    match_id = request.data.get("match_id")
    try:
        match = Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        return Response({"error": "Match not found"}, status=404)

    if match.is_finished:
        return Response({"error": "Match is already finished"}, status=400)

    # ako postoji nedovrsena igra u seriji (netko je zatrazio remi), zabiljezi je kao remi
    current_game = match.games.filter(is_finished=False).order_by('-game_number').first()
    if current_game:
        current_game.is_finished = True
        current_game.winner = "draw"
        current_game.save()

    next_number = match.games.count() + 1
    game = generate_valid_game(match.categories, match=match, game_number=next_number)

    return Response({
        "match": match_summary(match),
        "game_id": str(game.id)
    })

@api_view(['GET'])
def get_game(request, game_id):
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return Response({
            "error": "Game not found"
        }, status=404)

    cells = Cell.objects.filter(game=game)
    board = get_board(cells)
    return Response({
        "game_id": str(game.id),
        "board": board,
        "row_rules": [
            {"index": r.index, "field": r.field, "value": r.value, "display": r.display}
            for r in game.row_rules.all()
        ],
        "col_rules": [
            {"index": c.index, "field": c.field, "value": c.value, "display": c.display}
            for c in game.col_rules.all()
        ],
        "current_turn": game.current_turn,
        "is_finished": game.is_finished,
        "winner": game.winner,
        "match_id": str(game.match.id) if game.match else None,
        "game_number": game.game_number,
        "match": match_summary(game.match) if game.match else None
    })

@api_view(['GET'])
def possible_players(request, game_id):
    row = int(request.GET.get("row"))
    col = int(request.GET.get("col"))
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return Response({"error": "Game not found"}, status=404)
    try:
        row_rule = RowRule.objects.get(game=game, index=row)
        col_rule = ColRule.objects.get(game=game, index=col)
    except:
        return Response({"error": "Rules not found"}, status=404)
    players = Player.objects.all()
    players = apply_rule(
        players,
        row_rule.field,
        row_rule.value
     )
    players = apply_rule(
        players,
        col_rule.field,
        col_rule.value
    )
    return Response([
        {
            "name": player.name,
            "search_name": player.search_name
        }
        for player in players
    ])