import time
import os
import sys
import argparse

PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_FOLDER not in sys.path:

    sys.path.insert(0, PROJECT_FOLDER)

from database.anilist import get_cached_media, get_media
from database.database import get_all_animes_with_genres


def enrich_catalog(delay=1.0, limit=None):

    animes = get_all_animes_with_genres()
    completed = 0
    missing = 0
    failed = 0

    processed = 0

    for index, anime in enumerate(animes, start=1):

        cached = get_cached_media(
            anime['franchise']
        ) or {}

        if cached.get('synopsis') and cached.get('local_image'):

            continue

        if limit is not None and processed >= limit:

            break

        processed += 1

        try:

            media = get_media(
                anime['title'],
                anime['franchise'],
                anime.get('original_title')
            )

            if media and media.get('synopsis') and media.get('local_image'):

                completed += 1
                print(f'[{index}/{len(animes)}] OK {anime["title"]}')

            else:

                missing += 1
                print(f'[{index}/{len(animes)}] INCOMPLETE {anime["title"]}')

        except Exception as error:

            failed += 1
            print(f'[{index}/{len(animes)}] FAILED {anime["title"]}: {error}')

        time.sleep(delay)

    print()
    print(f'Completed: {completed}')
    print(f'Incomplete: {missing}')
    print(f'Failed: {failed}')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--delay', type=float, default=1.0)
    parser.add_argument('--limit', type=int, default=None)
    args = parser.parse_args()
    enrich_catalog(args.delay, args.limit)
