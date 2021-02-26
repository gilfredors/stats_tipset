import os
import pandas as pd
import requests
from datetime import date
from datetime import timedelta
from time import time


REQUEST_FORMAT = 'https://api.spela.svenskaspel.se/draw/1/results/datepicker?product={product}&year={year}&' \
                 'month={month}&live=false&_={epoch_time}'

# 'https://api.spela.svenskaspel.se/draw/1/results/datepicker?product=topptipsetfamily&year=2020&month=10&live=false&_=1613988705305'

REQUEST_DICT = {
    'topptipset': 'topptipset',
    'topptipsetfamily': 'topptipsetfamily',
    'stryktipset': 'stryktipset',
    'europatipset': 'europatipset'
}

DRAW_DICT = {
    'topptipset': 'topptipset',
    'topptipsetfamily': 'topptipsetextra',
    'stryktipset': 'stryktipset',
    'europatipset': 'europatipset'
}

DRAW_RESULT_URL_FORMAT = 'https://api.spela.svenskaspel.se/multifetch?urls=/draw/1/{product}/draws/{draw_number}|' \
                         '/draw/1/{product}/draws/forecast/{draw_number}|/draw/1/{product}/draws/{draw_number}/' \
                         'result&_={epoch_time}'


# https://api.spela.svenskaspel.se/multifetch?urls=/draw/1/topptipset/draws/1495|/draw/1/topptipset/draws/forecast/1495|/draw/1/topptipset/draws/1495/result&_=1611158107609''


def generate_draws_list_request(year, month, product):
    epoch_time = round(time())
    product_key = REQUEST_DICT[product]
    return REQUEST_FORMAT.format(year=year, month=month, epoch_time=epoch_time, product=product_key)


def generate_draw_result_request(draw_number, product):
    epoch_time = round(time())
    product_key = DRAW_DICT[product]
    return DRAW_RESULT_URL_FORMAT.format(draw_number=draw_number, epoch_time=epoch_time, product=product_key)


def fetch_draws_from_interval(time_interval, product):
    request_url = generate_draws_list_request(time_interval.year, time_interval.month, product)
    response = requests.get(request_url)
    json = response.json()
    if response.status_code != 404:
        data = pd.DataFrame(json['resultDates'])
        return data


def fetch_odds_from_draw(draw_number, product):
    request_url = generate_draw_result_request(draw_number, product)
    response = requests.get(request_url)
    json = response.json()
    result = parse_odds_from_json_response(json)
    if not result:
        print(f"Not possible to parse draw {draw_number}")
        return None
    return {'odds': pd.DataFrame(result['odds'])}


def fetch_result_from_draw(draw_number, product):
    request_url = generate_draw_result_request(draw_number, product)
    response = requests.get(request_url)
    json = response.json()
    result = parse_result_from_json_response(json)
    if not result:
        print(f"Not possible to parse draw {draw_number}")
        return None
    return {'score': pd.DataFrame(result['score']),
            'money': pd.DataFrame(result['money']),
            'odds': pd.DataFrame(result['odds'])}


def parse_odds_from_json_response(json_response):
    result = {}
    for response in json_response['responses']:
        if 'draw' in response:
            draw_events = pd.json_normalize(response['draw'])['drawEvents'].iloc[0]
            result['odds'] = {
                'eventNumber': [],
                'odds.one': [],
                'svs.one': [],
                'odds.x': [],
                'svs.x': [],
                'odds.two': [],
                'svs.two': [],
                'drawNumber': [],
                'team.one': [],
                'team.two': []
            }
            for event in draw_events:
                result['odds']['eventNumber'].append(event['eventNumber'])
                result['odds']['drawNumber'].append(response['draw']['drawNumber'])
                if event['eventDescription'] is not None:
                    teams = event['eventDescription'].split(' - ')
                    result['odds']['team.one'].append(teams[0])
                    result['odds']['team.two'].append(teams[1])
                else:
                    result['odds']['team.one'].append(None)
                    result['odds']['team.two'].append(None)
                for svs, vote in event['svenskaFolket'].items():
                    result['odds'][f'svs.{svs}'].append(vote)
                if event['odds'] is not None:
                    for odd, vote in event['odds'].items():
                        result['odds'][f'odds.{odd}'].append(vote)
                else:
                    result['odds']['odds.one'].append(None)
                    result['odds']['odds.x'].append(None)
                    result['odds']['odds.two'].append(None)
            break

    return result


