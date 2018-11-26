import requests
import operator
from datetime import date
from bs4 import BeautifulSoup

from django.shortcuts import render
from django.template import RequestContext
from .models import League, Player, Board
from .forms import SearchForm


# Handles request and retrieves league info to populate page
def process_league(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)

        if form.is_valid():
            league = form.cleaned_data['league']
            leagueSet = {}
            teamSet = {}
            today = date.today()

            if today.month < 8:
                year = today.year - 1
            else:
                year = today.year

            l = requests.get('http://games.espn.com/ffl/api/v2/leagueSettings',
                params={'leagueId': league,})
            leagueSet = l.json()

            # Getting League information
            leagueSize = leagueSet['leaguesettings']['size']
            leagueName = leagueSet['leaguesettings']['name']

            t = requests.get('http://games.espn.com/ffl/api/v2/teams',
                params={'leagueId': league, 'seasonId': year})
            teamSet = t.json()

            teams = []
            for i in range(leagueSize):
                team = {}
                team['id'] = teamSet['teams'][i]['teamId']
                team['name'] = teamSet['teams'][i]['teamLocation'] + ' ' + teamSet['teams'][i]['teamNickname']
                team['standing'] = teamSet['teams'][i]['overallStanding']
                team['wins'] = teamSet['teams'][i]['record']['overallWins']
                team['losses'] = teamSet['teams'][i]['record']['overallLosses']
                team['logo'] = teamSet['teams'][i]['logoUrl']
                team['championships'] = 0
                teams.append(team)

            standings = sorted(teams, key=lambda k: k['standing'])

            seasons = scrape_for_seasons(league)
            seasonsLength = len(seasons)
            firstSeason = seasons[seasonsLength - 1]

            for i in range(1, seasonsLength - 1):
                teamId = get_winner(seasons[i], league)
                print(teamId)
                #############

            return render(request, "base.html", {'leagueName': leagueName, 'leagueSize': leagueSize, 'standings': standings, 'firstSeason': firstSeason})

    else:
        form = SearchForm()

    return render(request, 'form.html', {'form': form})


# Create League and Message Board in database
def create_league(leagueId):
    pass


# Scrape ESPN Fantasy League website for seasons
def scrape_for_seasons(leagueId):
    source = requests.get('http://games.espn.com/ffl/leagueoffice', params={'leagueId': leagueId}).text

    soup = BeautifulSoup(source, 'lxml')

    select = soup.find('select', id='seasonHistoryMenu')

    options = select.find_all('option')

    seasons = []
    for option in options:
        seasons.append(option['value'])

    return seasons


# Retrieve past winners
def get_winner(season, leagueId):
    source = requests.get('http://games.espn.com/ffl/api/v2/leagueSettings', params={'leagueId': leagueId, 'seasonId': season})
    leagueSet = source.json()

    return leagueSet['leaguesettings']['finalCalculatedRanking'][0]


# Assigns past won championships to teams
def populate_championships():
    pass
