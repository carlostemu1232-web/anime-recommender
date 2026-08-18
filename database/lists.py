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

    USER_DATABASE = os.path.join(
        USER_DATA_FOLDER,
        'user.db'
    )

else:

    USER_DATABASE = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        'user.db'
    )


def get_connection():

    if USER_DATABASE.startswith(USER_DATA_FOLDER):

        os.makedirs(
            USER_DATA_FOLDER,
            exist_ok=True
        )

    return sqlite3.connect(USER_DATABASE)


def create_lists_database():

    connection = get_connection()
    connection.executescript(
        '''
        CREATE TABLE IF NOT EXISTS lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS list_animes (
            list_id INTEGER NOT NULL,
            anime_id INTEGER NOT NULL,
            added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (list_id, anime_id),
            FOREIGN KEY (list_id) REFERENCES lists(id) ON DELETE CASCADE
        );
        '''
    )
    connection.commit()
    connection.close()


def get_lists():

    connection = get_connection()
    rows = connection.execute(
        '''
        SELECT l.id, l.name, COUNT(la.anime_id)
        FROM lists l
        LEFT JOIN list_animes la ON la.list_id = l.id
        GROUP BY l.id
        ORDER BY l.name COLLATE NOCASE
        '''
    ).fetchall()
    connection.close()

    return [
        {'id': row[0], 'name': row[1], 'count': row[2]}
        for row in rows
    ]


def create_list(name):

    name = name.strip()

    if not name:

        return None

    connection = get_connection()

    try:

        cursor = connection.execute(
            'INSERT INTO lists (name) VALUES (?)',
            (name,)
        )
        connection.commit()
        return cursor.lastrowid

    except sqlite3.IntegrityError:

        return None

    finally:

        connection.close()


def rename_list(list_id, name):

    name = name.strip()

    if not name:

        return False

    connection = get_connection()

    try:

        connection.execute(
            'UPDATE lists SET name = ? WHERE id = ?',
            (name, list_id)
        )
        connection.commit()
        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


def delete_list(list_id):

    connection = get_connection()
    connection.execute(
        'DELETE FROM lists WHERE id = ?',
        (list_id,)
    )
    connection.commit()
    connection.close()


def add_anime_to_list(list_id, anime_id):

    connection = get_connection()
    connection.execute(
        'INSERT OR IGNORE INTO list_animes (list_id, anime_id) VALUES (?, ?)',
        (list_id, anime_id)
    )
    connection.commit()
    connection.close()


def remove_anime_from_list(list_id, anime_id):

    connection = get_connection()
    connection.execute(
        'DELETE FROM list_animes WHERE list_id = ? AND anime_id = ?',
        (list_id, anime_id)
    )
    connection.commit()
    connection.close()


def get_list_anime_ids(list_id):

    connection = get_connection()
    rows = connection.execute(
        'SELECT anime_id FROM list_animes WHERE list_id = ? ORDER BY added_at DESC',
        (list_id,)
    ).fetchall()
    connection.close()
    return [row[0] for row in rows]


def get_anime_lists(anime_id):

    connection = get_connection()
    rows = connection.execute(
        '''
        SELECT l.id, l.name
        FROM lists l
        JOIN list_animes la ON la.list_id = l.id
        WHERE la.anime_id = ?
        ORDER BY l.name COLLATE NOCASE
        ''',
        (anime_id,)
    ).fetchall()
    connection.close()
    return [{'id': row[0], 'name': row[1]} for row in rows]
