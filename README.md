# dart_elo
Python script to create elo ratings for my dart league

# files

## elo.py
- driver file to either update ratings or provide a preview for upcoming matches
- arguments to be passed are: league (in case players compete against multiple peer groups), k value (I've used 20 so that evenly matched games result in +/- 10 points), and date for latest game

## data_prep.py
- parse arguments, loads and prepares historical match/player data

## scoring.py
- handles the mechanics of scoring games (calculating team ELOs, match expected values, preparing the match dataframe,
  updating the player ratings, and writing out new player ratings)

## plotting.py
- I've also added a preview mode, which shows upcoming matches with projected win probabilities as well as the latest ratings in a bokeh visualization (adding a line chart for ratings over time is a planned enhancement)

## matches
- captures game, date, player, and result data

## players
- player ratings with effective dates for each match date

## players_backup
- I create a backup of the players file prior to processing
