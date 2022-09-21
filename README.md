# dart_elo
Python script to create elo ratings for my dart league

# files

## elo.py
- python script for processing updated elo ratings based on existing player ratings and match data
- will ask for inputs on league (in case players compete against multiple peer groups), k value (I've used 20 so that evenly matched games result in +/- 10 points), and date for latest game

## matches
- captures game, date, player, and result data

## players
- player ratings with effective dates for each match date

## players_backup
- I create a backup of the players file prior to processing. This one shows everyone with their initial value of 1500.
