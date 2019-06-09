from keys import apiKey
import requests, sys

BEATMAPSFILE = "topBeatmaps.txt"
DIFFICULTYTHRESHOLD = 6

def fetchBestPlays(beatmapIDs, players):
    for player in players:
        for beatmap in beatmapIDs:
            parameters = {
                "k": apiKey,
                "b": beatmap,
                "u": player,
                "m": 1,
                "limit": 1
                }
            option = "get_scores"
            response = requests.get("https://osu.ppy.sh/api/" + option, params=parameters)
            print(response.status_code)
            print(response.content)

def readTopBeatmaps():
    #Read cached file containing top beatmaps so far
    lastUpdated = '1000-01-01'
    beatmaps = []
    errorLines = []
    with open(BEATMAPSFILE,"r") as beatmapsFile:
        for line in beatmapsFile:
            line = line.strip()
            if "lastUpdated" in line:
                lastUpdated = line.split(":")[1]
                continue
            lineComponents = line.split("\t")
            if(lineComponents.count == 3):
                beatmaps.append((lineComponents[0], lineComponents[1], lineComponents[2]))
            else:
                errorLines.append(line)

    print("Beatmaps read from file:", len(beatmaps))
    if(len(errorLines) > 0):
        print("Number of read errors:" + len(errorLines))
        print("Read errors lines:", errorLines)
        sys.exit("Errors in " + BEATMAPSFILE + ", please fix them before running this program again")

    return beatmaps, lastUpdated
    #beatmapsFile.close()

#def syncBeatmapsFile(oldBeatmaps, newBeatmaps, lastUpdated):
    # 
    # with open("test", "w+") as beatmapsFile:
        # for 

def retreiveTopBeatmaps(since):
    #Retreives beatmaps greater than DIFFICULTYTHRESHOLD star rating from the 'since' date using the osu API
    newBeatmaps = []
    parameters = {
        "k": apiKey,
        "since": since, #Use the latest date to sync beatmaps
        "m": 1,
    #    "limit": 3
    }
    option = "get_beatmaps"
    response = requests.get("https://osu.ppy.sh/api/" + option, params=parameters)
    if response:
        print("Got API response for get_beatmaps")
    else:
        sys.exit("Error with API call, 'since' parameter = " + since)

    beatmapsJSON = response.json()
    for beatmap in beatmapsJSON:
        if(float(beatmap['difficultyrating']) > DIFFICULTYTHRESHOLD):
            newBeatmaps.append((beatmap['title'], beatmap['beatmap_id'], beatmap['difficultyrating']))

    lastDate = beatmapsJSON[-1]['approved_date']
    return newBeatmaps, lastDate
   # print(response.json())


beatmapIDs = [632241,525910]
players = ["apple_piez"]

#fetchBestPlays(beatmapIDs, players)
[readBeatmaps, lastUpdated] = readTopBeatmaps()
[newBeatmaps, lastUpdated] = retreiveTopBeatmaps(lastUpdated)
#syncBeatmapsFile(readBeatmaps, newBeatmaps, lastUpdated)