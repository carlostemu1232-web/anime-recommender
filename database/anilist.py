import difflib
import html
import json
import os
import re
import threading
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path


DATABASE_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

CACHE_FILE = os.path.join(
    DATABASE_FOLDER,
    'anilist_cache.json'
)

IMAGE_FOLDER = Path(
    DATABASE_FOLDER
) / 'anilist_images'

API_URL = 'https://graphql.anilist.co'
USER_AGENT = 'Mozilla/5.0 anime-app/0.7'
TITLE_ALIASES = {
    'castlevania': 'Castlevania anime',
    'gintama': 'Gintama TV',
    'golden_kamuy': 'Golden Kamuy anime',
    'grand_blue': 'Grand Blue Dreaming',
    'grave_of_fireflies': 'Grave of the Fireflies anime'
}

_REQUEST_LOCK = threading.Lock()
_ACTIVE_REQUESTS = {}

QUERY = '''
query ($search: String) {
    Media(search: $search, type: ANIME) {
        id
        title {
            romaji
            english
            native
        }
        description(asHtml: false)
        averageScore
        startDate {
            year
        }
        episodes
        status
        coverImage {
            large
        }
        trailer {
            id
            site
            thumbnail
        }
        streamingEpisodes {
            title
            url
            thumbnail
        }
        externalLinks {
            site
            url
        }
    }
}
'''


def _load_cache():

    if not os.path.exists(CACHE_FILE):

        return {}

    try:

        with open(CACHE_FILE, 'r', encoding='utf-8') as file:

            return json.load(file)

    except (OSError, json.JSONDecodeError):

        return {}


def _save_cache(cache):

    temporary_file = f'{CACHE_FILE}.tmp'

    with open(temporary_file, 'w', encoding='utf-8') as file:

        json.dump(cache, file, ensure_ascii=False, indent=2)

    os.replace(
        temporary_file,
        CACHE_FILE
    )


def _normalize_title(title):

    value = title.lower()
    value = re.sub(r'[^a-z0-9]+', ' ', value)
    return ' '.join(value.split())


def _clean_description(description):

    if not description:

        return None

    description = html.unescape(description)
    description = re.sub(r'\s+', ' ', description).strip()
    return description or None


def _title_score(local_title, media):

    local_title = _normalize_title(local_title)
    titles = media.get('title') or {}
    candidates = [
        titles.get('romaji'),
        titles.get('english'),
        titles.get('native')
    ]

    scores = [
        difflib.SequenceMatcher(
            None,
            local_title,
            _normalize_title(candidate)
        ).ratio()
        for candidate in candidates
        if candidate
    ]

    return max(scores, default=0)


def _request_media(title):

    payload = json.dumps({
        'query': QUERY,
        'variables': {'search': title}
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

    for attempt in range(3):

        try:

            with urllib.request.urlopen(request, timeout=15) as response:

                body = json.load(response)
                break

        except urllib.error.HTTPError as error:

            if error.code != 429 or attempt == 2:

                raise

            retry_after = error.headers.get('Retry-After')

            try:

                wait = max(float(retry_after), 2.0)

            except (TypeError, ValueError):

                wait = 4.0 * (attempt + 1)

            time.sleep(wait)

    errors = body.get('errors')

    if errors:

        raise RuntimeError(
            errors[0].get('message', 'AniList request failed.')
        )

    return body.get('data', {}).get('Media')


def _to_local_media(title, media):

    if media is None or _title_score(title, media) < 0.60:

        return None

    trailer = media.get('trailer') or {}
    trailer_url = None

    if trailer.get('site') == 'youtube' and trailer.get('id'):

        trailer_url = (
            f"https://www.youtube.com/watch?v={trailer['id']}"
        )

    watch_links = []

    for episode in media.get('streamingEpisodes') or []:

        if episode.get('url'):

            watch_links.append({
                'site': episode.get('title') or 'Streaming',
                'url': episode['url']
            })

    for link in media.get('externalLinks') or []:

        if link.get('url'):

            watch_links.append({
                'site': link.get('site') or 'Service',
                'url': link['url']
            })

    return {
        'anilist_id': media.get('id'),
        'synopsis': _clean_description(media.get('description')),
        'image_url': (media.get('coverImage') or {}).get('large'),
        'trailer_url': trailer_url,
        'watch_links': watch_links,
        'source_url': (
            f"https://anilist.co/anime/{media.get('id')}"
            if media.get('id') else None
        )
    }


def get_cached_media(franchise):

    return _load_cache().get(franchise)


def get_media(
    title,
    franchise,
    alternate_title=None
):

    cache = _load_cache()

    if franchise in cache:

        media = cache[franchise]

        if media.get('image_url') and not media.get('local_image'):

            try:

                IMAGE_FOLDER.mkdir(
                    parents=True,
                    exist_ok=True
                )
                image_path = IMAGE_FOLDER / f'{franchise}.jpg'
                request = urllib.request.Request(
                    media['image_url'],
                    headers={'User-Agent': USER_AGENT}
                )

                with urllib.request.urlopen(request, timeout=20) as response:

                    image_path.write_bytes(response.read())

                media['local_image'] = str(image_path)
                cache[franchise] = media
                _save_cache(cache)

            except Exception:

                pass

        return media

    media = _to_local_media(
        title,
        _request_media(title)
    )

    if media is None and alternate_title:

        media = _to_local_media(
            alternate_title,
            _request_media(alternate_title)
        )

    if media is None:

        alias = TITLE_ALIASES.get(franchise)

        if alias:

            media = _to_local_media(
                alias,
                _request_media(alias)
            )

    if media is not None:

        image_url = media.get('image_url')

        if image_url:

            try:

                IMAGE_FOLDER.mkdir(
                    parents=True,
                    exist_ok=True
                )

                image_path = IMAGE_FOLDER / f'{franchise}.jpg'
                request = urllib.request.Request(
                    image_url,
                    headers={'User-Agent': USER_AGENT}
                )

                with urllib.request.urlopen(request, timeout=20) as response:

                    image_path.write_bytes(response.read())

                media['local_image'] = str(image_path)

            except Exception:

                media['local_image'] = None

        cache[franchise] = media
        _save_cache(cache)

    return media


def get_media_async(
    title,
    franchise,
    on_success,
    on_error,
    alternate_title=None
):

    with _REQUEST_LOCK:

        callbacks = _ACTIVE_REQUESTS.get(franchise)

        if callbacks is not None:

            callbacks.append((on_success, on_error))
            return

        _ACTIVE_REQUESTS[franchise] = [
            (on_success, on_error)
        ]

    def worker():

        try:

            media = get_media(
                title,
                franchise,
                alternate_title
            )

            with _REQUEST_LOCK:

                callbacks = _ACTIVE_REQUESTS.pop(franchise, [])

            for success_callback, _ in callbacks:

                success_callback(media)

        except Exception as error:

            with _REQUEST_LOCK:

                callbacks = _ACTIVE_REQUESTS.pop(franchise, [])

            for _, error_callback in callbacks:

                error_callback(error)

    thread = threading.Thread(
        target=worker,
        daemon=True
    )
    thread.start()
