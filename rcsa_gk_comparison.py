import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as effect
from   mplsoccer import VerticalPitch



##### FUNCTION DEFINITIONS #####

def drawDividedPitch(ax , grids = False):
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
        label = False,
        tick = False,
        goal_type='box',
        linewidth = 3,
        line_color = 'black'
    )
    pitch.draw(ax = ax)

    # Draw the divisions
    if grids:
        y_lines = [100 - 10 * x for x in range(1,10)]
        x_lines = [100 - 20 * x for x in range(1,10)]

        for i in x_lines:
            ax.plot (
                      [i, i], [0, 100], 
                      color = "lightgray", 
                      ls = "--",
                      lw = 2,
                      zorder = -1)
        for j in y_lines:
            ax.plot(
                [100, 0], [j, j],
                color = "lightgray", 
                ls = "--",
                lw = 2,
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



##### GET COORDINATES OF THE GOALS CONCEDED BY KAMARA AND OUKIDJA #####

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
                # Count goals conceded by Kamara
                elif (event['playerId'] == kamaraId):
                    concededGoalKamara = concededGoalKamara + 1
                    whoConcededList.append("Kamara")
                    shotXList.append(shotX)
                    shotYList.append(shotY)
     


##### PUT CONCEDED GOAL DATA IN A DATA FRAME #####

dfAllData = pd.DataFrame({"Conceded by": whoConcededList,
                          "x": shotXList,
                          "y": shotYList})



##### DRAW THE PITCHES #####

# Create the figure and set the dimensions
figKamara = plt.figure(figsize = (4,4), dpi = 800)
axKamara = plt.subplot(111)

figOukidja = plt.figure(figsize = (4,4), dpi = 800)
axOukidja = plt.subplot(111)

# Draw the actual pitch with divisons
drawDividedPitch(axKamara, grids = True)
drawDividedPitch(axOukidja, grids = True)



##### CREATE DATA BINS #####

# Invert x and y coordinate to match vertical pitch
dfAllData.rename(columns = {"x":"y", "y":"x"}, inplace = True)

# Create and sort data bins
x_bins = [0 + 20 * x for x in range(0,6)]
y_bins = [50 + 10 * x for x in range(0,6)]

x_bins.sort()
y_bins.sort()

# Add bins to the data frame
dfAllData["bins_x"] = pd.cut(dfAllData["x"], bins = x_bins)
dfAllData["bins_y"] = pd.cut(dfAllData["y"], bins = y_bins)



##### EXTRACT KAMARA's DATA #####

dfKamaraData = dfAllData[dfAllData["Conceded by"] == "Kamara"]

dfKamaraData =  (dfKamaraData
                     .sort_values(by = ["bins_y", "bins_x"])
                     .reset_index(drop = True))

dfKamaraZones = pd.DataFrame(dfKamaraData[['bins_x', 'bins_y']]
                                 .value_counts()).reset_index()

dfKamaraZones.columns = ['zoneX', 'zoneY', 'occurence']

dfKamaraZones = (dfKamaraZones
                    .assign(occurenceShare = lambda x : x.occurence/concededGoalKamara))

dfKamaraZones = (dfKamaraZones
                    .assign(occurenceScale = lambda x : x.occurenceShare/x.occurenceShare.max()))

counter = 0
for X, Y in zip(dfKamaraZones["zoneX"], dfKamaraZones["zoneY"]):
    # Fill zones with color gradient
    axKamara.fill_between(
        x = [X.left, X.right],
        y1 = Y.left,
        y2 = Y.right,
        color = "#38A1E4",
        alpha = dfKamaraZones["occurenceScale"].iloc[counter],
        zorder = -1,
        lw = 0)
    # Add percentage values as text in zones
    if dfKamaraZones['occurenceShare'].iloc[counter] > .02:
            text_ = axKamara.annotate(
                    xy = (X.right - (X.right - X.left)/2, Y.right - (Y.right - Y.left)/2),
                    text = f"{dfKamaraZones['occurenceShare'].iloc[counter]:.0%}",
                    ha = "center",
                    va = "center",
                    color = "black",
                    size = 5.5,
                    weight = "bold",
                    zorder = 3)
            text_.set_path_effects([effect.Stroke(linewidth=1.5, foreground="white"), effect.Normal()])
    counter += 1



#### EXTRACT OUKIDJA's DATA #####

dfOukidjaData = dfAllData[dfAllData["Conceded by"] == "Oukidja"]

dfOukidjaData = (dfOukidjaData
                     .sort_values(by = ["bins_y", "bins_x"])
                     .reset_index(drop = True))

dfOukidjaZones = pd.DataFrame(dfOukidjaData[['bins_x', 'bins_y']]
                                  .value_counts()).reset_index()

dfOukidjaZones.columns = ['zoneX', 'zoneY', 'occurence']

dfOukidjaZones = (dfOukidjaZones
                    .assign(occurenceShare = lambda x : x.occurence/concededGoalOukidja))

dfOukidjaZones = (dfOukidjaZones
                    .assign(occurenceScale = lambda x : x.occurenceShare/x.occurenceShare.max()))

counter = 0

for X, Y in zip(dfOukidjaZones["zoneX"], dfOukidjaZones["zoneY"]):
    # Fill zones with color gradient
    axOukidja.fill_between(
        x = [X.left, X.right],
        y1 = Y.left,
        y2 = Y.right,
        color = "#38A1E4",
        alpha = dfOukidjaZones["occurenceScale"].iloc[counter],
        zorder = -1,
        lw = 0)
    # Add percentage values as text in zones
    if dfOukidjaZones['occurenceShare'].iloc[counter] > .02:
        text_ = axOukidja.annotate(
                xy = (X.right - (X.right - X.left)/2, Y.right - (Y.right - Y.left)/2),
                text = f"{dfOukidjaZones['occurenceShare'].iloc[counter]:.0%}",
                ha = "center",
                va = "center",
                color = "black",
                size = 5.5,
                weight = "bold",
                zorder = 3)
        text_.set_path_effects([effect.Stroke(linewidth=1.5, foreground="white"), effect.Normal()])
    counter += 1


figKamara.set_size_inches(8, 8)
figKamara.savefig('output/Kamara.png', dpi = 800, transparent=True)
figOukidja.set_size_inches(8, 8)
figOukidja.savefig('output/Oukidja.png', dpi = 800, transparent=True)
    
    
    
    