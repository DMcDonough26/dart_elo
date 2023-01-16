import pandas as pd
from bokeh.models import ColumnDataSource, Button, AnnularWedge, ColumnDataSource, Legend, LegendItem, Plot, Range1d, LabelSet
from bokeh.models.widgets import DataTable, TableColumn, Panel, Tabs, Div, Button
from bokeh.io import output_file, show
from bokeh.layouts import column, Spacer, layout, row
from bokeh.plotting import figure, show
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from bokeh.models.annotations import Label

from collections import Counter
from math import pi

from scipy.stats import binom

def load_files(league):
    # load the dataframes
    full_player_df = pd.read_csv('players.csv')
    full_match_df = pd.read_csv('matches.csv')
    preview_df = pd.read_csv('preview.csv')

    # check data quality
    if ((full_match_df['match_id'].max()*5) == len(full_match_df)):
        pass
    else:
        print('Incorrect number of games')
        print(full_match_df['match_id'].max()*5)
        print(len(full_match_df))

    if ((full_match_df['away_score'].sum() + full_match_df['home_score'].sum()) == len(full_match_df)):
        pass
    else:
        print('Incorrect number of winners')
        print(full_match_df['away_score'].sum())
        print(full_match_df['home_score'].sum())
        print(len(full_match_df))

    full_player_df['date'] = pd.to_datetime(full_player_df['date'])
    full_match_df['date'] = pd.to_datetime(full_match_df['date'])

    # filter to most recent night
    max_date_player = full_player_df['date'].max()
    max_date_match = full_match_df['date'].max()
    match_df = full_match_df[(full_match_df['date']==max_date_match)&(full_match_df['league']==league)].copy()
    player_df = full_player_df[(full_player_df['date']==max_date_player)&(full_player_df['league']==league)].copy()

    return player_df, match_df, preview_df

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

def prep_match_file(match_df,scoring_dict,k,match=True):
    # calculate team elos
    match_df['away_elo'] = match_df['away_players'].apply(calc_team_elo, args=(scoring_dict,))
    match_df['home_elo'] = match_df['home_players'].apply(calc_team_elo, args=(scoring_dict,))

    # calculate expected values
    match_df['away_exp'] = match_df.apply(calc_expected_values,axis=1,args=('Away',))
    match_df['home_exp'] = match_df.apply(calc_expected_values,axis=1,args=('Home',))

    if match==True:
        # calculate new team elos
        match_df['away_new'] = match_df.apply(update_team_elo, axis=1, args=(k,'Away'))
        match_df['home_new'] = match_df.apply(update_team_elo, axis=1, args=(k,'Home'))

    else:
        # calculate expected values
        match_df['away_exp'] = match_df['away_exp'].round(2)
        match_df['home_exp'] = match_df['home_exp'].round(2)

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

    if combined_df['rating'].mean() == 1500:
        pass
    else:
        print('Ratings are no longer symmetrical')

    combined_df.to_csv('players.csv',index=False)

def prep_preview(preview_df,scoring_dict,k,match_mode,player_df):
    preview_df = prep_match_file(preview_df,scoring_dict,k,match_mode)
    preview_df = preview_df.merge(player_df[['player_id','name']],left_on='away_players',right_on='player_id')
    preview_df = preview_df.merge(player_df[['player_id','name']],left_on='home_players',right_on='player_id')
    preview_df = preview_df[['name_x','name_y','away_elo','home_elo','away_exp','home_exp']].copy()
    preview_df.columns = ['Away Player','Home Player','Away ELO','Home ELO','Away Win Prob','Home Win Prob']
    preview_df['Away Win Prob'] = preview_df['Away Win Prob'].apply(lambda x: 1-binom.cdf(2.5,5,x))
    preview_df['Home Win Prob'] = preview_df['Home Win Prob'].apply(lambda x: 1-binom.cdf(2.5,5,x))
    return preview_df


