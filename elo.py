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

from data_prep import get_args, load_files, prep_player_file
from scoring import calc_team_elo, calc_expected_values, update_team_elo, prep_match_file, update_player_elo, write_files
from plotting import prep_preview, matchup_plot, ratings_plot, launch_bokeh

# # TODO: shade out inactive players on ratings chart
# # TODO: create line chart of player ratings over time

import argparse
def main():
    # date is used only to provide a new effective date for player ratings
    league, k, date = get_args()

    # previously prompted user for inputs
    # league = input('Which league?\n')
    # k = int(input('What k value?\n'))
    # date = input('New date?\n')

    mode = input('Which Mode?\n1. Scoring\n2. Preview\n')
    player_df, match_df, preview_df, full_player_df = load_files(league)
    scoring_dict = prep_player_file(player_df)
    if mode == '2':
        preview_df = prep_preview(preview_df,scoring_dict,k,False,player_df)
        launch_bokeh(preview_df, player_df, league, full_player_df)
    elif mode == '1':
        match_df = prep_match_file(match_df,scoring_dict,k)
        scoring_dict = update_player_elo(match_df,scoring_dict,'Away')
        scoring_dict = update_player_elo(match_df,scoring_dict,'Home')
        write_files(player_df,date,scoring_dict)

main()
