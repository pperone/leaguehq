import requests
import operator
from datetime import date

from django.shortcuts import render
from django.template import RequestContext
from .models import League, Player, Board
from .forms import SearchForm


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
                team['name'] = teamSet['teams'][i]['teamLocation'] + ' ' + teamSet['teams'][i]['teamNickname']
                team['standing'] = teamSet['teams'][i]['overallStanding']
                team['wins'] = teamSet['teams'][i]['record']['overallWins']
                team['losses'] = teamSet['teams'][i]['record']['overallLosses']
                team['logo'] = teamSet['teams'][i]['logoUrl']
                teams.append(team)

            standings = sorted(teams, key=lambda k: k['standing'])

            return render(request, "base.html", {'leagueName': leagueName, 'leagueSize': leagueSize, 'standings': standings})

    else:
        form = SearchForm()

    return render(request, 'form.html', {'form': form})

def create_league(leagueId):
    pass
