import sqlite3
import os


# =========================
# DATABASE CONFIGURATION
# =========================

DATABASE_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE_FILE = os.path.join(
    DATABASE_FOLDER,
    'anime.db'
)


# =========================
# CREATE DATABASE
# =========================

def create_database():

    os.makedirs(
        DATABASE_FOLDER,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = connection.cursor()

    # =========================
    # ANIMES
    # =========================

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS animes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            franchise TEXT UNIQUE NOT NULL,

            title TEXT NOT NULL,

            original_title TEXT,

            synopsis TEXT,

            rating REAL,

            year INTEGER,

            episodes INTEGER,

            status TEXT,

            image_url TEXT,

            trailer_url TEXT
        )
    ''')

    # =========================
    # GENRES
    # =========================

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS genres (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE NOT NULL
        )
    ''')

    # =========================
    # ANIME GENRES
    # =========================

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anime_genres (

            anime_id INTEGER,

            genre_id INTEGER,

            PRIMARY KEY (
                anime_id,
                genre_id
            ),

            FOREIGN KEY (
                anime_id
            )
            REFERENCES animes(id)
            ON DELETE CASCADE,

            FOREIGN KEY (
                genre_id
            )
            REFERENCES genres(id)
            ON DELETE CASCADE
        )
    ''')

    connection.commit()

    connection.close()

    print(
        'Database ready.'
    )


# =========================
# GET CONNECTION
# =========================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.execute(
        'PRAGMA foreign_keys = ON'
    )

    return connection


# =========================
# ADD GENRE
# =========================

def add_genre(
    name
):

    if not name:

        return

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        '''
        INSERT OR IGNORE INTO genres (
            name
        )

        VALUES (?)
        ''',
        (
            name.lower().strip(),
        )
    )

    connection.commit()

    connection.close()


# =========================
# GET GENRE ID
# =========================

def get_genre_id(
    name
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT id
        FROM genres
        WHERE name = ?
        ''',
        (
            name.lower().strip(),
        )
    )

    result = cursor.fetchone()

    connection.close()

    if result is None:

        return None

    return result[0]


# =========================
# ADD / UPDATE ANIME
# =========================

def add_anime(
    anime
):

    franchise = (
        anime.get(
            'franchise'
        )
    )

    title = (
        anime.get(
            'title'
        )
    )

    if not franchise:

        raise ValueError(
            f'Anime "{title}" has no franchise ID.'
        )

    if not title:

        raise ValueError(
            'Anime has no title.'
        )

    connection = get_connection()

    cursor = connection.cursor()

    # =========================
    # CHECK EXISTING
    # =========================

    cursor.execute(
        '''
        SELECT id
        FROM animes
        WHERE franchise = ?
        ''',
        (
            franchise,
        )
    )

    existing = cursor.fetchone()

    # =========================
    # UPDATE
    # =========================

    if existing:

        anime_id = existing[0]

        cursor.execute(
            '''
            UPDATE animes

            SET
                title = ?,
                original_title = ?,
                synopsis = ?,
                rating = ?,
                year = ?,
                episodes = ?,
                status = ?,
                image_url = ?,
                trailer_url = ?

            WHERE id = ?
            ''',
            (
                title,
                anime.get(
                    'original_title'
                ),
                anime.get(
                    'synopsis'
                ),
                anime.get(
                    'rating'
                ),
                anime.get(
                    'year'
                ),
                anime.get(
                    'episodes'
                ),
                anime.get(
                    'status'
                ),
                anime.get(
                    'image_url'
                ),
                anime.get(
                    'trailer_url'
                ),
                anime_id
            )
        )

    # =========================
    # INSERT
    # =========================

    else:

        cursor.execute(
            '''
            INSERT INTO animes (

                franchise,
                title,
                original_title,
                synopsis,
                rating,
                year,
                episodes,
                status,
                image_url,
                trailer_url

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                franchise,
                title,
                anime.get(
                    'original_title'
                ),
                anime.get(
                    'synopsis'
                ),
                anime.get(
                    'rating'
                ),
                anime.get(
                    'year'
                ),
                anime.get(
                    'episodes'
                ),
                anime.get(
                    'status'
                ),
                anime.get(
                    'image_url'
                ),
                anime.get(
                    'trailer_url'
                )
            )
        )

        anime_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return anime_id


# =========================
# LINK ANIME TO GENRE
# =========================

def add_anime_genre(
    anime_id,
    genre_name
):

    if not genre_name:

        return

    genre_id = get_genre_id(
        genre_name
    )

    if genre_id is None:

        return

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        '''
        INSERT OR IGNORE INTO anime_genres (

            anime_id,
            genre_id

        )

        VALUES (?, ?)
        ''',
        (
            anime_id,
            genre_id
        )
    )

    connection.commit()

    connection.close()


# =========================
# CLEAR ANIME GENRES
# =========================

def clear_anime_genres(
    anime_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        '''
        DELETE FROM anime_genres
        WHERE anime_id = ?
        ''',
        (
            anime_id,
        )
    )

    connection.commit()

    connection.close()


# =========================
# GET ANIME
# =========================

def get_anime(
    anime_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT

            id,
            franchise,
            title,
            original_title,
            synopsis,
            rating,
            year,
            episodes,
            status,
            image_url,
            trailer_url

        FROM animes

        WHERE id = ?
        ''',
        (
            anime_id,
        )
    )

    anime = cursor.fetchone()

    connection.close()

    if anime is None:

        return None

    return {

        'id': anime[0],

        'franchise': anime[1],

        'title': anime[2],

        'original_title': anime[3],

        'synopsis': anime[4],

        'rating': anime[5],

        'year': anime[6],

        'episodes': anime[7],

        'status': anime[8],

        'image_url': anime[9],

        'trailer_url': anime[10]
    }


