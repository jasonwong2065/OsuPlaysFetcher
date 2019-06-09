from keys import apiKey
import requests

beatmaps = [632241]
players = ["apple_piez"]
for player in players:
    for beatmap in beatmaps:
        parameters = {
            "k": apiKey,
            "b": beatmap,
            "u": player,
            "m": 1,
            "limit": 1
            }
        option = "get_scores"
        response = requests.get("https://osu.ppy.sh/api/" + option, params=parameters)
        print(response)
        print(response.content)