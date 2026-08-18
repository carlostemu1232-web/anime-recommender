import argparse
import difflib
import json
import os
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_FOLDER not in sys.path:

    sys.path.insert(0, PROJECT_FOLDER)

from database.database import DATABASE_FILE


API_URL = 'https://api.jikan.moe/v4/anime'
USER_AGENT = 'anime-app-metadata-importer/0.7'
PROJECT_FOLDER = Path(__file__).resolve().parent.parent
IMAGE_FOLDER = PROJECT_FOLDER / 'database' / 'images'


def normalize_title(title):

    value = title.lower()
    value = re.sub(r'[^a-z0-9]+', ' ', value)
    return ' '.join(value.split())


def request_json(url):

    request = urllib.request.Request(
        url,
        headers={'User-Agent': USER_AGENT}
    )

    with urllib.request.urlopen(request, timeout=20) as response:

        return json.load(response)


def find_match(title):

    query = urllib.parse.urlencode({
        'q': title,
        'limit': 5
    })
    payload = request_json(f'{API_URL}?{query}')
    candidates = payload.get('data', [])

    if not candidates:

        return None

    normalized_title = normalize_title(title)
    best_candidate = None
    best_score = 0

    for candidate in candidates:

        candidate_titles = [
            candidate.get('title', ''),
            candidate.get('title_english', ''),
            candidate.get('title_japanese', '')
        ]
        candidate_score = max(
            difflib.SequenceMatcher(
                None,
                normalized_title,
                normalize_title(candidate_title)
            ).ratio()
            for candidate_title in candidate_titles
            if candidate_title
        )

        if candidate_score > best_score:

            best_score = candidate_score
            best_candidate = candidate

    if best_score < 0.72:

        return None

    return best_candidate


def download_image(anime_id, image_url):

    if not image_url:

        return None

    IMAGE_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    image_path = IMAGE_FOLDER / f'{anime_id}.jpg'
    request = urllib.request.Request(
        image_url,
        headers={'User-Agent': USER_AGENT}
    )

    with urllib.request.urlopen(request, timeout=20) as response:

        image_path.write_bytes(response.read())

    return str(
        image_path.relative_to(PROJECT_FOLDER)
    )


def update_database(anime_id, candidate, download_images):

    image_data = candidate.get('images', {}).get('jpg', {})
    image_url = (
        image_data.get('large_image_url')
        or image_data.get('image_url')
    )
    synopsis = candidate.get('synopsis')

    if download_images and image_url:

        image_url = download_image(
            anime_id,
            image_url
        )

    if not synopsis and not image_url:

        return False

    connection = sqlite3.connect(DATABASE_FILE)

    connection.execute(
        '''
        UPDATE animes
        SET synopsis = COALESCE(?, synopsis),
            image_url = COALESCE(?, image_url)
        WHERE id = ?
        ''',
        (synopsis, image_url, anime_id)
    )

    connection.commit()
    connection.close()

    return True


def enrich_metadata(delay, download_images):

    connection = sqlite3.connect(DATABASE_FILE)
    rows = connection.execute(
        'SELECT id, title FROM animes ORDER BY title'
    ).fetchall()
    connection.close()

    updated = 0
    skipped = 0
    failed = 0

    for anime_id, title in rows:

        try:

            candidate = find_match(title)

            if candidate is None:

                print(f'Skipping: {title} (no confident match)')
                skipped += 1
                continue

            if update_database(
                anime_id,
                candidate,
                download_images
            ):

                print(f'Updated: {title}')
                updated += 1

            else:

                print(f'Skipping: {title} (no metadata)')
                skipped += 1

            time.sleep(delay)

        except Exception as error:

            print(f'Failed: {title} ({error})')
            failed += 1

    print()
    print(f'Updated: {updated}')
    print(f'Skipped: {skipped}')
    print(f'Failed: {failed}')


def main():

    parser = argparse.ArgumentParser(
        description='One-time local anime metadata importer.'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.2,
        help='Seconds between requests.'
    )
    parser.add_argument(
        '--download-images',
        action='store_true',
        help='Download poster images into database/images.'
    )
    args = parser.parse_args()

    enrich_metadata(
        args.delay,
        args.download_images
    )


if __name__ == '__main__':

    main()
