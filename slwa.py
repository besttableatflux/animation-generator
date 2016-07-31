from __future__ import print_function

import os
import sys
import json
import shutil
from collections import defaultdict
from six.moves.urllib.parse import urlparse
from os.path import exists, basename, splitext

import six
import requests
import pandas as pd
from whoosh.qparser import MultifieldParser
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir

URL = (
    'http://catalogue.beta.data.wa.gov.au/dataset/7faa2336-7601-447c-91b0-'
    '4b771ee26b6f/resource/9117bf08-bd54-4b19-89f8-ca86ae799875/download/'
    'slwapictorial.csv'
)
FILENAME = basename(URL)

if not exists(FILENAME):
    with open(FILENAME, 'wb') as fh:
        fh.write(requests.get(URL).content)


def load_df():
    df = pd.read_csv(FILENAME, encoding='latin1')
    df['URLS for images'] = df['URLS for images'].str.split(';')
    df = df[~df['URLS for images'].isnull()]

    return df


def generate_index():
    schema = Schema(
        title=TEXT(stored=True),
        image=ID(stored=True),
        description=TEXT(stored=True),
        recordNumber=TEXT(stored=True)
    )
    ix = create_in("indexdir", schema)
    writer = ix.writer()

    for _, row in load_df().iterrows():
        urls = row["URLS for images"]

        image = get_image(urls)
        if not image:
            continue

        description = row.Summary
        if pd.isnull(description):
            description = ''

        writer.add_document(
            title=six.text_type(row.Title),
            image=six.text_type(image),
            description=six.text_type(description),
            recordNumber=six.text_type(row['Bibliographic Record number'])
        )

    writer.commit()

    return ix


def get_index(query):
    if exists('indexdir'):
        ix = open_dir('indexdir')
    else:
        os.mkdir('indexdir')
        try:
            ix = generate_index()
        except Exception:
            shutil.rmtree('indexdir', ignore_errors=True)
            raise

    with ix.searcher() as searcher:
        query = MultifieldParser(
            ['title', 'description'],
            ix.schema
        ).parse(query)
        return list(map(dict, searcher.search(query, limit=50)))


def get_image(images):

    exts = defaultdict(list)

    for image in images:
        ext = splitext(image)[1]

        if urlparse(image).hostname == 'purl.slwa.wa.gov.au' and ext == '':
            continue

        exts[ext].append(image)

    if '.jpg' in exts:
        return exts['.jpg'][0]

    if '.png' in exts:
        return exts['.png'][0]

    for key in exts:
        return exts[key][0]

    return None


def main(query=sys.argv[1]):
    valid_rows = [
        {
            'title': row['title'],
            'description': row['description'],
            'source': 'SLWA Pictorial',
            'originalImageUrl': row['image'],
            'source_url': 'http://catalogue.slwa.wa.gov.au/record={}'.format(
                row['recordNumber'][:-1]
                # last digit is check digit
            )
        }
        for row in get_index(query)
        if 'image' in row
    ]

    print(json.dumps(valid_rows))


if __name__ == '__main__':
    main()
