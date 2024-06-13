from nba_api.stats.static import *
from nba_api.stats.endpoints import cumestatsteamgames, cumestatsteam, gamerotation, boxscoresummaryv2
import json
import time
import requests
import pandas as pd
import random
import uuid


mavericks = '1610612742'


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

def int_to_season(season: str):
    return str(season) + "-" + str(season+1)[-2:] # Convert year to season format ie. 2020 -> 2020-21

@retry
def boxscore(game_id):
    """returns a boxscore of a specific game"""
    return json.loads(boxscoresummaryv2.BoxScoreSummaryV2(game_id = game_id).get_normalized_json())

def all_regular_season_games(team_id: str, season_year: int):

    #gets all games of a specific season
    games = json.loads(cumestatsteamgames.CumeStatsTeamGames(
            league_id='00', #for NBA
            season=int_to_season(season_year),
            season_type_all_star='Regular Season',
            team_id = team_id,
        ).get_normalized_json())

    games = games['CumeStatsTeamGames']

    return games

def all_team_ids():
    all_teams = teams.get_teams()
    return [team['id'] for team in all_teams]
        

def save_game_ids_to_file(game_ids, filename='game_ids.txt'):
    with open(filename, 'w') as file:
        for game_id in game_ids:
            file.write(f"{game_id}\n")


def load_game_ids_from_file(filename='game_ids.txt'):
    with open(filename, 'r') as file:
        game_ids = [line.strip() for line in file]
    return game_ids


#@retry
def all_regular_season_game_ids(season_year: int, team_id: str = None):
    if team_id: 
        games = all_regular_season_games(team_id, season_year)
        return [game['GAME_ID'] for game in games]
    result = []
    for team in all_team_ids():
        games = all_regular_season_games(team, season_year)
        result = list(set(result + [game['GAME_ID'] for game in games]))
    return result



def analyze_boxscore(boxscore: dict):
    pass





def collect_boxscores(game_ids, output_file):
    all_games_data = {}
    for i, game_id in enumerate(game_ids):
        print('getting '+ game_id+ ' (',str(round(float((i+1)/len(game_ids)*100),5))+'%)')
        game_data = boxscore(game_id)
        all_games_data[game_id] = game_data
        
        with open(output_file, 'w') as f:
            json.dump(all_games_data, f, indent=4)
        
        
        nba_cooldown = random.gammavariate(alpha=11, beta=0.4)
        time.sleep(nba_cooldown)






if __name__ == "__main__":


    ids = load_game_ids_from_file('game_ids7.txt')

    #ids4 = load_game_ids_from_file('game_ids5.txt')
    #collect_boxscores(ids,'boxscores_'+str(uuid.uuid4())+'.json')
    #pretty_print(boxscore('0021900464'))


    w = json.load(open('box10.json'))
    x = json.load(open('box8.json'))
    y = json.load(open('box9.json'))
    z = {**w, **x, **y}
    

    with open('games.json', 'w') as f:
        json.dump(z, f, indent=4)
    




    #ids = load_game_ids_from_file('game_ids3.txt')
    #teams = all_team_ids()
    # games = json.load(open('boxscores1.json'))
    # print(len(games))
    # print(games.keys())


    # df_columns = [
    #     'GAME_ID',
    #     'HOME_TEAM_ID',
    #     'AWAY_TEAM_ID',
    #     'DATE',

    #     'WP10_H',
    #     'WP10_A',

    #     'WPR_H',
    #     'WPR_A',

    #     'PT10_H',
    #     'PT10_A',

    #     'FG10_H',
    #     'FG10_A',

    #     'T10_H',
    #     'T10_A',

    #     'HC_H',
    #     'HC_A',

    #     'W_H',
    # ]

    # df = pd.DataFrame(columns=df_columns)
    # df.loc[len(df.index)] = [

    # ] 
    # print(game['LineScore'])








