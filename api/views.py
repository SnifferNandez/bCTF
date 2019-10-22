import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from apps.accounts.models import Account
from apps.challenges.models import Solves, Challenge
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import datetime
import pytz
import math

TIME_CACHE = 15 # In ms

@cache_page(TIME_CACHE)
def scores(request):
    if request.method == 'GET':
        response = {}
        response['ranks'] = []

        total_points = cache.get('total_points')
        if total_points is None:
            total_points = Challenge.objects.filter(visible=True).aggregate(Sum('points'))['points__sum']
            cache.set('total_points', int(total_points), timeout=120)

        accounts_scored = cache.get('accounts_scored')
        if accounts_scored is None:
            accounts_scored = Account.objects.prefetch_related('solves').filter(points__gt=0).filter(is_active=True).order_by('-points')
            cache.set('accounts_scored', list(accounts_scored), timeout=120)

        for (rank, account) in enumerate(accounts_scored, start=1):
            team = {}
            team['id'] = account.pk
            team['name'] = account.username
            team['attendant'] = account.attendant
            team['country'] = account.country.flag_css
            team['country_name'] = account.country.name
            team['country_code'] = account.country.code
            team['points'] = account.points
            team['precentage'] = str(round((account.points * 100) / total_points if account.number_solved or total_points else 0, 2))
            team['avatar'] = account.get_avatar
            team['rank'] = rank
            response['ranks'].append(team)
        
        return JsonResponse(response)


@cache_page(TIME_CACHE)
def top_scores(request):
    if request.method == 'GET':
        response = {}
        response['ranks'] = {}
        
        if Solves.objects.count() > 0:
            for (rank, account) in enumerate(Account.objects.prefetch_related('solves').order_by('-points')[:10], start=1):
                team = {}
                team['id'] = account.pk
                team['name'] = account.username
                team['solves'] = []

                for solve in account.solves.select_related('challenge').iterator():
                    chall = {}
                    chall['chal'] = solve.challenge_id
                    chall['team'] = account.pk
                    chall['time'] = int(solve.created_at.timestamp())
                    #chall['value'] = solve.challenge.points
                    # Dynamic Score
                    # based on https://github.com/CTFd/CTFd/tree/master/CTFd/plugins/dynamic_challenges/README.md
                    min_val = 10
                    max_solv = 5
                    solved = solve.challenge.solves.count()
                    ini_pts = 1000
                    act_pts = solve.challenge.points
                    value = int(math.ceil((((min_val - ini_pts) / (max_solv ** 2)) * ((solved-1) ** 2)) + ini_pts))
                    if value < min_val:
                        value = min_val
                    # end of based formula
                    chall['value'] = value
                    team['solves'].append(chall)

                response['ranks'].update({rank: team})

            return JsonResponse(response)
        else:
            return JsonResponse(response)


@cache_page(TIME_CACHE)
def events(request):
    if request.method == 'GET':
        response = {}
        response['events'] = []

        latest_events = Solves.objects.prefetch_related('account').prefetch_related('challenge').order_by('-created_at')[:5]
        for event in latest_events:
            new_event = {}
            new_event['team'] = event.account.username
            new_event['team_id'] = event.account_id
            new_event['challenge'] = event.challenge.name
            new_event['challenge_id'] = event.challenge.id
            #new_event['time'] = event.created_at #.timestamp() #.strftime("%Y-%m-%d %H:%M")
            d = datetime.datetime.fromtimestamp(int(event.created_at.timestamp()), pytz.timezone('America/Bogota'))
            new_event['time'] = d.strftime("%Y-%m-%d %H:%M")
            response['events'].append(new_event)
        
        return JsonResponse(response)


@cache_page(TIME_CACHE)
def teams(request):
    if request.method == 'GET':
        response = {}
        response['teams'] = []
        
        teams = Account.objects.all().order_by('date_joined')
        for team in teams:
            new_team = {}
            new_team['name'] = team.username
            
            response['teams'].append(new_team)

        return JsonResponse(response)
