# -*- coding: utf-8 -*-

'''Search Wikipedia articles.

Synopsis: <trigger> <filter>'''

import json
import time
from pathlib import Path
from urllib import parse, request

from albert import ClipAction, Item, UrlAction, iconLookup  # pylint: disable=import-error


__title__ = 'Wikipedia'
__version__ = '0.4.4'
__triggers__ = 'wiki '
__authors__ = 'manuelschneid3r'

ICON_PATH = iconLookup('wikipedia') or str(Path(__file__).parent / 'icons/wikipedia.svg')
BASE_URL = 'https://en.wikipedia.org/w/api.php'
USER_AGENT = 'org.albert.extension.python.wikipedia'
LIMIT = 20


def handleQuery(query):
    if not query.isTriggered:
        return None

    query.disableSort()

    # Avoid rate limiting
    time.sleep(0.1)
    if not query.isValid:
        return None

    stripped = query.string.strip()

    if not stripped:
        return Item(id=__title__, icon=ICON_PATH, text=__title__, subtext='Enter a query to search on Wikipedia')

    results = []

    params = {'action': 'opensearch', 'search': stripped, 'limit': LIMIT, 'utf8': 1, 'format': 'json'}
    get_url = f'{BASE_URL}?{parse.urlencode(params)}'
    req = request.Request(get_url, headers={'User-Agent': USER_AGENT})

    with request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))

        for i in range(0, min(LIMIT, len(data[1]))):
            title = data[1][i]
            summary = data[2][i]
            url = data[3][i]

            results.append(
                Item(
                    id=__title__,
                    icon=ICON_PATH,
                    text=title,
                    subtext=summary if summary else url,
                    completion=title,
                    actions=[UrlAction('Open article on Wikipedia', url), ClipAction('Copy URL', url)],
                )
            )

    return results
