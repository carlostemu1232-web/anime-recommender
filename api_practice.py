# =========================
# ISEKAI KEYWORDS
# =========================

ISEKAI_ANIMES = [

    're:zero',
    'rezero',

    'mushoku tensei',

    'jobless reincarnation',

    'konosuba',

    'kono subarashii',

    'that time i got reincarnated as a slime',

    'tensei shitara slime datta ken',

    'overlord',

    'sword art online',

    'the rising of the shield hero',

    'tate no yuusha',

    'no game no life',

    'the eminence in shadow',

    'kage no jitsuryokusha',

    'jobless reincarnation',

    'arifureta',

    'cautious hero',

    'tsukimichi',

    'moonlit fantasy',

    'ascendance of a bookworm',

    'log horizon',

    'grimgar',

    'drifters',

    'gate',

    'problem children are coming',

    'restaurant to another world',

    'isekai quartet',

    'the saint magic power is omnipotent',

    'parallel world pharmacy',

    'black summoner',

    'uncle from another world',

    'handyman saitou in another world',

    'saving 80000 gold',

    'trapped in a dating sim',

    'villainess level 99',

    '7th time loop'

]


# =========================
# CHECK ISEKAI
# =========================

def is_isekai(anime):

    name = anime.get(
        'name',
        ''
    ).lower()

    genres = anime.get(
        'genres',
        []
    )

    # Primero comprobamos
    # el género oficial

    if 'isekai' in genres:

        return True

    # Después comprobamos
    # títulos conocidos

    for title in ISEKAI_ANIMES:

        if title in name:

            return True

    return False


# =========================
# MATCH FILTERS
# =========================

def matches_filters(
    anime,
    selected_genres,
    episode_filter
):

    anime_genres = anime.get(
        'genres',
        []
    )

    genre_matches = 0

    for genre in selected_genres:

        # =========================
        # ISEKAI
        # =========================

        if genre == 'isekai':

            if is_isekai(anime):

                genre_matches += 1

            continue

        # =========================
        # NORMAL GENRES
        # =========================

        if genre in anime_genres:

            genre_matches += 1

    # =========================
    # NO GENRE
    # =========================

    if genre_matches == 0:

        return False

    # =========================
    # EPISODES
    # =========================

    episodes = anime.get(
        'episodes'
    )

    if episodes is None:

        return False

    if episode_filter == 'under':

        if episodes >= 50:

            return False

    elif episode_filter == 'over':

        if episodes < 50:

            return False

    # =========================
    # SAVE MATCHES
    # =========================

    anime['genre_matches'] = (
        genre_matches
    )

    return True


# =========================
# GET RECOMMENDATIONS
# =========================

def get_recommendations(
    animes,
    selected_genres,
    episode_filter
):

    recommendations = []

    for anime in animes:

        if matches_filters(
            anime,
            selected_genres,
            episode_filter
        ):

            recommendations.append(
                anime
            )

    # =========================
    # SORT
    # =========================

    recommendations.sort(
        key=lambda anime: (

            anime.get(
                'genre_matches',
                0
            ),

            anime.get(
                'rating'
            ) or 0,

            anime.get(
                'year'
            ) or 0
        ),

        reverse=True
    )

    return recommendations