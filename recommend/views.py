from django.views.decorators.csrf import csrf_exempt
from recommend.recommender import Recommender
from rest_framework.decorators import api_view, permission_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from recommend.models import SteamGame, SteamUser, Ownership
from django.http import HttpResponse

from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

    # Create your views here.


@csrf_exempt
@api_view(["GET"])
def test(request):
    data = {'sample_data': 123}
    return Response(data, status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def game_recommend(request, user_id):
    try:
        user = SteamUser.objects.get(user_id=user_id)
        ownerships = Ownership.objects.filter(owner__user_id=user.user_id).order_by('-time_played')[:5]
    except (SteamUser.DoesNotExist, Ownership.DoesNotExist) as e:
        return HttpResponse(HTTP_404_NOT_FOUND)
    games = list(map(lambda x: x.game.game_id, ownerships))
    r = Recommender()
    recommendations = r.predict_games(games)
    data = {
        'games': recommendations
    }
    return JSONResponse(data, status=HTTP_200_OK)
