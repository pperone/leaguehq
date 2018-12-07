import requests
import operator
from datetime import date
from bs4 import BeautifulSoup

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse
from django.core import serializers
from django.conf.urls.static import static
from .models import Board
from .forms import SearchForm
from .serializers import BoardSerializer
from rest_framework import viewsets
from rest_framework.decorators import action


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
            try:
                leagueSize = leagueSet['leaguesettings']['size']
                leagueName = leagueSet['leaguesettings']['name']
            except KeyError:
                return render(index.html)

            t = requests.get('http://games.espn.com/ffl/api/v2/teams',
                params={'leagueId': league, 'seasonId': year})
            teamSet = t.json()

            teams = []
            for i in range(leagueSize):
                team = {}
                team['id'] = teamSet['teams'][i]['teamId']
                team['name'] = teamSet['teams'][i]['teamLocation'] + ' ' + teamSet['teams'][i]['teamNickname']
                team['abbrev'] = teamSet['teams'][i]['teamAbbrev']
                team['standing'] = teamSet['teams'][i]['overallStanding']
                team['wins'] = teamSet['teams'][i]['record']['overallWins']
                team['losses'] = teamSet['teams'][i]['record']['overallLosses']
                try:
                    team['logo'] = teamSet['teams'][i]['logoUrl']
                except KeyError:
                    team['logo'] = 'https://txmgv24xack1i8jje2nayxpr-wpengine.netdna-ssl.com/us/files/2015/08/FFL-Logo.png'
                team['championships'] = 0
                team['scores'] = []
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

            allmessages = get_messages(league)

            return render(request, "base.html", {
                'leagueId': league,
                'leagueName': leagueName,
                'leagueSize': leagueSize,
                'year': year,
                'standings': standings,
                'firstSeason': firstSeason,
                'winners': winners,
                'losers': losers,
                'lower': lower,
                'lowest': lowest,
                'maxrings': maxrings,
                'minrings': minrings,
                'messages': allmessages
            })

    else:
        form = SearchForm()

    return render(request, 'form.html', {'form': form})


# Load league from URI
def with_league(request, lid):
        league = lid
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
        try:
            leagueSize = leagueSet['leaguesettings']['size']
            leagueName = leagueSet['leaguesettings']['name']
        except KeyError:
            return render(index.html)

        t = requests.get('http://games.espn.com/ffl/api/v2/teams',
            params={'leagueId': league, 'seasonId': year})
        teamSet = t.json()

        teams = []
        for i in range(leagueSize):
            team = {}
            team['id'] = teamSet['teams'][i]['teamId']
            team['name'] = teamSet['teams'][i]['teamLocation'] + ' ' + teamSet['teams'][i]['teamNickname']
            team['abbrev'] = teamSet['teams'][i]['teamAbbrev']
            team['standing'] = teamSet['teams'][i]['overallStanding']
            team['wins'] = teamSet['teams'][i]['record']['overallWins']
            team['losses'] = teamSet['teams'][i]['record']['overallLosses']
            try:
                team['logo'] = teamSet['teams'][i]['logoUrl']
            except KeyError:
                team['logo'] = 'https://txmgv24xack1i8jje2nayxpr-wpengine.netdna-ssl.com/us/files/2015/08/FFL-Logo.png'
            team['championships'] = 0
            team['scores'] = []
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

        allmessages = get_messages(league)

        return render(request, "base.html", {
            'leagueId': league,
            'leagueName': leagueName,
            'leagueSize': leagueSize,
            'year': year,
            'standings': standings,
            'firstSeason': firstSeason,
            'winners': winners,
            'losers': losers,
            'lower': lower,
            'lowest': lowest,
            'maxrings': maxrings,
            'minrings': minrings,
            'messages': allmessages
        })


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


# Retrieve past winners
def get_messages(leagueId):
    qs = Board.objects.all()
    ordered = qs.order_by('-id')
    return ordered


# Viewsets for API endpoints
class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    @action(methods=['get'], detail=True)
    def queryforleague(self, request, pk):
        queryset = Board.objects.filter(leagueId=pk)
        serialized_queryset = serializers.serialize('json', queryset)
        return HttpResponse(serialized_queryset)

    @action(methods=['post'], detail=True)
    def postonleague(self, request, pk):
        name = request.POST['namefield']
        text = request.POST['textarea']
        message = Board(leagueId=pk, name=name, body=text)
        message.save()
        return HttpResponse(with_league(request, pk))
