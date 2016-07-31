import os
import sys
import json
from itertools import islice

from lxml.html import fromstring
from flickrapi import FlickrAPI


SIZES = (
    'url_o', 'url_l', 'url_c', 'url_z', 'url_n',
    'url_m', 'url_q', 'url_s', 'url_t', 'url_sq'
)


def for_account(api, query, username, uid):
    for image in api.walk(user_id=uid, text=query,
                          extras='description,license,' + ','.join(SIZES)):
        meta = image.attrib
        title = meta['title']

        description = image.find('.//description')
        description = ' '.join(description.itertext())
        description = ' '.join(fromstring(description).itertext())

        image = next(
            meta[key]
            for key in SIZES
            if key in meta
        )

        yield {
            "title": title,
            "description": description,
            "source": '{} Flickr'.format(username),
            "originalImageUrl": image,
            "source_url": (
                'https://www.flickr.com/people/{user_id}/{photo_id}'
                .format(user_id=uid, photo_id=meta['id'])
            )
        }


def client(uid, username):
    print(json.dumps(list(search(sys.argv[1], uid, username))))


def search(query, uid, username):
    return islice(
        for_account(
            FlickrAPI(
                os.environ['FLICKR_API_KEY'],
                os.environ['FLICKR_SECRET']
            ),
            query,
            username,
            uid
        ),
        20
    )