def parse_result_from_json_response(json_response):
    parsed = False
    result = {}
    for response in json_response['responses']:
        if 'result' in response:
            result['money'] = {
                'netSale': [response['result']['currentNetSale']],
                'closeTime': [response['result']['regCloseTime']],
                'winners': [response['result']['distribution'][0]['winners']],
                'amount': [response['result']['distribution'][0]['amount']],
                'drawNumber': [response['result']['drawNumber']],
            }
            outcomes = pd.json_normalize(response['result']['events'])[['eventNumber', 'outcome']]
            result['score'] = {
                'eventNumber': outcomes['eventNumber'],
                'outcome': outcomes['outcome'],
                'drawNumber': [response['result']['drawNumber']] * outcomes.shape[0]
            }
            parsed = True
            break
    for response in json_response['responses']:
        if 'draw' in response:
            draw_events = pd.json_normalize(response['draw'])['drawEvents'].iloc[0]
            result['odds'] = {
                'eventNumber': [],
                'odds.one': [],
                'svs.one': [],
                'odds.x': [],
                'svs.x': [],
                'odds.two': [],
                'svs.two': [],
                'drawNumber': [],
                'team.one': [],
                'team.two': []
            }
            for event in draw_events:
                result['odds']['eventNumber'].append(event['eventNumber'])
                result['odds']['drawNumber'].append(response['draw']['drawNumber'])
                if event['eventDescription'] is not None:
                    teams = event['eventDescription'].split(' - ')
                    result['odds']['team.one'].append(teams[0])
                    result['odds']['team.two'].append(teams[1])
                else:
                    result['odds']['team.one'].append(None)
                    result['odds']['team.two'].append(None)
                for svs, vote in event['svenskaFolket'].items():
                    result['odds'][f'svs.{svs}'].append(vote)
                if event['odds'] is not None:
                    for odd, vote in event['odds'].items():
                        result['odds'][f'odds.{odd}'].append(vote)
                else:
                    result['odds']['odds.one'].append(None)
                    result['odds']['odds.x'].append(None)
                    result['odds']['odds.two'].append(None)
            break

    if parsed:
        return result
    else:
        return None


def fetch_draws_list(from_date_iso, to_date_iso, product):

    time_delta = timedelta(days=31)
    time_interval = date.fromisoformat(from_date_iso)
    end_interval = date.fromisoformat(to_date_iso)
    csv_name = f'{product}_draws_from{from_date_iso.replace("-", "")}_to{to_date_iso.replace("-", "")}.csv'

    if os.path.exists(csv_name):
        return pd.read_csv(csv_name)

    fetched_stats = []

    while time_interval < end_interval:
        data = fetch_draws_from_interval(time_interval, product)
        if data is not None:
            fetched_stats.append(data)
        time_interval += time_delta

    time_interval = end_interval
    data = fetch_draws_from_interval(time_interval, product)
    if data is not None:
        fetched_stats.append(data)
    df = pd.concat(fetched_stats, ignore_index=True).drop_duplicates()
    df.to_csv(csv_name, index=False)
    return df


def get_odds_and_svf_from_draws(draws, product):
    results = []
    for _, row in draws.iterrows():
        result = fetch_odds_from_draw(row.drawNumber, product)
        if result is not None:
            results.append((result['odds']))
    return pd.concat(results, ignore_index=True)


def get_results_from_draws(draws, product):
    results_money = []
    results_score = []
    results_odds = []
    for _, row in draws.iterrows():
        result = fetch_result_from_draw(row.drawNumber, product)
        if result is not None:
            results_money.append(result['money'])
            results_score.append(result['score'])
            results_odds.append((result['odds']))
    return pd.concat(results_money, ignore_index=True), \
           pd.concat(results_score, ignore_index=True), \
           pd.concat(results_odds, ignore_index=True)
