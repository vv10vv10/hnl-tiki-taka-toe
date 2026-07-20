from django.db import models
import uuid

# Create your models here.
class Confederation(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100)
    confederation = models.ForeignKey(
        Confederation,
        on_delete=models.CASCADE,
        related_name="countries"
    )

    def __str__(self):
        return self.name


class Club(models.Model):
    tm_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Player(models.Model):
    tm_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    name_in_home_country = models.CharField(max_length=100)
    search_name = models.CharField(max_length=100)
    is_retired = models.BooleanField(default=False)
    market_value = models.FloatField(default=0)
    player_slug = models.CharField(max_length=150)

    clubs = models.ManyToManyField("Club", related_name="players")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name="players")
    coaches = models.ManyToManyField("Coach", related_name="players")

    hnl_nastupi = models.IntegerField(default=0)
    kup_nastupi = models.IntegerField(default=0)
    superkup_nastupi = models.IntegerField(default=0)
    a_repka_nastupi = models.IntegerField(default=0)

    hnl_golovi = models.IntegerField(default=0)
    finale_kupa_nastupi = models.IntegerField(default=0)
    finale_kupa_golovi = models.IntegerField(default=0)
    superkup_golovi = models.IntegerField(default=0)

    najbolji_strijelac = models.IntegerField(default=0)

    hnl_naslovi = models.IntegerField(default=0)
    kup_naslovi = models.IntegerField(default=0)
    superkup_naslovi = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Coach(models.Model):
    tm_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    best_of = models.IntegerField(default=3)  # 1, 3 ili 5
    categories = models.JSONField(default=list)  # odabrane kategorije, iste za sve igre u seriji
    x_wins = models.IntegerField(default=0)
    o_wins = models.IntegerField(default=0)
    is_finished = models.BooleanField(default=False)
    winner = models.CharField(max_length=1, null=True, blank=True)  # "X" ili "O"

    # play with a friend (online preko linka)
    is_online = models.BooleanField(default=False)
    player_x_session = models.UUIDField(null=True, blank=True)
    player_o_session = models.UUIDField(null=True, blank=True)
    seconds_per_move = models.IntegerField(null=True, blank=True)  # None = bez limita

    def __str__(self):
        return f"Match {self.id} (Bo{self.best_of})"

class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, blank=True, related_name="games")
    game_number = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)
    winner = models.CharField(max_length=100, null=True, blank=True)
    current_turn = models.CharField(
        max_length=1,
        choices=[("X", "X"), ("O", "O")],
        default="X"
    )
    turn_started_at = models.DateTimeField(null=True, blank=True)  # za online timer po potezu

class Cell(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="cells")
    row = models.IntegerField()
    col = models.IntegerField()
    player_name = models.CharField(max_length=100, null=True, blank=True)
    symbol = models.CharField(max_length=1, null=True, blank=True)

class RowRule(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="row_rules")
    index = models.IntegerField()
    field = models.CharField(max_length=50)
    value = models.CharField(max_length=100)
    display = models.CharField(max_length=100)

class ColRule(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="col_rules")
    index = models.IntegerField()  # 0,1,2
    field = models.CharField(max_length=50)
    value = models.CharField(max_length=100)
    display = models.CharField(max_length=100)