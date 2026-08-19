import json
import os
import re
import sys
import time
import urllib.request

PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_FOLDER not in sys.path:

    sys.path.insert(0, PROJECT_FOLDER)

from database.anilist import API_URL, USER_AGENT
from database.catalog import ANIME_CATALOG


QUERY = '''
query ($page: Int, $perPage: Int) {
    Page(page: $page, perPage: $perPage) {
        media(type: ANIME, sort: POPULARITY_DESC) {
            id
            title { romaji english native }
            description(asHtml: false)
            averageScore
            startDate { year }
            episodes
            status
            genres
        }
    }
}
'''


def slugify(value):

    slug = re.sub(r'[^a-z0-9]+', '_', value.lower()).strip('_')
    return slug or 'anime'


def request_page(page):

    payload = json.dumps({
        'query': QUERY,
        'variables': {'page': page, 'perPage': 50}
    }).encode('utf-8')
    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': USER_AGENT
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:

        return json.load(response)['data']['Page']['media']


def make_record(media, used_franchises, used_titles):

    titles = media.get('title') or {}
    title = titles.get('english') or titles.get('romaji') or titles.get('native')

    if not title:

        return None

    normalized_title = title.casefold().strip()

    if normalized_title in used_titles:

        return None

    franchise = slugify(title)
    base_franchise = franchise
    suffix = 2

    while franchise in used_franchises:

        franchise = f'{base_franchise}_{suffix}'
        suffix += 1

    used_franchises.add(franchise)
    used_titles.add(normalized_title)

    year = (media.get('startDate') or {}).get('year')
    status = media.get('status')
    status_map = {
        'FINISHED': 'finished',
        'RELEASING': 'ongoing',
        'NOT_YET_RELEASED': 'upcoming',
        'CANCELLED': 'cancelled',
        'HIATUS': 'hiatus'
    }

    return {
        'franchise': franchise,
        'title': title,
        'original_title': titles.get('romaji'),
        'synopsis': None,
        'rating': (media.get('averageScore') / 10) if media.get('averageScore') else None,
        'year': year,
        'episodes': media.get('episodes'),
        'status': status_map.get(status, status.lower() if status else None),
        'image_url': None,
        'trailer_url': None,
        'genres': [genre.lower() for genre in media.get('genres') or []]
    }


def main():

    used_franchises = {anime['franchise'] for anime in ANIME_CATALOG}
    used_titles = {anime['title'].casefold().strip() for anime in ANIME_CATALOG}
    records = []
    page = 1

    while len(ANIME_CATALOG) + len(records) < 1000:

        print(f'Fetching AniList page {page}...')
        media_items = request_page(page)

        if not media_items:

            break

        for media in media_items:

            record = make_record(
                media,
                used_franchises,
                used_titles
            )

            if record:

                records.append(record)

            if len(ANIME_CATALOG) + len(records) >= 1000:

                break

        page += 1
        time.sleep(1.2)

    output = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        'catalog_extra.py'
    )

    with open(output, 'w', encoding='utf-8') as file:

        file.write('EXPANDED_CATALOG = ')
        file.write(repr(records))
        file.write('\n')

    print(f'Generated {len(records)} new anime records.')
    print(f'Catalog total after import: {len(ANIME_CATALOG) + len(records)}')


if __name__ == '__main__':

    main()
