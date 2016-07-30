import sys
from itertools import islice
from operator import itemgetter
from os.path import exists, basename

import requests
import pandas as pd
from fuzzywuzzy.fuzz import ratio

URL = (
    'http://catalogue.beta.data.wa.gov.au/dataset/7faa2336-7601-447c-91b0-'
    '4b771ee26b6f/resource/9117bf08-bd54-4b19-89f8-ca86ae799875/download/'
    'slwapictorial.csv'
)
FILENAME = basename(URL)

if not exists(FILENAME):
    with open(FILENAME, 'wb') as fh:
        fh.write(requests.get(URL).content)


def main(query=sys.argv[1]):
    df = pd.read_csv(FILENAME, encoding='latin1')

    df['URLS for images'] = df['URLS for images'].str.split(';')

    key = lambda row: ratio(row.Title, query)

    rows = map(itemgetter(1), df.iterrows())

    rows = sorted(rows, key=key)

    rows = islice(rows, 100)

    for row in rows:
        sys.stdout.write(
            '{}\n'.format(
                row.to_json()
            )
        )

if __name__ == '__main__':
    main()
