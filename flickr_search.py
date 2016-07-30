import os
import sys
import json
from flickrapi import FlickrAPI
from lxml.html import fromstring
from itertools import islice, chain


def for_account(api, query, username, uid):
    for image in api.walk(user_id=uid, text=query):
        image = image.attrib
        title = image['title']
        photo_id = image['id']

        info = api.photos.getInfo(photo_id=photo_id)
        description = info.find('.//description').text
        description = fromstring(description)
        description = ' '.join(description.itertext())

        sizes = api.photos.getSizes(photo_id=photo_id)
        sizes = {
            size.attrib['label']: size.attrib['source']
            for size in sizes[0]
        }

        yield {
            "title": title,
            "description": description,
            "source": '{} Flickr'.format(username),
            "originalImageUrl": sizes['Large']
        }


def search(query):
    api = FlickrAPI(
        os.environ['FLICKR_API_KEY'],
        os.environ['FLICKR_SECRET']
    )

    accounts = [
        ('27331537@N06', 'State Records NSW'),
        ('32605636@N06', 'State Library Queensland')
    ]

    images = zip(
        *(
            for_account(api, query, username, uid)
            for uid, username in accounts
        )
    )
    images = chain.from_iterable(images)
    return islice(images, 20)


def main(query=sys.argv[1]):
    print(json.dumps(list(search(query))))


if __name__ == '__main__':
    main()
