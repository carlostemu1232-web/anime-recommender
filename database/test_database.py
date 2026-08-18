import sys
import os


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    PROJECT_ROOT
)


from database.database import get_connection


# =========================
# TEST GENRE SEARCH
# =========================

def test_genre(
    genre
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT
            animes.title

        FROM animes

        JOIN anime_genres
            ON animes.id = anime_genres.anime_id

        JOIN genres
            ON genres.id = anime_genres.genre_id

        WHERE genres.name = ?

        ORDER BY animes.title
        ''',
        (
            genre,
        )
    )

    results = cursor.fetchall()

    connection.close()

    print()
    print(
        f'===== {genre.upper()} ====='
    )

    if not results:

        print(
            'No anime found.'
        )

        return

    for anime in results:

        print(
            f'- {anime[0]}'
        )


# =========================
# TESTS
# =========================

test_genre('isekai')

test_genre('romance')

test_genre('psychological')

test_genre('action')

test_genre('fantasy')