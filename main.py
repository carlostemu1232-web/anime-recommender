import tkinter as tk
from tkinter import messagebox

from database.database import (
    create_database,
    get_all_animes,
    get_all_animes_with_genres,
    get_recommendations
)
from database.importer import import_catalog


# =========================
# CONFIGURATION
# =========================

TITLE = '🎌 Anime Recommender'

WINDOW_WIDTH = 650
WINDOW_HEIGHT = 750

GENRES = [
    '',
    'action',
    'fantasy',
    'comedy',
    'drama',
    'school',
    'adventure',
    'romance',
    'isekai',
]


# =========================
# DATABASE
# =========================

create_database()

if not get_all_animes():

    import_catalog()


# =========================
# MAIN WINDOW
# =========================

root = tk.Tk()

root.title(TITLE)

root.geometry(
    f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}'
)

root.resizable(
    False,
    False
)

root.minsize(
    600,
    650
)


# =========================
# MAIN CONTAINER
# =========================

main_frame = tk.Frame(
    root
)

main_frame.pack(
    fill='both',
    expand=True,
    padx=15,
    pady=10
)


# =========================
# TITLE
# =========================

title_label = tk.Label(
    main_frame,
    text=TITLE,
    font=('Arial', 24, 'bold')
)

title_label.pack(
    pady=10
)


# =========================
# GENRE SELECTION
# =========================

genre_label = tk.Label(
    main_frame,
    text='Select up to 3 genres:',
    font=('Arial', 14)
)

genre_label.pack(
    pady=5
)


genre_var_1 = tk.StringVar(
    value='action'
)

genre_var_2 = tk.StringVar(
    value=''
)

genre_var_3 = tk.StringVar(
    value=''
)


genre_frame = tk.Frame(
    main_frame
)

genre_frame.pack(
    pady=5
)


genre_menu_1 = tk.OptionMenu(
    genre_frame,
    genre_var_1,
    *GENRES
)

genre_menu_1.config(
    font=('Arial', 12),
    width=14
)

genre_menu_1.grid(
    row=0,
    column=0,
    padx=5
)


genre_menu_2 = tk.OptionMenu(
    genre_frame,
    genre_var_2,
    *GENRES
)

genre_menu_2.config(
    font=('Arial', 12),
    width=14
)

genre_menu_2.grid(
    row=0,
    column=1,
    padx=5
)


genre_menu_3 = tk.OptionMenu(
    genre_frame,
    genre_var_3,
    *GENRES
)

genre_menu_3.config(
    font=('Arial', 12),
    width=14
)

genre_menu_3.grid(
    row=0,
    column=2,
    padx=5
)


# =========================
# EPISODE FILTER
# =========================

episode_label = tk.Label(
    main_frame,
    text='How many episodes?',
    font=('Arial', 14)
)

episode_label.pack(
    pady=(10, 5)
)


episode_filter = tk.StringVar(
    value='all'
)


episode_frame = tk.Frame(
    main_frame
)

episode_frame.pack()


all_episodes_button = tk.Radiobutton(
    episode_frame,
    text='All episodes',
    variable=episode_filter,
    value='all',
    font=('Arial', 12)
)

all_episodes_button.grid(
    row=0,
    column=0,
    padx=10
)


under_button = tk.Radiobutton(
    episode_frame,
    text='Under 50 episodes',
    variable=episode_filter,
    value='under',
    font=('Arial', 12)
)

under_button.grid(
    row=0,
    column=1,
    padx=10
)


over_button = tk.Radiobutton(
    episode_frame,
    text='50+ episodes',
    variable=episode_filter,
    value='over',
    font=('Arial', 12)
)

over_button.grid(
    row=0,
    column=2,
    padx=10
)


# =========================
# STATUS
# =========================

status_label = tk.Label(
    main_frame,
    text='Ready',
    font=('Arial', 11)
)

status_label.pack(
    pady=5
)


# =========================
# RECOMMEND FUNCTION
# =========================

