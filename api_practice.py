import requests
genre_ids = {
    'action': 1,
    'adventure': 2,
    'comedy': 4,
    'drama': 8,
    'fantasy': 10,
    'horror': 14,
    'mystery': 7,
    'romance': 22,
    'sci-fi': 24,
    'sports': 30
}


def load_animes(genre):
    genre_id = genre_ids.get(genre)

    if genre_id is None:
        return []

    url = f'https://api.jikan.moe/v4/anime?genres={genre_id}'

    response = requests.get(url)

    if response.status_code != 200:
        print('Error connecting to Jikan.')
        return []

    data = response.json()

    animes = []

    for anime in data['data']:

        genres = []

        for genre in anime['genres']:
            genres.append(genre['name'].lower())

        anime_data = {
            'name': anime['title'],
            'genres': genres,
            'rating': anime['score'],
            'year': anime['year'],
            'episodes': anime['episodes']
        }

        animes.append(anime_data)

    return animes


def matches_filters(anime, genre, episode_filter):

    if anime['episodes'] is None:
        return False

    if episode_filter == 'under':
        matches_episode_filter = anime['episodes'] < 50

    elif episode_filter == 'over':
        matches_episode_filter = anime['episodes'] >= 50

    else:
        matches_episode_filter = False

    return genre in anime['genres'] and matches_episode_filter


def get_recommendations(animes, genre, episode_filter):

    recommendations = []

    for anime in animes:

        if matches_filters(anime, genre, episode_filter):
            recommendations.append(anime)

    return sorted(
        recommendations,
        key=lambda anime: anime['rating'],
        reverse=True
    )

