from datetime import datetime
from loading import fetch_draws_list, get_odds_and_svf_from_draws
import pandas as pd


def print_odds_format(df):
    for match in ('one', 'x', 'two'):
        df[f'odds.{match}'] = df[f'odds.{match}'].apply(lambda x: x.replace(',', '.')).astype(float)
    for number, data in df.iterrows():
        print(f'Match {number + 1}: {data["team.one"]} vs {data["team.two"]} '
              f'--> 1: <{100 * 1/data["odds.one"]:.1f} | {data["svs.one"]}%>  '
              f'X: <{100 * 1/data["odds.x"]:.1f} | {data["svs.x"]}%>  '
              f'2: <{100 * 1/data["odds.two"]:.1f} | {data["svs.two"]}%>')


def main():
    product = 'topptipsetfamily'
    format_date = '%Y-%m-%d'
    today = datetime.now().strftime(format_date)
    draws_list = fetch_draws_list(today, today, product)
    draws_list['str_date'] = draws_list['date'].apply(lambda x: datetime.fromisoformat(x).strftime(format_date))
    draws = draws_list[(draws_list.drawState == 'Open')&(draws_list.str_date == today)]
    odds = get_odds_and_svf_from_draws(draws, product)
    print_odds_format(odds)
    print('Exit')


if __name__ == '__main__':
    main()
