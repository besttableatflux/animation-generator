from __future__ import print_function

import os
import sys
import json
import random
import argparse
import requests
from urllib.parse import urlparse
from itertools import islice, count

from lxml.html import fromstring
from lxml.etree import strip_tags

parser = argparse.ArgumentParser(description='Search Trove API')
parser.add_argument('query', metavar='Q', type=str,
                    help='search query')

args = parser.parse_args()


# Quick Trove API structure guide:
# response['response']['query'] - the query we submitted
# response['response']['zone'][0] - should be our results, we only request one zone
# response['response']['zone'][0]['records']['next'] - URL path to next page (includes &s=xx)
# response['response']['zone'][0]['records']['work'] - actual list of results ("work"?!)


class Exceeded(Exception):
    pass


def fetch(query):
    # arbitrary date for images likely to be black & white, and unlikely to be copyrighted
    # query += ' date:[1900 TO 1950]'

    for page in count(0):
        params = {
            "key": os.environ['TROVE_API_KEY'],
            "q": query,
            "zone": "picture",
            "encoding": "json"
        }

        if page > 0:
            # TODO: get page size from previous results?
            params['s'] = 20 * page

        r = requests.get('http://api.trove.nla.gov.au/result', params=params)
        if 'Quota of 100 requests per minute has been exceeded.' in r.text:
            raise Exceeded
        response = r.json()

        for result in response['response']['zone'][0]['records']['work']:


            # arbitrary score threshold, for some searches with lots of results (e.g. "dogs")
            # scores as low as 0.2 are still good, for others the threshold should be 3 or 4
            if 'relevance' not in result or float(result['relevance']['score']) < 1:
                continue

            # skip items without links
            if 'identifier' not in result:
                continue

            good_link = next(
                (
                    link['value']
                    for link in result['identifier']
                    if link['linktype'] == 'fulltext'
                ),
                ''
            )

            if urlparse(good_link).hostname == 'www.digitalpast.org':
                # expired domain
                continue

            if good_link != '':
                description = result.get('snippet')
                if description:
                    description = strip_tags(fromstring(description))
                else:
                    description = ''

                yield {
                    "title": result['title'],
                    "description": description,
                    "source": urlparse(good_link).hostname,
                    "original": good_link,
                    "colourisedImage": None
                }


def fetchAtLeast(query, count):
    return islice(fetch(query), count)


def get_images(query, sample_size=5, n=20):
    return random.sample(list(fetchAtLeast(query, n)), sample_size)


# pick off random 5? of the first 20 to meet our thresholds
for image in get_images(args.query):
    sys.stdout.write('{}\n'.format(json.dumps(image)))
