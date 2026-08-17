title = '🎌 Anime Recommender'
print(title)
print()
genre = input('What anime genre do you like? ').lower()
episode_filter = input('Do you want under 50 or 50+ episodes? (under/over)').lower()
while episode_filter not in ['under', 'over']:
    episode_filter = input('Do you want under 50 or 50+ episodes? (under/over)').lower()
print(f'You chose:{genre}')

anime1 = {'name':'One Punch Man', 'genres':['action','comedy','superhero'], 'duration':'24 episodes', 'rating':8.4, 'year':2015, 'episodes':24}
anime2 = {'name':'Death Note', 'genres':['thriller','mystery','psychological'], 'duration':'37 episodes', 'rating':8.6, 'year':2006, 'episodes':37}
anime3 = {'name':'Attack on Titan', 'genres':['action', 'drama', 'fantasy'], 'duration':'89 episodes', 'rating':9.1, 'year':2013, 'episodes':89}


animes = [anime1,anime2,anime3]
sorted_animes = sorted(animes, key=lambda anime: anime['rating'], reverse=True)



genre_found = False
found = False


def show_anime(anime):
    print(f"🎌 {anime['name']}")
    print(f"⭐ Rating: {anime['rating']}")
    print(f"📅 Year: {anime['year']}")
    print(f"🎬 Episodes: {anime['episodes']}")
    print('-------------------------')
def matches_filters(anime, genre, episode_filter):
    matches_episode_filter = False
    if episode_filter == 'under':
        matches_episode_filter = anime['episodes'] < 50
    elif episode_filter == 'over':
        matches_episode_filter = anime['episodes'] >= 50
    return genre in anime['genres'] and matches_episode_filter
def get_recommendations(animes, genre, episode_filter):
    recommendations = []
    for anime in animes:
        if matches_filters(anime, genre, episode_filter):
            recommendations.append(anime)
    return recommendations
def genre_exists(animes, genre):
    for anime in animes:
        if genre in anime['genres']:
            return True
    return False
recommendations = get_recommendations(animes, genre, episode_filter)
genre_found = genre_exists(animes, genre)
for anime in recommendations:
    show_anime(anime)


if not genre_found:
    print('No anime found for this genre.')
elif not recommendations:
    print('No anime matches your episode filter.')