def matchup_plot(df,player_df):
    # Data
    # x = Counter({'Greg': 51, 'Dan': 49})
    x = Counter({df['Away Player']: df['Away Win Prob'], df['Home Player']: df['Home Win Prob']})

    data = pd.DataFrame.from_dict(dict(x), orient='index').reset_index().rename(index=str, columns={0:'Win Probability', 'index':'Player'})
    data['angle'] = data['Win Probability']/sum(x.values()) * 2*pi
    data['color'] = (Category20c[6][1],Category20c[6][5])
    data['leg_val'] = data.apply(lambda x: x['Player']+': '+str(int(round(x['Win Probability']*100,0)))+"%",axis=1)


    # # Plotting code

    player_df.reset_index(inplace=True,drop=True)

    away_rank = str(int(player_df[player_df['name']==df['Away Player']].index[0])+1)
    home_rank = str(int(player_df[player_df['name']==df['Home Player']].index[0])+1)

    titleval = ("#"+away_rank+" "+df['Away Player'] + ' vs. ' + "#"+home_rank+" "+df['Home Player'])

    p = figure(plot_height=250, plot_width=400,title=titleval, toolbar_location=None)

    p.annular_wedge(x=0, y=1, inner_radius=0.2, outer_radius=0.4,
                    start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                    line_color="white", fill_color='color', legend='leg_val', source=data)

    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None

    return p

def ratings_plot(df):
    p = figure(x_range=df['name'], height=250, width=800,toolbar_location=None, tools="")

    p.vbar(x=df['name'], top=df['rating'], width=0.9, fill_color=Category20c[10][8])

    p.xgrid.grid_line_color = None
    p.y_range.start = round(df['rating'].min(),-2)-100
    p.y_range.end = round(df['rating'].max(),-2)+100

    # p.axis.axis_label=None
    # p.axis.visible=False
    p.grid.grid_line_color = None

    source = ColumnDataSource(dict(x=df['name'],y=df['rating']))

    for i in range(len(df)):
        rating = int(df.reset_index().iloc[i]['rating'])
        label = Label(x=i, y=rating, x_offset=30, y_offset=10, text=str(rating))
        p.add_layout(label)

    return p

# bokeh
def launch_bokeh(preview_df, player_df, league):

    # player ratings
    div1 = Div(text="""<p>Current Player Ratings:</p>""",width=900,height=30)

    player_df.sort_values(by='rating',ascending=False,inplace=True)

    # c1 = [TableColumn(field=Ci, title=Ci) for Ci in player_df.columns] # bokeh columns
    # d1 = DataTable(columns=c1, source=ColumnDataSource(player_df),width=800,height=(player_df.shape[0]+1)*30) # bokeh table

    p0 = ratings_plot(player_df)

    # upcoming matches
    div2 = Div(text="""<p>Upcoming Matches:</p>""",width=900,height=30)

    # c1 = [TableColumn(field=Ci, title=Ci) for Ci in preview_df.columns] # bokeh columns
    # d1 = DataTable(columns=c1, source=ColumnDataSource(preview_df),width=800,height=(preview_df.shape[0]+1)*30) # bokeh table

    p1 = matchup_plot(preview_df.iloc[0],player_df)
    p2 = matchup_plot(preview_df.iloc[1],player_df)
    p3 = matchup_plot(preview_df.iloc[2],player_df)
    p4 = matchup_plot(preview_df.iloc[3],player_df)

    # curdoc().add_root(Tabs(tabs=[Panel(child=layout([column(button,div0,div1,d1, Spacer(width=0, height=10), div2,d2, Spacer(width=0, height=10), div3,d3)], sizing_mode='fixed'), title="NBA Scoreboard")],sizing_mode='scale_height'))
    show(Tabs(tabs=[Panel(child=layout([column(div1,p0,div2,row(p1,p2),row(p3,p4))], sizing_mode='fixed'), title=league)],sizing_mode='scale_height'))


# TODO: need an arg parse for league name, k value, date
# TODO: sqlite database

# def main(league, k):
def main():
    league = input('Which league?\n')
    k = int(input('What k value?\n'))
    # date is used only to provide a new effective date for player ratings
    date = input('New date?\n')
    mode = input('Which Mode?\n1. Scoring\n2. Preview\n')
    player_df, match_df, preview_df = load_files(league)
    scoring_dict = prep_player_file(player_df)
    match_df = prep_match_file(match_df,scoring_dict,k)
    if mode == '2':
        preview_df = prep_preview(preview_df,scoring_dict,k,False,player_df)
        # print('\nUpcoming Games:\n')
        # print(preview_df)
        # print('\nCurrent Standings:\n')
        # print(player_df.sort_values(by='rating',ascending=False))
        launch_bokeh(preview_df, player_df, league)
    elif mode == '1':
        scoring_dict = update_player_elo(match_df,scoring_dict,'Away')
        scoring_dict = update_player_elo(match_df,scoring_dict,'Home')
        write_files(player_df,date,scoring_dict)

main()
