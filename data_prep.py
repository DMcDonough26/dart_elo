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

# from scoring import prep_match_file, update_player_elo, write_files
# from plotting import prep_preview, matchup_plot, ratings_plot, launch_bokeh

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('league')
    parser.add_argument('k',type=int)
    parser.add_argument('date')
    args = parser.parse_args()
    return args.league, args.k, args.date


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
