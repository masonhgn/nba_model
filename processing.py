from nba_api.stats.static import *
from nba_api.stats.endpoints import cumestatsteamgames, cumestatsteam, gamerotation, boxscoresummaryv2
import json
import time
import requests
import pandas as pd
import random
import uuid


# Retry Wrapper 
def retry(func, retries=4):
    def retry_wrapper(*args, **kwargs):
        attempts = 0
        while attempts < retries:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                print(e)
                time.sleep(600)
                attempts += 1

    return retry_wrapper

def pretty_print(d):
    print(json.dumps(d,sort_keys=True,indent=4))

@retry
def boxscore(game_id):
    """returns a boxscore of a specific game"""
    return json.loads(boxscoresummaryv2.BoxScoreSummaryV2(game_id = game_id).get_normalized_json())


def all_team_ids():
    all_teams = teams.get_teams()
    return [team['id'] for team in all_teams]

def load_game_ids_from_file(filename='game_ids.txt'):
    with open(filename, 'r') as file:
        game_ids = [line.strip() for line in file]
    return game_ids


if __name__ == "__main__":


    teams = all_team_ids()

    records, scores = {team:[] for team in teams}, {team:[] for team in teams}
    turnovers = {team:[] for team in teams}


    ids = load_game_ids_from_file('game_ids.txt')
    #print(len(ids), len(set(ids)))

    boxscores = json.load(open('games.json'))
    #print(len(boxscores))

    df_columns = [
        'GAME_ID',
        'TEAM_ID_HOME',
        'TEAM_ID_AWAY',
        'WIN_HOME',
        'SCORE_HOME',
        'SCORE_AWAY',
        'DATE',
        'TURNOVERS_HOME',
        'TURNOVERS_AWAY',
    ]


    df = pd.DataFrame(columns=df_columns)
    for i in range(len(ids)):
        
        game = boxscores[ids[i]]
        date = game['LineScore'][0]['GAME_DATE_EST'][:10]

        #get ids of both teams
        ht_id, at_id = game['GameSummary'][0]['HOME_TEAM_ID'], game['GameSummary'][0]['VISITOR_TEAM_ID']

        #this is the index of each team in the LineScore
        h, a = (0,1) if game['LineScore'][0]['TEAM_ID'] == ht_id else (1,0)


        #calculate and store scores for both teams
        ht_score, at_score = game['LineScore'][h]['PTS'], game['LineScore'][a]['PTS']
        scores[ht_id].append(ht_score)
        scores[at_id].append(at_score)

        #calculate and score win or loss for each team
        ht_win, at_win = int(ht_score > at_score), int(ht_score < at_score)
        records[ht_id].append(ht_win)
        records[at_id].append(at_win)

        h, a = (0,1) if game['OtherStats'][0]['TEAM_ID'] == ht_id else (1,0)

        h_t, a_t = game['OtherStats'][h]['TOTAL_TURNOVERS'], game['OtherStats'][a]['TOTAL_TURNOVERS']
        turnovers[ht_id].append(h_t)
        turnovers[at_id].append(a_t)





        new_row = pd.DataFrame([{
            'GAME_ID': ids[i],  
            'TEAM_ID_HOME': ht_id,         
            'TEAM_ID_AWAY': at_id,           
            'WIN_HOME': ht_win,            
            'SCORE_HOME': ht_score,           
            'SCORE_AWAY': at_score,   
            'DATE': date,  
            'TURNOVERS_HOME': h_t,  
            'TURNOVERS_AWAY': a_t, 
        }])

        df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv('games.csv')

        

