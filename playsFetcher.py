from keys import apiKey
import requests, sys, datetime, time

BEATMAPSFILE = "topBeatmaps.txt" #Delete the file or change the name to made another beatmaps file
SCORESFILE = "scores.txt"
DIFFICULTYTHRESHOLD = 6
REFRESHSCORES = True
MODE = 1  #(0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania).
USERNAMES = ["Jaye"] #Who to calculate scores for

def fetchBestPlays(beatmapIDs, players):
    for player in players:
        for beatmap in beatmapIDs:
            parameters = {
                "k": apiKey,
                "b": beatmap,
                "u": player,
                "m": MODE,
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
                    lastUpdated = line.split("\t")[1]
                    lastUpdated = lastUpdated.split(" ")[0]
                    continue
                lineComponents = line.split("\t")
                if(len(lineComponents) == 4):
                    beatmaps.append((lineComponents[0], lineComponents[1], lineComponents[2], lineComponents[3]))
                else:
                    errorLines.append(line)

        print("Beatmaps read from", BEATMAPSFILE, ":", len(beatmaps))
        if(len(errorLines) > 0):
            print("Number of read errors:", len(errorLines))
            print("Read errors lines:", errorLines)
            sys.exit("Errors in " + BEATMAPSFILE + ", please fix them before running this program again")
    except SystemExit:
        sys.exit()
    except:    
        print(BEATMAPSFILE, "doesn't exist, creating it")
    return beatmaps, lastUpdated


def readScores():
    #Read cached user scores
    scores = []
    errorLines = []
    try:
        with open(SCORESFILE,"r") as scoresFile:
            for line in scoresFile:
                line = line.strip()
                lineComponents = line.split("\t")
                if(len(lineComponents) == 3 and lineComponents[0] in USERNAMES):
                    (username, beatmapID, passStatus) = (lineComponents[0], lineComponents[1], lineComponents[2])
                    scores.append((username, beatmapID, passStatus))
                else:
                    errorLines.append(line)

        print("Scores read from", SCORESFILE, ":", len(scores))
        if(len(errorLines) > 0):
            print("Number of read errors:", len(errorLines))
            print("Read errors lines:", errorLines)
            sys.exit("Errors in " + SCORESFILE + ", please fix them before running this program again")
    except SystemExit:
        sys.exit()
    except:    
        print(SCORESFILE, "doesn't exist, creating it")
    return scores

def getMissingScores(beatmaps, oldScores):
    #Finds which scores are needed to complete the spreadsheet.
    allScores = {}
    for beatmap in beatmaps:
        for username in USERNAMES:
            beatmapID = beatmap[2]
            allScores.add((username, beatmapID))

    missingScores = {}
    if(REFRESHSCORES):
        #If force refresh flag is true
        print("Refreshing scores file", SCORESFILE)
        missingScores = allScores
    else:
        missingScores = allScores - set(oldScores)

    return list(missingScores)
        
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
        "m": MODE,
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
        if(float(beatmap['difficultyrating']) > DIFFICULTYTHRESHOLD and beatmap['approved'] in ["1","2"]):
            #If star rating > DIFFICULTYTHRESHOLD and it's not loved, removed the second check to include loved maps
            newBeatmaps.append((beatmap['title'], beatmap['version'], beatmap['beatmap_id'], beatmap['difficultyrating']))

    lastDate = beatmapsJSON[-1]['approved_date'].split(" ")[0]

    time.sleep(1) #Sleep to prevent overloading osu servers
    return newBeatmaps, lastDate

players = ["apple_piez"]

#fetchBestPlays(beatmapIDs, players)

###
# Reads the beatmaps cache
###

[readBeatmaps, lastUpdated] = readTopBeatmaps()
newBeatmaps = []

###
# Retreive any new beatmaps from osu if beatmaps file is outdated
###
readCounter = 0
todayUTC = str(datetime.datetime.utcnow()).split(" ")[0]
while lastUpdated < todayUTC:
    #Retreive all top beatmaps
    [newBeatmaps, lastUpdated] = retreiveTopBeatmaps(lastUpdated)
    readBeatmaps = syncBeatmapsFile(readBeatmaps, newBeatmaps, lastUpdated)
    readCounter += 1
    if readCounter > 200:
        #Prevent infinite loops in case there's any
        break

###
# Reads the players cache for existing scores (note this doesn't automatically update if new highscores are made, set REFRESHSCORES to True to update)
###

readScores()