import requests
import time


# =========================
# CONFIGURATION
# =========================

MAX_RETRIES = 2
REQUEST_TIMEOUT = 6
RETRY_DELAY = 1

ANILIST_RESULTS = 60
JIKAN_RESULTS = 25
KITSU_RESULTS = 20


# =========================
# GENRE IDS
# =========================

JIKAN_GENRE_IDS = {

    'action': 1,
    'adventure': 2,
    'comedy': 4,
    'mystery': 7,
    'drama': 8,
    'fantasy': 10,
    'horror': 14,
    'psychological': 40,
    'romance': 22,
    'sci-fi': 24,
    'sports': 30,
    'supernatural': 37,
    'thriller': 41,
    'school': 23,
    'military': 38,
    'music': 19,
    'mecha': 18,
    'historical': 13,
    'samurai': 27,
    'parody': 20,
    'slice of life': 36,
    'shounen': 27,
    'shoujo': 25,
    'josei': 43
}


# =========================
# API REQUEST WITH RETRY
# =========================

def request_with_retry(
    method,
    url,
    **kwargs
):

    for attempt in range(
        MAX_RETRIES
    ):

        try:

            response = requests.request(
                method,
                url,
                timeout=REQUEST_TIMEOUT,
                **kwargs
            )

            if response.status_code == 200:

                return response

            print(
                f'API error: '
                f'{response.status_code} '
                f'(attempt '
                f'{attempt + 1}/'
                f'{MAX_RETRIES})'
            )

        except requests.RequestException as error:

            print(
                f'Connection error: '
                f'{error} '
                f'(attempt '
                f'{attempt + 1}/'
                f'{MAX_RETRIES})'
            )

        if attempt == 0:

            print(
                'Retrying...'
            )

            time.sleep(
                RETRY_DELAY
            )

    print(
        'API discarded after '
        f'{MAX_RETRIES} failed attempts.'
    )

    return None


# =========================
# ANILIST RATING
# =========================

def normalize_anilist_rating(
    rating
):

    if rating is None:

        return None

    return rating / 10


# =========================
# JIKAN
# =========================

def load_jikan_animes(
    search_type='trending',
    genre=None
):

    params = {
        'limit': JIKAN_RESULTS
    }

    # -------------------------
    # GENRE
    # -------------------------

    if genre:

        genre_id = JIKAN_GENRE_IDS.get(
            genre
        )

        if genre_id is not None:

            url = (
                'https://api.jikan.moe/v4/anime'
            )

            params[
                'genres'
            ] = genre_id

        else:

            url = (
                'https://api.jikan.moe/v4/anime'
            )

    # -------------------------
    # TRENDING
    # -------------------------

    elif search_type == 'trending':

        url = (
            'https://api.jikan.moe/v4/top/anime'
        )

        params[
            'filter'
        ] = 'bypopularity'

    # -------------------------
    # RECENT
    # -------------------------

    elif search_type == 'recent':

        url = (
            'https://api.jikan.moe/v4/anime'
        )

        params[
            'order_by'
        ] = 'start_date'

        params[
            'sort'
        ] = 'desc'

    # -------------------------
    # TOP
    # -------------------------

    else:

        url = (
            'https://api.jikan.moe/v4/top/anime'
        )

    response = request_with_retry(
        'GET',
        url,
        params=params
    )

    if response is None:

        print(
            'Jikan discarded.'
        )

        return []

    print(
        'Jikan Status:',
        response.status_code
    )

    data = response.json()

    animes = []

    for anime in data.get(
        'data',
        []
    ):

        genres = []

        for genre_data in anime.get(
            'genres',
            []
        ):

            genres.append(
                genre_data[
                    'name'
                ].lower()
            )

        year = anime.get(
            'year'
        )

        if year is None:

            aired = anime.get(
                'aired'
            )

            if aired:

                from_date = aired.get(
                    'from'
                )

                if from_date:

                    try:

                        year = int(
                            from_date[:4]
                        )

                    except (
                        ValueError,
                        TypeError
                    ):

                        year = None

        animes.append({

            'name': anime.get(
                'title'
            ),

            'genres': genres,

            'rating': anime.get(
                'score'
            ),

            'year': year,

            'episodes': anime.get(
                'episodes'
            )
        })

    return animes


# =========================
# KITSU
# =========================