def recommend_anime():

    selected_genres = [
        genre_var_1.get(),
        genre_var_2.get(),
        genre_var_3.get()
    ]

    selected_genres = [
        genre.lower().strip()
        for genre in selected_genres
        if genre
    ]

    # =========================
    # CHECK GENRES
    # =========================

    if not selected_genres:

        messagebox.showwarning(
            'No genre',
            'Please select at least one genre.'
        )

        return

    # =========================
    # GET FILTERS
    # =========================

    selected_filter = (
        episode_filter.get()
    )

    # =========================
    # CLEAR RESULTS
    # =========================

    result_text.delete(
        '1.0',
        tk.END
    )

    status_label.config(
        text='Loading anime...'
    )

    root.update_idletasks()

    # =========================
    # LOAD LOCAL ANIMES
    # =========================

    try:

        animes = get_all_animes_with_genres()

    except Exception as error:

        status_label.config(
            text='Error loading anime.'
        )

        result_text.insert(
            tk.END,
            f'Error:\n{error}'
        )

        return

    # =========================
    # NO DATA
    # =========================

    if not animes:

        status_label.config(
            text='No anime found.'
        )

        result_text.insert(
            tk.END,
            'No anime data was found.\n\n'
            'Try another genre or episode filter.'
        )

        return

    # =========================
    # RECOMMENDATIONS
    # =========================

    recommendations = get_recommendations(
        animes,
        selected_genres,
        selected_filter
    )

    recommendations = recommendations[:10]

    # =========================
    # SHOW RESULTS
    # =========================

    if not recommendations:

        status_label.config(
            text='No matches found.'
        )

        result_text.insert(
            tk.END,
            'No anime found matching your filters.\n\n'
            'Try:\n'
            '- Another genre\n'
            '- Another episode filter'
        )

        return

    status_label.config(
        text=(
            f'{len(recommendations)} '
            f'anime recommendations found.'
        )
    )

    for index, anime in enumerate(
        recommendations,
        start=1
    ):

        name = anime.get(
            'title',
            'Unknown'
        )

        rating = anime.get(
            'rating'
        )

        year = anime.get(
            'year'
        )

        episodes = anime.get(
            'episodes'
        )

        genre_matches = anime.get(
            'genre_matches',
            0
        )

        result_text.insert(
            tk.END,
            f'{index}. 🎌 {name}\n'
        )

        if rating is not None:

            result_text.insert(
                tk.END,
                f'   ⭐ Rating: {rating}\n'
            )

        else:

            result_text.insert(
                tk.END,
                '   ⭐ Rating: N/A\n'
            )

        if year is not None:

            result_text.insert(
                tk.END,
                f'   📅 Year: {year}\n'
            )

        else:

            result_text.insert(
                tk.END,
                '   📅 Year: N/A\n'
            )

        if episodes is not None:

            result_text.insert(
                tk.END,
                f'   🎬 Episodes: {episodes}\n'
            )

        else:

            result_text.insert(
                tk.END,
                '   🎬 Episodes: N/A\n'
            )

        result_text.insert(
            tk.END,
            '   💾 Source: Local database\n'
        )

        result_text.insert(
            tk.END,
            f'   🎭 Genre matches: '
            f'{genre_matches}\n'
        )

        result_text.insert(
            tk.END,
            '\n-------------------------\n\n'
        )


# =========================
# BUTTON
# =========================

recommend_button = tk.Button(
    main_frame,
    text='🎌 Recommend Anime',
    font=('Arial', 14, 'bold'),
    command=recommend_anime,
    padx=20,
    pady=8
)

recommend_button.pack(
    pady=10
)


# =========================
# RESULTS FRAME
# =========================

result_frame = tk.Frame(
    main_frame
)

result_frame.pack(
    fill='both',
    expand=True,
    pady=5
)


# =========================
# SCROLLBAR
# =========================

result_scrollbar = tk.Scrollbar(
    result_frame
)

result_scrollbar.pack(
    side='right',
    fill='y'
)


# =========================
# RESULTS TEXT
# =========================

result_text = tk.Text(
    result_frame,
    font=('Arial', 12),
    wrap='word',
    yscrollcommand=(
        result_scrollbar.set
    )
)

result_text.pack(
    side='left',
    fill='both',
    expand=True
)


result_scrollbar.config(
    command=result_text.yview
)


# =========================
# INITIAL MESSAGE
# =========================

result_text.insert(
    tk.END,
    'Select your genres and filters,\n'
    'then press "🎌 Recommend Anime".'
)


# =========================
# START APPLICATION
# =========================

root.mainloop()