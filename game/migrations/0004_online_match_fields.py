# Generated manually - online "play with a friend" fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_match_game_game_number_game_match'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='match',
            name='player_x_session',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='player_o_session',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='seconds_per_move',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='turn_started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]