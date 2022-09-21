import pandas as pd

def load_files(league):
    # load the dataframes
    full_player_df = pd.read_csv('players.csv')
    full_match_df = pd.read_csv('matches.csv')

    # filter to most recent night
    max_date_player = full_player_df['date'].max()
    max_date_match = full_match_df['date'].max()
    match_df = full_match_df[(full_match_df['date']==max_date_match)&(full_match_df['league']==league)].copy()
    player_df = full_player_df[(full_player_df['date']==max_date_player)&(full_player_df['league']==league)].copy()

    return player_df, match_df

def prep_player_file(player_df):
    scoring_dict = dict(zip(player_df['player_id'],player_df['rating']))
    return scoring_dict

def calc_team_elo(x, scoring_dict):
    team_elo = 0
    if type(x) == int():
        for player in x.split(','):
            team_elo += scoring_dict[int(player)]
        return team_elo/len(x.split(','))
    else:
        team_elo += scoring_dict[int(x)]
        return team_elo



def calc_expected_values(x, team='Away'):
    qa = 10**(x['away_elo']/400)
    qb = 10**(x['home_elo']/400)

    ea = qa/(qa+qb)
    eb = qb/(qa+qb)

    if team == 'Away':
        return ea
    else:
        return eb

def update_team_elo(x,k,team='Away'):
    if team == 'Away':
        x['away_new'] = k * (x['away_score']-x['away_exp'])
        return x['away_new']
    else:
        x['home_new'] = k * (x['home_score']-x['home_exp'])
        return x['home_new']

def prep_match_file(match_df,scoring_dict,k):
    # calculate team elos
    match_df['away_elo'] = match_df['away_players'].apply(calc_team_elo, args=(scoring_dict,))
    match_df['home_elo'] = match_df['home_players'].apply(calc_team_elo, args=(scoring_dict,))

    # calculate expected values
    match_df['away_exp'] = match_df.apply(calc_expected_values,axis=1,args=('Away',))
    match_df['home_exp'] = match_df.apply(calc_expected_values,axis=1,args=('Home',))

    # calculate new team elos
    match_df['away_new'] = match_df.apply(update_team_elo, axis=1, args=(k,'Away'))
    match_df['home_new'] = match_df.apply(update_team_elo, axis=1, args=(k,'Home'))

    return match_df

def update_player_elo(match_df, scoring_dict, team='Away'):
    for i in range(len(match_df)):
        if team == 'Away':
            if type(match_df.iloc[i]['away_players']) != list():
                player = match_df.iloc[i]['away_players']
                scoring_dict[int(player)] += match_df.iloc[i]['away_new']
            else:
                playercount = len(match_df.iloc[i]['away_players'].split(','))
                for player in match_df.iloc[i]['away_players'].split(','):
                    scoring_share = (scoring_dict[int(player)] / (match_df.iloc[i]['away_elo']*playercount))
                    scoring_dict[int(player)] += (scoring_share * match_df.iloc[i]['away_new'])
        else:
            if type(match_df.iloc[i]['home_players']) != list():
                playercount = 1
                player = match_df.iloc[i]['home_players']
                scoring_dict[int(player)] += match_df.iloc[i]['home_new']
            else:
                playercount = len(match_df.iloc[i]['home_players'].split(','))
                for player in match_df.iloc[i]['home_players'].split(','):
                    scoring_share = (scoring_dict[int(player)] / (match_df.iloc[i]['home_elo']*playercount))
                    scoring_dict[int(player)] += (scoring_share * match_df.iloc[i]['home_new'])

    return scoring_dict

def write_files(player_df, date, scoring_dict):
    for value in scoring_dict:
        scoring_dict[value] = round(scoring_dict[value],0)
    original_df = pd.read_csv('players.csv')
    original_df.to_csv('players_backup.csv',index=False)
    new_df = player_df.copy()
    new_df.drop('rating',axis=1,inplace=True)
    new_df['date'] = date
    new_rating_df = pd.DataFrame({'player_id':scoring_dict.keys(),'rating':scoring_dict.values()})
    new_df = new_df.merge(new_rating_df,on='player_id')
    combined_df = pd.concat([original_df,new_df],axis=0)
    combined_df.to_csv('players.csv',index=False)


# TODO: need an arg parse for league name, k value, date
# TODO: sqlite database

# def main(league, k):
def main():
    league = input('Which league?\n')
    k = int(input('What k value?\n'))
    date = input('New date?\n')
    player_df, match_df = load_files(league)
    scoring_dict = prep_player_file(player_df)
    match_df = prep_match_file(match_df,scoring_dict,k)
    scoring_dict = update_player_elo(match_df,scoring_dict,'Away')
    scoring_dict = update_player_elo(match_df,scoring_dict,'Home')
    write_files(player_df,date,scoring_dict)

main()
