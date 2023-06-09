import json
from dataclasses import asdict, dataclass

import requests
from django.conf import settings
from django.http import HttpResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt


def filter_by_keys(sourse, keys):
    filtered_data = {}

    for key, value in sourse.items():
        if key in keys:
            filtered_data[key] = value

    return filtered_data


@dataclass
class Pokemon:
    id: int
    name: str
    height: int
    weight: int
    base_experience: int

    @classmethod
    def from_raw_data(cls, raw_data):
        filtered_data = filter_by_keys(
            raw_data,
            cls.__dataclass_fields__.keys(),
        )

        return cls(**filtered_data)


POKEMONS = {}


def get_pokeapi_from_api(name):
    url = settings.POKEAPI_BASE_URL + f"/{name}"
    response = requests.get(url)
    raw_data = response.json()

    return Pokemon.from_raw_data(raw_data)


def _get_pokemon(name):
    if name in POKEMONS:
        pokemon = POKEMONS[name]
    else:
        pokemon = get_pokeapi_from_api(name=name)
        POKEMONS[name] = pokemon

    return pokemon


def _del_pokemon(name):
    del POKEMONS[name]


@csrf_exempt
def get_pokemon(request, name):
    if request.method == "GET":
        pokemon = _get_pokemon(name)

        return HttpResponse(
            content_type="application/json",
            content=json.dumps(asdict(pokemon)),
        )

    elif request.method == "DELETE":
        _del_pokemon(name)
        return HttpResponse(f"{name} DELETE")


@csrf_exempt
def get_pokemon_for_mobile(request, name):
    if request.method == "GET":
        pokemon = _get_pokemon(name)

        result = filter_by_keys(
            asdict(pokemon),
            ["id", "name", "base_experience"],
        )

        return HttpResponse(
            content_type="application/json",
            content=json.dumps(result),
        )
    elif request.method == "DELETE":
        _del_pokemon(name)
        return HttpResponse(f"{name} DELETE")


urlpatterns = [
    path("api/pokemon/<str:name>/", get_pokemon),
    path("api/pokemon/mobile/<str:name>/", get_pokemon_for_mobile),
]
