import os


def get_csv_file_name(store_dir, subname, product, from_date, to_date):
    return os.path.join(store_dir,
                        f'{product}_{subname}_from{from_date.replace("-", "")}_to{to_date.replace("-", "")}.csv')
