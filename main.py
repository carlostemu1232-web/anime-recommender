import tkinter as tk
from api_practice import load_animes, get_recommendations

title = '🎌 Anime Recommender'
print(title)

root = tk.Tk()
root.title('🎌 Anime Recommender')
root.geometry('500x500')

label = tk.Label(
    root,
    text='🎌 Anime Recommender',
    font=('Arial', 24)
)
label.pack(pady=20)

genre_label = tk.Label(
    root,
    text='What anime genre do you like?',
    font=('Arial', 14)
)
genre_label.pack()

genres = [
    'action',
    'adventure',
    'comedy',
    'drama',
    'fantasy',
    'horror',
    'mystery',
    'romance',
    'sci-fi',
    'sports'
]

genre_var = tk.StringVar(value='action')

genre_menu = tk.OptionMenu(
    root,
    genre_var,
    *genres
)
genre_menu.config(font=('Arial', 14))
genre_menu.pack()

episode_label = tk.Label(
    root,
    text='How many episodes?',
    font=('Arial', 14)
)
episode_label.pack(pady=10)

episode_filter = tk.StringVar(value='under')

under_button = tk.Radiobutton(
    root,
    text='Under 50 episodes',
    variable=episode_filter,
    value='under',
    font=('Arial', 12)
)
under_button.pack()

over_button = tk.Radiobutton(
    root,
    text='50+ episodes',
    variable=episode_filter,
    value='over',
    font=('Arial', 12)
)
over_button.pack()


def recommend_anime():
    genre = genre_var.get().lower()

    selected_filter = episode_filter.get()

    animes = load_animes(genre)

    recommendations = get_recommendations(
        animes,
        genre,
        selected_filter
    )

    result = ''

    for anime in recommendations:
        result += f"🎌 {anime['name']}\n"
        result += f"⭐ Rating: {anime['rating']}\n"
        result += f"📅 Year: {anime['year']}\n"
        result += f"🎬 Episodes: {anime['episodes']}\n"
        result += '-------------------------\n'

    if recommendations:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, result)
    else:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, 'No anime found matching your filters.')

recommend_button = tk.Button(
    root,
    text='Recommend Anime',
    font=('Arial', 14),
    command=recommend_anime
)
recommend_button.pack(pady=15)
result_frame = tk.Frame(root)
result_frame.pack(pady=10, fill='both', expand=True)

result_scrollbar = tk.Scrollbar(result_frame)
result_scrollbar.pack(side='right', fill='y')

result_text = tk.Text(
    result_frame,
    font=('Arial', 12),
    yscrollcommand=result_scrollbar.set
)
result_text.pack(side='left', fill='both', expand=True)

result_scrollbar.config(command=result_text.yview)

root.mainloop()