import difflib
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_FOLDER not in sys.path:

    sys.path.insert(0, PROJECT_FOLDER)

from database.anilist import API_URL, IMAGE_FOLDER, USER_AGENT
from database.database import get_all_animes_with_genres


QUERY = '''
query ($page: Int, $perPage: Int) {
    Page(page: $page, perPage: $perPage) {
        media(type: ANIME, sort: POPULARITY_DESC) {
            title { romaji english native }
            coverImage { large }
        }
    }
}
'''

CACHE_FILE = os.path.join(
    PROJECT_FOLDER,
    'database',
    'anilist_cache.json'
)


def normalize(value):

    value = value.casefold()
    value = re.sub(r'[^a-z0-9]+', ' ', value)
    return ' '.join(value.split())


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

    for attempt in range(4):

        try:

            with urllib.request.urlopen(request, timeout=30) as response:

                body = json.load(response)
                break

        except urllib.error.HTTPError as error:

            if error.code != 429 or attempt == 3:

                raise

            retry_after = error.headers.get('Retry-After')

            try:

                wait = max(float(retry_after), 10.0)

            except (TypeError, ValueError):

                wait = 20.0 * (attempt + 1)

            print(f'Rate limited. Waiting {wait:g}s...')
            time.sleep(wait)

    return body.get('data', {}).get('Page', {}).get('media', [])


def best_match(anime, media_items):

    local_titles = [
        normalize(anime['title']),
        normalize(anime.get('original_title') or '')
    ]
    best = None
    best_score = 0

    for media in media_items:

        titles = media.get('title') or {}
        remote_titles = [
            normalize(titles.get('romaji') or ''),
            normalize(titles.get('english') or ''),
            normalize(titles.get('native') or '')
        ]
        score = max(
            (
                difflib.SequenceMatcher(None, local, remote).ratio()
                for local in local_titles
                if local
                for remote in remote_titles
                if remote
            ),
            default=0
        )

        if score > best_score:

            best = media
            best_score = score

    return best if best_score >= 0.82 else None


def download_image(franchise, url):

    if not url:

        return None

    IMAGE_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )
    path = IMAGE_FOLDER / f'{franchise}.jpg'

    if path.is_file() and path.stat().st_size > 0:

        return str(path)

    request = urllib.request.Request(
        url,
        headers={'User-Agent': USER_AGENT}
    )

    with urllib.request.urlopen(request, timeout=30) as response:

        data = response.read()

    if not data:

        return None

    path.write_bytes(data)
    return str(path)


def main():

    animes = get_all_animes_with_genres()
    cache = {}

    if os.path.isfile(CACHE_FILE):

        with open(CACHE_FILE, 'r', encoding='utf-8') as file:

            cache = json.load(file)

    pending = [
        anime
        for anime in animes
        if not (
            cache.get(anime['franchise'], {}).get('local_image')
            and os.path.isfile(cache[anime['franchise']]['local_image'])
        )
    ]
    print(f'Pending images: {len(pending)}')

    pending_by_franchise = {
        anime['franchise']: anime
        for anime in pending
    }
    updated = 0

    for page in range(1, 41):

        print(f'Fetching AniList page {page}/40...')
        media_items = request_page(page)

        for franchise, anime in list(pending_by_franchise.items()):

            media = best_match(anime, media_items)

            if media is None:

                continue

            image_url = (media.get('coverImage') or {}).get('large')

            try:

                local_image = download_image(
                    franchise,
                    image_url
                )

            except Exception as error:

                print(f'Image failed: {anime["title"]}: {error}')
                continue

            if local_image:

                entry = cache.setdefault(franchise, {})
                entry['image_url'] = image_url
                entry['local_image'] = local_image
                pending_by_franchise.pop(franchise)
                updated += 1

        with open(CACHE_FILE, 'w', encoding='utf-8') as file:

            json.dump(cache, file, ensure_ascii=False, indent=2)

        print(f'Page saved. Pending: {len(pending_by_franchise)}')

        if not pending_by_franchise:

            break

        time.sleep(1.0)

    with open(CACHE_FILE, 'w', encoding='utf-8') as file:

        json.dump(cache, file, ensure_ascii=False, indent=2)

    print(f'Images updated: {updated}')


if __name__ == '__main__':

    main()
