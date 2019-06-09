from keys import apiKey
import requests, sys, datetime, time

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
    try:
        with open(BEATMAPSFILE,"r") as beatmapsFile:
            for line in beatmapsFile:
                line = line.strip()
                if "lastUpdated" in line:
                    print(line.split("\t"))
                    lastUpdated = line.split("\t")[1]
                    lastUpdated = lastUpdated.split(" ")[0]
                    continue
                lineComponents = line.split("\t")
                if(len(lineComponents) == 4):
                    beatmaps.append((lineComponents[0], lineComponents[1], lineComponents[2], lineComponents[3]))
                else:
                    errorLines.append(line)

        print("Beatmaps read from file:", len(beatmaps))
        if(len(errorLines) > 0):
            print("Number of read errors:", len(errorLines))
            print("Read errors lines:", errorLines)
            sys.exit("Errors in " + BEATMAPSFILE + ", please fix them before running this program again")
    except SystemExit:
        sys.exit()
    except:    
        print("File doesn't exist, new one will be created")
    return beatmaps, lastUpdated
    #beatmapsFile.close()

def syncBeatmapsFile(oldBeatmaps, newBeatmaps, lastUpdated):
    allBeatmaps = oldBeatmaps + newBeatmaps
    noDuplicatesSet = set(allBeatmaps)
    newMaps = list(noDuplicatesSet - set(oldBeatmaps))
    noDuplicateBeatmaps = list(noDuplicatesSet)
    print("Syncing beatmaps file")
    with open(BEATMAPSFILE, "w+") as beatmapsFile:
        beatmapsFile.write("lastUpdated\t" + lastUpdated + "\n")
        for beatmap in noDuplicateBeatmaps:
            beatmapsFile.write("\t".join(beatmap))
            beatmapsFile.write("\n")
    newBeatmapsCount = len(newMaps)
    print("Added", newBeatmapsCount, "beatmaps to", BEATMAPSFILE, "dated up to " + lastUpdated)
    for beatmap in newMaps:
        print(beatmap)
    return noDuplicateBeatmaps

def retreiveTopBeatmaps(since):
    #Retreives beatmaps greater than DIFFICULTYTHRESHOLD star rating from the 'since' date using the osu API
    print("Retreiving latest beatmaps from osu")
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
        if(float(beatmap['difficultyrating']) > DIFFICULTYTHRESHOLD and beatmap['approved'] != "4"):
            #If star rating > DIFFICULTYTHRESHOLD and it's not loved, removed the second check to include loved maps
            newBeatmaps.append((beatmap['title'], beatmap['version'], beatmap['beatmap_id'], beatmap['difficultyrating']))

    lastDate = beatmapsJSON[-1]['approved_date'].split(" ")[0]

    time.sleep(1) #Sleep to prevent overloading osu servers
    return newBeatmaps, lastDate
   # print(response.json())


beatmapIDs = [632241,525910]
players = ["apple_piez"]

todayUTC = str(datetime.datetime.utcnow()).split(" ")[0]
#fetchBestPlays(beatmapIDs, players)

[readBeatmaps, lastUpdated] = readTopBeatmaps()
newBeatmaps = []

readCounter = 0
while lastUpdated < todayUTC:
    [newBeatmaps, lastUpdated] = retreiveTopBeatmaps(lastUpdated)
    readBeatmaps = syncBeatmapsFile(readBeatmaps, newBeatmaps, lastUpdated)
    readCounter += 1
    if readCounter > 200:
        break