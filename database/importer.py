import os
import sys


# =========================
# PROJECT PATH
# =========================

CURRENT_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_FOLDER = os.path.dirname(
    CURRENT_FOLDER
)

if PROJECT_FOLDER not in sys.path:

    sys.path.insert(
        0,
        PROJECT_FOLDER
    )


# =========================
# DATABASE
# =========================

from database.database import (
    create_database,
    add_anime,
    add_genre,
    add_anime_genre,
    clear_anime_genres,
    get_all_animes
)


# =========================
# CATALOG
# =========================

from database.catalog import (
    get_all_catalog_animes
)


# =========================
# IMPORT CATALOG
# =========================

def import_catalog():

    print()
    print(
        '============================'
    )
    print(
        'ANIME DATABASE IMPORTER'
    )
    print(
        '============================'
    )
    print()

    # =========================
    # DATABASE
    # =========================

    create_database()

    # =========================
    # CATALOG
    # =========================

    catalog = (
        get_all_catalog_animes()
    )

    print(
        f'Catalog contains: '
        f'{len(catalog)} anime(s)'
    )

    print()

    imported = 0

    # =========================
    # IMPORT
    # =========================

    for anime in catalog:

        title = anime.get(
            'title'
        )

        franchise = anime.get(
            'franchise'
        )

        if not title:

            print(
                'Skipping anime without title.'
            )

            continue

        if not franchise:

            print(
                f'Skipping {title}: '
                f'no franchise ID.'
            )

            continue

        print(
            f'Importing: {title}'
        )

        # =========================
        # ANIME
        # =========================

        anime_id = add_anime(
            anime
        )

        # =========================
        # GENRES
        # =========================

        clear_anime_genres(
            anime_id
        )

        genres = anime.get(
            'genres',
            []
        )

        for genre in genres:

            if not genre:

                continue

            add_genre(
                genre
            )

            add_anime_genre(
                anime_id,
                genre
            )

        imported += 1

    # =========================
    # RESULT
    # =========================

    print()

    print(
        '============================'
    )

    print(
        f'Imported anime: {imported}'
    )

    print(
        '============================'
    )

    print()

    database_animes = (
        get_all_animes()
    )

    print(
        'Anime database contains: '
        f'{len(database_animes)} anime(s)'
    )

    print()

    for index, anime in enumerate(
        database_animes,
        start=1
    ):

        print(
            f'{index}. '
            f'{anime["title"]}'
        )


# =========================
# START
# =========================

if __name__ == '__main__':

    import_catalog()