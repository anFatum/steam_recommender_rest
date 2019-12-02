from django.db import models


# Create your models here.
class SteamUser(models.Model):
    user_id = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.user_id}"


class SteamGame(models.Model):
    game_id = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.game_id}"


class Ownership(models.Model):
    time_played = models.FloatField()
    owner = models.ForeignKey(SteamUser, on_delete=models.DO_NOTHING)
    game = models.ForeignKey(SteamGame, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.owner} played {self.game} for {self.time_played}"

    class Meta:
        unique_together = (
            'owner',
            'game',
            'time_played'
        )
        ordering = ['time_played']
