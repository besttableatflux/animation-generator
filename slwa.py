import os
import sys
import json
import shutil
from os.path import exists, basename, splitext

import six
import requests
import pandas as pd
from whoosh.qparser import QueryParser
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


def generate_index():
    schema = Schema(
        title=TEXT(stored=True),
        image=ID(stored=True),
        description=TEXT(stored=True),
        recordNumber=TEXT(stored=True)
    )
    ix = create_in("indexdir", schema)
    writer = ix.writer()
    df = pd.read_csv(FILENAME, encoding='latin1')

    df['URLS for images'] = df['URLS for images'].str.split(';')

    for _, row in df.iterrows():
        urls = row["URLS for images"]
        if not isinstance(urls, list):
            continue

        image = get_image(urls)
        assert image

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
        query = QueryParser('title', ix.schema).parse(query)
        return list(map(dict, searcher.search(query, limit=50)))


def get_image(images):
    for image in images:
        if splitext(image)[1] == '.jpg':
            return image

    return images[0]


def main(query=sys.argv[1]):
    valid_rows = []
    for row in get_index(query):
        if 'image' not in row:
            continue
        valid_rows.append({
            'title': row['title'],
            'description': row['description'],
            'source': 'SLWA Pictorial',
            'originalImageUrl': row['image'],
            'source_url': 'http://catalogue.slwa.wa.gov.au/record={}'.format(
                row['recordNumber'][:-1]
            )
        })

    print(json.dumps(valid_rows))


if __name__ == '__main__':
    main()