def load_kitsu_animes(
    search_type='trending',
    genre=None
):

    url = (
        'https://kitsu.io/api/edge/anime'
    )

    params = {

        'page[limit]':
            KITSU_RESULTS
    }

    # -------------------------
    # SORT
    # -------------------------

    if search_type == 'trending':

        params[
            'sort'
        ] = '-userCount'

    elif search_type == 'recent':

        params[
            'sort'
        ] = '-startDate'

    else:

        params[
            'sort'
        ] = '-averageRating'

    # -------------------------
    # GENRE FILTER
    # -------------------------

    if genre:

        params[
            'filter[genres]'
        ] = genre

    response = request_with_retry(
        'GET',
        url,
        params=params
    )

    if response is None:

        print(
            'Kitsu discarded.'
        )

        return []

    print(
        'Kitsu Status:',
        response.status_code
    )

    data = response.json()

    animes = []

    for anime in data.get(
        'data',
        []
    ):

        attributes = anime.get(
            'attributes',
            {}
        )

        rating = attributes.get(
            'averageRating'
        )

        if rating is not None:

            try:

                rating = (
                    float(rating)
                    / 10
                )

            except (
                ValueError,
                TypeError
            ):

                rating = None

        year = None

        start_date = attributes.get(
            'startDate'
        )

        if start_date:

            try:

                year = int(
                    start_date[:4]
                )

            except (
                ValueError,
                TypeError
            ):

                year = None

        animes.append({

            'name': attributes.get(
                'canonicalTitle'
            ),

            'genres': [],

            'rating': rating,

            'year': year,

            'episodes': attributes.get(
                'episodeCount'
            )
        })

    return animes


# =========================
# ANILIST
# =========================

def load_anilist_animes(
    search_type='trending',
    genre=None
):

    url = (
        'https://graphql.anilist.co'
    )

    # -------------------------
    # SORT
    # -------------------------

    if search_type == 'trending':

        sort_type = (
            'TRENDING_DESC'
        )

    elif search_type == 'recent':

        sort_type = (
            'START_DATE_DESC'
        )

    else:

        sort_type = (
            'SCORE_DESC'
        )

    # -------------------------
    # QUERY
    # -------------------------

    query = '''
    query (
        $page: Int
        $perPage: Int
        $sort: [MediaSort!]
        $genre: String
    ) {

        Page(
            page: $page
            perPage: $perPage
        ) {

            media(
                type: ANIME
                sort: $sort
                genre: $genre
            ) {

                title {
                    romaji
                    english
                }

                genres

                averageScore

                episodes

                startDate {
                    year
                }
            }
        }
    }
    '''

    variables = {

        'page': 1,

        'perPage':
            ANILIST_RESULTS,

        'sort': [
            sort_type
        ]
    }

    if genre:

        variables[
            'genre'
        ] = genre

    response = request_with_retry(
        'POST',
        url,
        json={
            'query': query,
            'variables': variables
        }
    )

    if response is None:

        print(
            'AniList discarded.'
        )

        return []

    print(
        'AniList Status:',
        response.status_code
    )

    data = response.json()

    if 'errors' in data:

        print(
            'AniList error:',
            data['errors']
        )

        return []

    media = (
        data
        .get(
            'data',
            {}
        )
        .get(
            'Page',
            {}
        )
        .get(
            'media',
            []
        )
    )

    animes = []

    for anime in media:

        title_data = anime.get(
            'title',
            {}
        )

        title = title_data.get(
            'english'
        )

        if not title:

            title = title_data.get(
                'romaji'
            )

        genres = []

        for genre_data in anime.get(
            'genres',
            []
        ):

            genres.append(
                genre_data.lower()
            )

        start_date = anime.get(
            'startDate'
        )

        year = None

        if start_date:

            year = start_date.get(
                'year'
            )

        animes.append({

            'name': title,

            'genres': genres,

            'rating':
                normalize_anilist_rating(
                    anime.get(
                        'averageScore'
                    )
                ),

            'year': year,

            'episodes': anime.get(
                'episodes'
            )
        })

    return animes


# =========================
# NORMALIZE NAME
# =========================

def normalize_name(
    name
):

    if not name:

        return ''

    return (
        name
        .lower()
        .strip()
    )


# =========================
# FIND SAME ANIME
# =========================

def find_same_anime(
    animes
):

    grouped = {}

    for anime in animes:

        name = normalize_name(
            anime.get(
                'name'
            )
        )

        if not name:

            continue

        if name not in grouped:

            grouped[name] = []

        grouped[name].append(
            anime
        )

    return grouped