# =========================
# GET ALL ANIMES
# =========================

def get_all_animes():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT

            id,
            franchise,
            title,
            original_title,
            synopsis,
            rating,
            year,
            episodes,
            status,
            image_url,
            trailer_url

        FROM animes

        ORDER BY title
        '''
    )

    rows = cursor.fetchall()

    connection.close()

    animes = []

    for anime in rows:

        animes.append({

            'id': anime[0],

            'franchise': anime[1],

            'title': anime[2],

            'original_title': anime[3],

            'synopsis': anime[4],

            'rating': anime[5],

            'year': anime[6],

            'episodes': anime[7],

            'status': anime[8],

            'image_url': anime[9],

            'trailer_url': anime[10]
        })

    return animes


# =========================
# GET ALL ANIMES WITH GENRES
# =========================

def get_all_animes_with_genres():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT

            a.id,
            a.franchise,
            a.title,
            a.original_title,
            a.synopsis,
            a.rating,
            a.year,
            a.episodes,
            a.status,
            a.image_url,
            a.trailer_url,
            GROUP_CONCAT(g.name, '|')

        FROM animes a

        LEFT JOIN anime_genres ag
            ON a.id = ag.anime_id

        LEFT JOIN genres g
            ON ag.genre_id = g.id

        GROUP BY a.id
        ORDER BY a.title
        '''
    )

    rows = cursor.fetchall()

    connection.close()

    animes = []

    for anime in rows:

        genre_data = anime[11]

        animes.append({

            'id': anime[0],

            'franchise': anime[1],

            'title': anime[2],

            'name': anime[2],

            'original_title': anime[3],

            'synopsis': anime[4],

            'rating': anime[5],

            'year': anime[6],

            'episodes': anime[7],

            'status': anime[8],

            'image_url': anime[9],

            'trailer_url': anime[10],

            'genres': genre_data.split('|') if genre_data else [],

            'sources': 1
        })

    return animes


# =========================
# GET ANIME WITH GENRES
# =========================

def get_anime_with_genres(
    anime_id
):

    animes = get_all_animes_with_genres()

    for anime in animes:

        if anime['id'] == anime_id:

            return anime

    return None


# =========================
# SEARCH ANIMES
# =========================

def search_animes(
    query
):

    query = query.strip()

    if not query:

        return []

    animes = get_all_animes_with_genres()
    query = query.casefold()

    return [
        anime
        for anime in animes
        if query in anime.get('title', '').casefold()
        or query in (anime.get('original_title') or '').casefold()
    ]


# =========================
# FILTER ANIMES
# =========================

def get_recommendations(
    animes,
    selected_genres,
    episode_filter
):

    recommendations = []

    for anime in animes:

        anime_genres = set(
            anime.get(
                'genres',
                []
            )
        )

        genre_matches = len(
            anime_genres.intersection(
                selected_genres
            )
        )

        if genre_matches == 0:

            continue

        episodes = anime.get(
            'episodes'
        )

        if episode_filter == 'under':

            if episodes is None or episodes >= 50:

                continue

        elif episode_filter == 'over':

            if episodes is None or episodes < 50:

                continue

        anime['genre_matches'] = genre_matches

        recommendations.append(
            anime
        )

    recommendations.sort(
        key=lambda anime: (
            anime.get('genre_matches', 0),
            anime.get('rating') or 0,
            anime.get('year') or 0
        ),
        reverse=True
    )

    return recommendations


# =========================
# GET ANIMES BY GENRE
# =========================

def get_animes_by_genre(
    genre_name
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        '''
        SELECT

            a.id,
            a.franchise,
            a.title,
            a.original_title,
            a.synopsis,
            a.rating,
            a.year,
            a.episodes,
            a.status,
            a.image_url,
            a.trailer_url

        FROM animes a

        INNER JOIN anime_genres ag
            ON a.id = ag.anime_id

        INNER JOIN genres g
            ON ag.genre_id = g.id

        WHERE g.name = ?

        ORDER BY a.rating DESC
        ''',
        (
            genre_name.lower().strip(),
        )
    )

    rows = cursor.fetchall()

    connection.close()

    animes = []

    for anime in rows:

        animes.append({

            'id': anime[0],

            'franchise': anime[1],

            'title': anime[2],

            'original_title': anime[3],

            'synopsis': anime[4],

            'rating': anime[5],

            'year': anime[6],

            'episodes': anime[7],

            'status': anime[8],

            'image_url': anime[9],

            'trailer_url': anime[10]
        })

    return animes