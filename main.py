import tkinter as tk
title = '🎌 Anime Recommender'
print(title)
root = tk.Tk()
root.title('🎌 Anime Recommender')
root.geometry('500x500')
label = tk.Label(root, text='🎌 Anime Recommender', font=('Arial', 24))
label.pack(pady=20)
genre_label = tk.Label(root, text='What anime genre do you like?', font=('Arial', 14))
genre_label.pack()

genre_entry = tk.Entry(root, font=('Arial', 14))
genre_entry.pack(pady=5)
episode_label = tk.Label(root, text='How many episodes?', font=('Arial', 14))
episode_label.pack(pady=10)

episode_filter = tk.StringVar(value='under')

under_button = tk.Radiobutton(root, text='Under 50 episodes', variable=episode_filter, value='under', font=('Arial', 12))
under_button.pack()

over_button = tk.Radiobutton(root, text='50+ episodes', variable=episode_filter, value='over', font=('Arial', 12))
over_button.pack()
def recommend_anime():
    genre = genre_entry.get().lower()
    if not genre:
         result_label.config(text='Please enter an anime genre.')
         return
    selected_filter = episode_filter.get()
    recommendations = get_recommendations(animes, genre, selected_filter)
    genre_found = genre_exists(animes, genre)

    result = ''

    for anime in recommendations:
        result += f"🎌 {anime['name']}\n"
        result += f"⭐ Rating: {anime['rating']}\n"
        result += f"📅 Year: {anime['year']}\n"
        result += f"🎬 Episodes: {anime['episodes']}\n"
        result += '-------------------------\n'

    if recommendations:
        result_label.config(text=result)
    elif not genre_found:
        result_label.config(text='No anime found for this genre.')
    else:
        result_label.config(text='No anime matches your episode filter.')
recommend_button = tk.Button(root, text='Recommend Anime', font=('Arial', 14), command=recommend_anime)
recommend_button.pack(pady=15)
result_label = tk.Label(root, text='', font=('Arial', 12))
result_label.pack()


def get_user_preferences():
    genre = input('What anime genre do you like? ').lower()
    episode_filter = input('Do you want under 50 or 50+ episodes? (under/over)').lower()
    while episode_filter not in ['under', 'over']:
        episode_filter = input('Do you want under 50 or 50+ episodes? (under/over)').lower()
    return genre, episode_filter

def ask_to_continue():
    while True:
        continue_choice = input('Do you want to continue? (yes/no): ').lower()
        if continue_choice in ['yes', 'no']:
            return continue_choice == 'yes'
        print('Invalid input. Please enter "yes" or "no".')
def run_search():
    genre, episode_filter = get_user_preferences()

    recommendations = get_recommendations(animes, genre, episode_filter)
    genre_found = genre_exists(animes, genre)

    for anime in recommendations:
        show_anime(anime)

    if not genre_found:
        print('No anime found for this genre.')
    elif not recommendations:
        print('No anime matches your episode filter.')


anime1 = {'name':'One Punch Man', 'genres':['action','comedy','superhero'], 'duration':'24 episodes', 'rating':8.4, 'year':2015, 'episodes':24}
anime2 = {'name':'Death Note', 'genres':['thriller','mystery','psychological'], 'duration':'37 episodes', 'rating':8.6, 'year':2006, 'episodes':37}
anime3 = {'name':'Attack on Titan', 'genres':['action', 'drama', 'fantasy'], 'duration':'89 episodes', 'rating':9.1, 'year':2013, 'episodes':89}


animes = [anime1,anime2,anime3]







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
    return sorted(recommendations, key=lambda anime: anime['rating'], reverse=True)
def genre_exists(animes, genre):
    for anime in animes:
        if genre in anime['genres']:
            return True
    return False

root.mainloop()