# =========================
# CALCULATE RATING
# =========================

def calculate_average_rating(
    anime_list
):

    ratings = []

    for anime in anime_list:

        rating = anime.get(
            'rating'
        )

        if rating is not None:

            ratings.append(
                rating
            )

    if not ratings:

        return None

    return (
        sum(ratings)
        / len(ratings)
    )


# =========================
# CREATE UNIFIED ANIME
# =========================

def create_unified_anime(
    anime_list
):

    average_rating = (
        calculate_average_rating(
            anime_list
        )
    )

    # =========================
    # NAME
    # =========================

    name = None

    for anime in anime_list:

        if anime.get('name'):

            name = anime['name']

            break

    # =========================
    # GENRES
    # =========================

    genres = []

    for anime in anime_list:

        for genre in anime.get(
            'genres',
            []
        ):

            if genre not in genres:

                genres.append(
                    genre
                )

    # =========================
    # YEAR
    # =========================

    year = None

    for anime in anime_list:

        if anime.get('year') is not None:

            year = anime['year']

            break

    # =========================
    # EPISODES
    # =========================

    episodes = None

    for anime in anime_list:

        if anime.get('episodes') is not None:

            episodes = anime['episodes']

            break

    # =========================
    # RETURN
    # =========================

    return {

        'name': name,

        'genres': genres,

        'rating': (
            round(
                average_rating,
                2
            )
            if average_rating is not None
            else None
        ),

        'year': year,

        'episodes': episodes,

        'sources': len(
            anime_list
        )
    }


# =========================
# LOAD ALL ANIMES
# =========================

def load_all_animes(
    search_type='trending',
    selected_genres=None
):

    print()

    print(
        '===== LOADING ANIMES ====='
    )

    # -------------------------
    # SELECT GENRE
    # -------------------------

    search_genre = None

    if selected_genres:

        search_genre = (
            selected_genres[0]
        )

        print(
            'Genre search:',
            search_genre
        )

    # -------------------------
    # LOAD APIS
    # -------------------------

    jikan_animes = (
        load_jikan_animes(
            search_type,
            search_genre
        )
    )

    kitsu_animes = (
        load_kitsu_animes(
            search_type,
            search_genre
        )
    )

    anilist_animes = (
        load_anilist_animes(
            search_type,
            search_genre
        )
    )

    # -------------------------
    # STATUS
    # -------------------------

    print()

    print(
        'Jikan animes loaded:',
        len(jikan_animes)
    )

    print(
        'Kitsu animes loaded:',
        len(kitsu_animes)
    )

    print(
        'AniList animes loaded:',
        len(anilist_animes)
    )

    active_apis = 0

    if jikan_animes:

        active_apis += 1

    if kitsu_animes:

        active_apis += 1

    if anilist_animes:

        active_apis += 1

    print(
        'Active APIs:',
        active_apis
    )

    # -------------------------
    # COMBINE
    # -------------------------

    all_animes = []

    all_animes.extend(
        jikan_animes
    )

    all_animes.extend(
        kitsu_animes
    )

    all_animes.extend(
        anilist_animes
    )

    if not all_animes:

        print(
            'No anime data available.'
        )

        return []

    # -------------------------
    # GROUP
    # -------------------------

    grouped_animes = (
        find_same_anime(
            all_animes
        )
    )

    # -------------------------
    # UNIFY
    # -------------------------

    unified_animes = []

    for name, anime_list in (
        grouped_animes.items()
    ):

        unified_anime = (
            create_unified_anime(
                anime_list
            )
        )

        unified_animes.append(
            unified_anime
        )

    # -------------------------
    # SORT
    # -------------------------

    unified_animes.sort(

        key=lambda anime: (

            anime.get(
                'rating'
            ) or 0
        ),

        reverse=True
    )

    # -------------------------
    # STATUS
    # -------------------------

    print()

    if active_apis == 3:

        print(
            'All 3 APIs are working.'
        )

    elif active_apis == 2:

        print(
            'One API failed.'
        )

        print(
            'Continuing with 2 APIs.'
        )

    elif active_apis == 1:

        print(
            'Two APIs failed.'
        )

        print(
            'Continuing with 1 API.'
        )

    else:

        print(
            'All APIs failed.'
        )

    print()

    print(
        'Unified animes:',
        len(
            unified_animes
        )
    )

    return unified_animes