from loading import fetch_draws_list, get_results_from_draws


def format_and_save_money(results, from_date, to_date, product):
    results['amount'] = results['amount'].apply(lambda x: float(x.replace(',', '.')))
    results['netSale'] = results['netSale'].apply(lambda x: float(x.replace(',', '.')))
    results.to_csv(f'{product}_results_from{from_date.replace("-", "")}_to{to_date.replace("-", "")}.csv', index=False)
    return results


def main():
    product = 'topptipsetfamily'
    from_date = '2021-01-01'
    to_date = '2021-02-21'
    draws_list = fetch_draws_list(from_date, to_date, product)
    draws = draws_list[draws_list.drawState == 'Finalized']
    money, score, odds = get_results_from_draws(draws, product)
    money = format_and_save_money(money, from_date, to_date, product)
    score.to_csv(f'{product}_score_from{from_date.replace("-", "")}_to{to_date.replace("-", "")}.csv', index=False)
    odds.to_csv(f'{product}_odds_from{from_date.replace("-", "")}_to{to_date.replace("-", "")}.csv', index=False)

    print('Exit')


if __name__ == '__main__':
    main()
