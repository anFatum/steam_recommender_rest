from django.db import models


class SteamUser(models.Model):
    user_id = models.IntegerField(unique=True)

    def __str__(self):
        return "{}".format(self.user_id)


class SteamGame(models.Model):
    game_id = models.IntegerField(unique=True)

    def __str__(self):
        return "{}".format(self.game_id)


class Ownership(models.Model):
    time_played = models.FloatField()
    owner = models.ForeignKey(SteamUser, on_delete=models.DO_NOTHING)
    game = models.ForeignKey(SteamGame, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{} played {} for {}".format(self.owner, self.game, self.time_played)

    class Meta:
        unique_together = (
            'owner',
            'game',
            'time_played'
        )
        ordering = ['time_played']
