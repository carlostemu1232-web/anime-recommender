import os
import sqlite3


PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

USER_DATA_FOLDER = os.path.join(
    PROJECT_FOLDER,
    'user_data'
)

if os.path.isdir(USER_DATA_FOLDER) or not os.path.exists(USER_DATA_FOLDER):

    FAVORITES_DATABASE = os.path.join(
        USER_DATA_FOLDER,
        'favorites.db'
    )

else:

    FAVORITES_DATABASE = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        'favorites.db'
    )


def get_connection():

    if FAVORITES_DATABASE.startswith(
        USER_DATA_FOLDER
    ):

        os.makedirs(
            USER_DATA_FOLDER,
            exist_ok=True
        )

    return sqlite3.connect(
        FAVORITES_DATABASE
    )


def create_favorites_database():

    connection = get_connection()

    connection.execute(
        '''
        CREATE TABLE IF NOT EXISTS favorites (
            anime_id INTEGER PRIMARY KEY,
            added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )

    connection.commit()
    connection.close()


def is_favorite(anime_id):

    connection = get_connection()

    result = connection.execute(
        'SELECT 1 FROM favorites WHERE anime_id = ?',
        (anime_id,)
    ).fetchone()

    connection.close()

    return result is not None


def add_favorite(anime_id):

    connection = get_connection()

    connection.execute(
        'INSERT OR IGNORE INTO favorites (anime_id) VALUES (?)',
        (anime_id,)
    )

    connection.commit()
    connection.close()


def remove_favorite(anime_id):

    connection = get_connection()

    connection.execute(
        'DELETE FROM favorites WHERE anime_id = ?',
        (anime_id,)
    )

    connection.commit()
    connection.close()


def toggle_favorite(anime_id):

    if is_favorite(anime_id):

        remove_favorite(anime_id)
        return False

    add_favorite(anime_id)
    return True


def get_favorite_ids():

    connection = get_connection()

    rows = connection.execute(
        'SELECT anime_id FROM favorites ORDER BY added_at DESC'
    ).fetchall()

    connection.close()

    return [row[0] for row in rows]
