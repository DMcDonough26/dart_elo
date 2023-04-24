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
import argparse

from scoring import prep_match_file

from random import sample

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

def historical_plot(full_player_df):
    graph_df = pd.crosstab(full_player_df['date'],full_player_df['name'],full_player_df['rating'],aggfunc='sum')

    p = figure(title='Historical Scores', x_axis_label='Week', y_axis_label='Rating')

    color_list = ['black','blue','brown','darkgreen','darksalmon','yellow','lightgreen','lightskyblue','orange','pink','purple','red']
    keep_colors = sample(color_list,len(graph_df.columns))

    for i, player in enumerate(graph_df.columns):
        p.line(range(len(graph_df.index.values)), graph_df[player], legend_label=player, color=keep_colors[i], line_width=3)

    p.xgrid.grid_line_color = None
    p.grid.grid_line_color = None

    p.legend.location = 'top_left'

    return p

# bokeh
def launch_bokeh(preview_df, player_df, league, full_player_df):

    # player ratings
    div1 = Div(text="""<p>Current Player Ratings:</p>""",width=900,height=30)
    player_df.sort_values(by='rating',ascending=False,inplace=True)
    p0 = ratings_plot(player_df)

    # upcoming matches
    div2 = Div(text="""<p>Upcoming Matches:</p>""",width=900,height=30)
    p1 = matchup_plot(preview_df.iloc[0],player_df)
    p2 = matchup_plot(preview_df.iloc[1],player_df)
    p3 = matchup_plot(preview_df.iloc[2],player_df)

    # add code for line chart
    div3 = Div(text="""<p>Historical Ratings:</p>""",width=900,height=30)
    p4 = historical_plot(full_player_df)

    # show final
    show(Tabs(tabs=[Panel(child=layout([column(div1,p0,div2,row(p1,p2),row(p3),div3,p4)], sizing_mode='fixed'), title=league)],sizing_mode='scale_height'))
