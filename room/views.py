import requests
import operator
from datetime import date
from bs4 import BeautifulSoup

from django.shortcuts import render
from django.template import RequestContext
from .models import Board
from .forms import SearchForm
from .serializers import BoardSerializer
from rest_framework import viewsets


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

            for i in range(1, seasonsLength):
                teamId = get_winner(seasons[i], league)
                for team in teams:
                    if team['id'] == teamId:
                        team['championships'] += 1

            amountrings = []
            for team in teams:
                amountrings.append(team['championships'])

            maxrings = max(amountrings)
            minrings = min(amountrings)

            winners = []
            losers = []
            for team in teams:
                winner = {}
                if team['championships'] == maxrings:
                    winner['name'] = team['name']
                    winner['logo'] = team['logo']
                    winners.append(winner)
                loser = {}
                if team['championships'] == minrings:
                    loser['name'] = team['name']
                    loser['logo'] = team['logo']
                    losers.append(loser)

            lowest = 300
            for w in range(1, 12):
                s = requests.get('http://games.espn.com/ffl/api/v2/scoreboard',
                    params={'leagueId': league, 'seasonId': year, 'matchupPeriodId': w})
                scoreSet = s.json()

                for m in range(0, 4):
                    for t in range(0, 2):
                        score = scoreSet['scoreboard']['matchups'][m]['teams'][t]['score']
                        if score < lowest:
                            lowest = score
                            lowestWeek = w
                            lowestId = scoreSet['scoreboard']['matchups'][m]['teams'][t]['teamId']

            lower = {}
            for team in teams:
                if team['id'] == lowestId:
                    lower['name'] = team['name']
                    lower['logo'] = team['logo']
                    lower['week'] = w - 1

            return render(request, "base.html", {
                'leagueId': league,
                'leagueName': leagueName,
                'leagueSize': leagueSize,
                'standings': standings,
                'firstSeason': firstSeason,
                'winners': winners,
                'losers': losers,
                'lower': lower,
                'lowest': lowest,
                'maxrings': maxrings,
                'minrings': minrings
            })

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


# Viewsets for API endpoints
class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
