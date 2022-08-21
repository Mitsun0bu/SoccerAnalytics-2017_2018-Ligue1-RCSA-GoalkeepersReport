import json
import pandas as pd
import matplotlib.pyplot as plt
from   mplsoccer import VerticalPitch


##### FUNCTION DEFINITIONS #####

def draw_divided_pitch(ax , grids = False):
    '''
    This function returns a vertical football pitch
    divided in specific locations.

    Arguments passed as parameters :
        ax    (obj)  : a matplotlib axes
        grids (bool) : should draw the grid lines or not
    '''
    


    # Draw a vertical pitch
    pitch = VerticalPitch(
        pitch_type = "opta",
        half = True,
        label = True,
        tick = True,
        goal_type='box',
        linewidth = 1.25,
        line_color = 'black'
    )
    pitch.draw(ax = ax)

    # Draw the divisions
    if grids:
        y_lines = [100 - 10 * x for x in range(1,10)]
        x_lines = [100 - 20 * x for x in range(1,10)]

        for i in x_lines:
            ax.plot(
                [i, i], [0, 100], 
                color = "lightgray", 
                ls = "--",
                lw = 1,
                zorder = -1
            )
        for j in y_lines:
            ax.plot(
                [100, 0], [j, j],
                color = "lightgray", 
                ls = "--",
                lw = 1,
                zorder = -1
            )

    return ax

##### OPEN JSONs FILES #####

with open('../wyscout_data/competitions.json') as f:
    competitions = json.load(f)

with open('../wyscout_data/teams.json') as t:
    teams = json.load(t)

with open('../wyscout_data/players.json') as p:
    players = json.load(p)

with open('../wyscout_data/matches/matches_France.json') as m:
    matches = json.load(m)
    
with open('../wyscout_data/events/events_France.json') as e:
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

gameDict = {}
for match in matches:
    leagueMatchList = list(match['teamsData'].keys())
    if leagueMatchList[0] == '3779' or leagueMatchList[1] == '3779':
        gameDict.update({match['wyId'] : match['label']})


##### GET ALL CONCEDED GOALS EVENT #####

concededGoalTotal    = 0
concededGoalKamara   = 0
concededGoalOukidja  = 0
concededGoalBonnefoi = 6
concededOwnGoal      = 0
whoConcededList      = []
shotXList            = []
shotYList            = []

# For each match playe by RCSA
for matchId, matchName in gameDict.items():
    # print('Match ID = ', matchName)
    # For each event in the data set
    for event in events:
        # If the event corresponds to a match played by RCSA 
        if(event['matchId'] == matchId):
            eventType = event['eventName']
            if event['tags']:
                tag = event['tags'][0].get('id')
            teamId = event['teamId']
            # If the event is a 'Shot' / 'Free Kick' by an opposing team leading to a goal against RCSA
            if (eventType == 'Shot' or eventType == 'Free Kick') and \
               tag == 101                                        and \
               teamId != strasbourgId:
                   shotX = event['positions'][0].get('x')
                   shotY = event['positions'][0].get('y')
                   shotCoord = [shotX, shotY]
                   concededGoalTotal = concededGoalTotal + 1
                   # print("Goal scored from " + str(shotCoord))
            # Else if the event is an own goal conceded by RCSA
            elif tag == 102 and teamId == strasbourgId:
                concededOwnGoal = concededOwnGoal + 1
                concededGoalTotal = concededGoalTotal + 1
            
            # If the event is a goal conceded by RCSA
            if tag == 101 and teamId == strasbourgId:
                # Count goals conceded by Oukidja
                if (event['playerId'] == oukidjaId):
                    concededGoalOukidja = concededGoalOukidja + 1
                    whoConcededList.append("Oukidja")
                    shotXList.append(shotX)
                    shotYList.append(shotY)
                    # print('Conceded by Oukidja')
                # Count goals conceded by Kamara
                elif (event['playerId'] == kamaraId):
                    concededGoalKamara = concededGoalKamara + 1
                    whoConcededList.append("Kamara")
                    shotXList.append(shotX)
                    shotYList.append(shotY)
                    # print('Conceded by Kamara')

# print("Goal conceded by Strasbourg : " + str(concededGoalTotal))
# print("Goal conceded by Oukidja : "    + str(concededGoalOukidja))
# print("Goal conceded by Kamara : "     + str(concededGoalKamara))  
# print("Goal conceded by Bonnefoi : "   + str(concededGoalBonnefoi))
# print("Own goal conceded : "           + str(concededOwnGoal))      

df = pd.DataFrame({"Conceded by": whoConcededList,
                   "x": shotXList,
                   "y": shotYList})

print(df)

##### DRAW THE PITCH #####

# Create the figure and set the dimensions
fig = plt.figure(figsize = (4,4), dpi = 100)
ax = plt.subplot(111)

draw_divided_pitch(ax, grids = True)
    

    






