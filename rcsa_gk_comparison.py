import json

##### USEFUL LINKS #####
# https://www.footballdatabase.eu/fr/club/equipe/33-strasbourg/2017-2018



##### OPEN JSONs FILES #####

with open('wyscout_data/competitions.json') as f:
    competitions = json.load(f)

with open('wyscout_data/teams.json') as t:
    teams = json.load(t)

with open('wyscout_data/players.json') as p:
    players = json.load(p)

with open('wyscout_data/matches/matches_France.json') as m:
    matches = json.load(m)
    
with open('wyscout_data/events/events_France.json') as e:
    events = json.load(e)



##### SETTING VARIABLE OF INTEREST #####

# ID of Ligue 1
competitionId = 412

# ID of RC Strasbourg Alsace
strasbourgId  = 3779

# ID of Oukidja
oukidjaId     = 26676
kamaraId      = 301635



##### GET A LIST OF ALL MATCH FROM RCSA #####

matchIdList = []
matchNameList = []
for match in matches:
    leagueMatchList = list(match['teamsData'].keys())
    if leagueMatchList[0] == '3779' or leagueMatchList[1] == '3779':
        matchIdList.append(match['wyId'])
        matchNameList.append(match['label'])

gameDict = dict(zip(matchIdList, matchNameList)) 


##### GET ALL CONCEDED GOALS EVENT #####
concededGoalTotal    = 0
concededGoalKamara   = 0
concededGoalOukidja  = 0
concededGoalBonnefoi = 6
concededOwnGoal      = 0

for matchId, matchName in gameDict.items():
    print('Match ID = ', matchName)
    for event in events:
        if(event['matchId'] == matchId):

            eventType = event['eventName']
            if event['tags']:
                tag = event['tags'][0].get('id')
            teamId = event['teamId']

            if (eventType == 'Shot' or eventType == 'Free Kick') and \
               tag == 101                                        and \
                teamId != strasbourgId:
                        y = event['positions'][0].get('y')
                        x = event['positions'][0].get('x')
                        shotCoord = [x, y]
                        concededGoalTotal = concededGoalTotal + 1
                        print("Goal scored from " + str(shotCoord))
            elif tag == 102 and teamId == strasbourgId:
                concededOwnGoal = concededOwnGoal + 1
                concededGoalTotal = concededGoalTotal + 1
            if tag == 101 and teamId == strasbourgId:
                if (event['playerId'] == oukidjaId):
                    print("Goal conceded by Oukidja")
                    concededGoalOukidja = concededGoalOukidja + 1
                elif (event['playerId'] == kamaraId):
                    print("Goal conceded by Kamara")
                    concededGoalKamara = concededGoalKamara + 1


print("Goal conceded by Strasbourg : " + str(concededGoalTotal))
print("Goal conceded by Oukidja : "    + str(concededGoalOukidja))
print("Goal conceded by Kamara : "     + str(concededGoalKamara))  
print("Goal conceded by Bonnefoi : "   + str(concededGoalBonnefoi))
print("Own goal conceded : "           + str(concededOwnGoal))      