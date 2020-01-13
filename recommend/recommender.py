from typing import Optional
import pandas as pd
from recommend.models import Ownership, SteamUser, SteamGame
from recommend.utils import convert_data_to_rating
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors


class DataMeta(type):
    _instance = None

    def __call__(cls):
        if cls._instance is None:
            cls._instance = super(DataMeta, cls).__call__()
        return cls._instance


def get_data():
    data_list = []
    for ownership in Ownership.objects.all():
        user_id = ownership.owner.user_id
        game_id = ownership.game.game_id
        time_played = ownership.time_played
        ownership_dict = {
            'user_id': user_id,
            'game_id': game_id,
            'time_played': time_played
        }
        data_list.append(ownership_dict)
    return pd.DataFrame.from_dict(data_list)


class Recommender(metaclass=DataMeta):
    _data: pd.DataFrame = None

    def __init__(self):
        self.update_data()

    def predict_game(self, game_id):
        game_features, game_features_matrix = self.get_features_matrix(index='game_id', columns='user_id')
        predictions = self.predict(game_features, game_features_matrix, game_id)
        result = []
        for i, (idx, dist) in enumerate(predictions):
            result.append({
                'game_id': game_features.index[idx],
                'prob': dist
            })
        return result

    def predict_games(self, games_id):
        result = []
        for game_id in games_id:
            result.extend(self.predict_game(game_id))
        # TODO: add unique here
        result = sorted(result, key=lambda x: x['prob'])
        predicted = list(map(lambda x: x['game_id'], result))
        return predicted

    def predict_games_for_user(self, games_id, user_id):
        result = self.predict_games(games_id)
        owned_games = self._data.loc[self._data['user_id'] == user_id, 'game_id']
        predicted = []
        for game in result:
            if (owned_games == game).any():
                continue
            predicted.append(game)
        return predicted[:min(len(predicted), 5)]

    # def predict_user(self, user_id):
    #     game_features, game_features_matrix = self.get_features_matrix(index='user_id', columns='game_title')
    #     predictions = self.predict(game_features, game_features_matrix, user_id)
    #     for i, (idx, dist) in enumerate(predictions):
    #         print(f'{i + 1}: {game_features.index[idx]}, with chance {dist:.2f}%')

    def predict(self, game_features, game_features_matrix, key, n_recommendations=10):
        """
        Method used to predict data, based on game features and matrix, made from them
        Based on K-nearest neighbours algorithm
        :param n_recommendations:
        Number of recommendations should be predicted
        :param game_features:
        DataFrame with game features. Used for getting index of predicted objects
        :param game_features_matrix:
        Csr matrix created from :param game_features
        :param key:
        Game title/id or user id that predictions are made for
        :return:
        """
        model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
        model_knn.fit(game_features_matrix)
        idx = game_features.index.get_loc(key)
        distances, indices = model_knn.kneighbors(
            game_features_matrix[idx],
            n_neighbors=n_recommendations + 1)
        raw_recommends = \
            sorted(
                list(
                    zip(
                        indices.squeeze().tolist(),
                        distances.squeeze().tolist()
                    )
                ),
                key=lambda x: x[1]
            )[:0:-1]
        return raw_recommends

    def get_features_matrix(self, index, columns):
        """
        Method that creates features matrix for data
        :param index:
        For which feature should predictions made for
        :param columns:
        On
        :return:
        """
        game_features = self._data.pivot(
            index=index,
            columns=columns,
            values='ratings'
        ).fillna(0)

        game_features_matrix = csr_matrix(game_features.values)
        return game_features, game_features_matrix

    def append_data(self, new_data: pd.DataFrame):
        processed_data = self.process_data(new_data)
        _data = self._data.append(processed_data)

    @classmethod
    def process_data(cls, data):
        # Dropping duplicates
        data = data.drop_duplicates()

        # Convert games played to ranking scale
        data['ratings'] = 1
        data.loc[:, ['ratings']] = data['time_played'].map(convert_data_to_rating)

        return data

    def update_data(self):
        self._data = self.process_data(get_data())
