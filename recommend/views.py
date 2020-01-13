from django.views.decorators.csrf import csrf_exempt
from recommend.recommender import Recommender
from rest_framework.decorators import api_view, permission_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from recommend.models import SteamGame, SteamUser, Ownership
from django.http import HttpResponse
from recommend.utils import user_games, add_data

from rest_framework.status import (
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response

r = Recommender()


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
@api_view(["GET"])
def test(request):
    data = {'sample_data': 123}
    return Response(data, status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def game_recommend(request, user_id):
    try:
        user = SteamUser.objects.get(user_id=user_id)
        ownerships = Ownership.objects.filter(owner__user_id=user.user_id).order_by('-time_played')[:5]
    except (SteamUser.DoesNotExist, Ownership.DoesNotExist) as e:
        new_user_data = user_games(user_id)
        if len(new_user_data) == 0:
            return HttpResponse(HTTP_404_NOT_FOUND)
        else:
            user = add_data(new_user_data)
            r.update_data()

    games = list(map(lambda x: x.game.game_id, ownerships))
    recommendations = r.predict_games_for_user(games, user_id)
    data = {
        'games': recommendations
    }
    return JSONResponse(data, status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def update_games(request):
    r.update_data()
    return JSONResponse({'status': 'updated'}, status=HTTP_200_OK)
