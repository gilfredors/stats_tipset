import pandas as pd
from common import get_csv_file_name


def main():
    product = 'stryktipset'
    from_date = '2015-06-01'
    to_date = '2021-01-20'
    store_dir = 'data'

    score = pd.read_csv(get_csv_file_name(store_dir, 'score', product, from_date, to_date))
    odds = pd.read_csv(get_csv_file_name(store_dir, 'odds', product, from_date, to_date))
    money = pd.read_csv(get_csv_file_name(store_dir, 'results', product, from_date, to_date))

    print('Exit')


if __name__ == '__main__':
    main()