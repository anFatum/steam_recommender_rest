from rest_framework import serializers
from recommend.models import SteamGame, SteamUser, Ownership


class SteamGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SteamGame
        fields = ['game_id']


class SteamUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SteamUser
        fields = ['user_id']


class OwnershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ownership
        fields = ['owner', 'game', 'time_played']
