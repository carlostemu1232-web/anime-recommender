title = '🎌 Anime Recommender'
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




found = False


for anime in sorted_animes:
    matches_episode_filter = False
    if episode_filter == 'under':
        matches_episode_filter = anime['episodes'] < 50
    elif episode_filter == 'over':
        matches_episode_filter = anime['episodes'] >= 50
    if genre in anime['genres'] and matches_episode_filter:
        found = True
        print(anime['name'])
        print(f"The duration of the anime is: {anime['duration']}")
        print(f"The rating is: {anime['rating']}")
        print(f"The year is: {anime['year']}")
        print(f"The number of episodes is: {anime['episodes']}")
        print(f'Your episode filter: {episode_filter}')
        print()

if not found:
    print('No anime found matching your filters.')