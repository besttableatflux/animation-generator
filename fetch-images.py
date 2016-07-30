from __future__ import print_function

import os
import random
import argparse
import requests

parser = argparse.ArgumentParser(description='Search Trove API')
parser.add_argument('query', metavar='Q', type=str,
                    help='search query')

args = parser.parse_args()


# Quick Trove API structure guide:
# response['response']['query'] - the query we submitted
# response['response']['zone'][0] - should be our results, we only request one zone
# response['response']['zone'][0]['records']['next'] - URL path to next page (includes &s=xx)
# response['response']['zone'][0]['records']['work'] - actual list of results ("work"?!)

class TroveAPI(object):
    def __init__(self, query):
        self.useful_images = []
        self.page = 0
        self.query = query

    def fetch(self):
        params = {
            "key": os.environ['TROVE_API_KEY'],
            "q": self.query,
            "zone": "picture",
            "encoding": "json"
        }

        if self.page > 0:
            # TODO: get page size from previous results?
            params['s'] = 20 * self.page

        self.page += 1

        r = requests.get('http://api.trove.nla.gov.au/result', params=params)
        response = r.json()

        for result in response['response']['zone'][0]['records']['work']:
            # arbitrary date for images likely to be black & white, and unlikely to be copyrighted
            if 'issued' not in result or result['issued'] > 1946:
                continue

            # arbitrary score threshold, for some searches with lots of results (e.g. "dogs")
            # scores as low as 0.2 are still good, for others the threshold should be 3 or 4
            if 'relevance' not in result or float(result['relevance']['score']) < 1:
                continue

            # skip items without links
            if 'identifier' not in result:
                continue

            good_link = ''
            for link in result['identifier']:
                if link['linktype'] == 'fulltext':
                    good_link = link['value']

            if good_link != '':
                self.useful_images.append(good_link)

    def fetchAtLeast(self, count):
        while len(self.useful_images) < count:
            t.fetch()

    def get_images(self):
        return random.sample(self.useful_images, 5)


t = TroveAPI(args.query)
t.fetchAtLeast(20)

# pick off random 5? of the first 20 to meet our thresholds
print(t.get_images())
