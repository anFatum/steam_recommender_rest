import requests
from recommend.models import SteamGame, SteamUser, Ownership
import pandas as pd
import numpy as np
from typing import Dict


def convert_data_to_rating(value):
    if value > 1000:
        return 7
    if value > 200:
        return 6
    if value > 20:
        return 5
    if value > 5:
        return 4
    if value > 1:
        return 3
    if value > 0:
        return 2
    return 1


def user_games(user_id):
    req = f'https://steamcommunity.com/profiles/{user_id}/games?tab=all&xml=1'
    games = []
    num_tries = 3
    while num_tries >= 0:
        resp = requests.get(req)
        if resp.status_code != 200:
            print(f"Status code: {resp.status_code}")
            print(f"Left retries: {num_tries}")
            if resp.status_code == 429:
                raise KeyError(f"Max retries acceeded for {user_id}")
            num_tries -= 1
            continue
        from xml.etree import ElementTree
        from xml.etree.ElementTree import ParseError
        try:
            xml_tree = ElementTree.fromstring(resp.content)
            break
        except ParseError:
            num_tries -= 1

    if num_tries < 0:
        return games

    for elem in xml_tree.iter('game'):
        app_id = elem.find('appID').text
        time_spend = elem.find('hoursOnRecord').text if elem.find('hoursOnRecord') is not None else '0'
        time_spend = time_spend.replace(',', '')
        game = {
            'user_id': int(user_id),
            'app_id': int(app_id),
            'time_spend': float(time_spend)
        }
        games.append(game)

    return games


def add_data(user_games_data: Dict):
    user_games_data = pd.DataFrame.from_dict(user_games_data)
    users = user_games_data['user_id'].unique()
    for user in users:
        u = SteamUser.objects.get_or_create(user_id=user)
        for app in user_games_data.loc[user_games_data['user_id'] == user, 'app_id']:
            game = SteamGame.objects.get_or_create(game_id=app)
            ownership = Ownership.objects.get_or_create(game=game, owner=u)
            ownership.time_played = user_games_data.loc[
                np.logical_and(user_games_data['user_id'] == u, user_games_data['app_id'] == app), 'time_played']
            game.save()
            ownership.save()
        u.save()
    if users.shape[0] == 1:
        return SteamUser.objects.get(users[0])
    else:
        return None
