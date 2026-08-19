import json
import os
from functools import partial

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import DictProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager

APP_TITLE = "AniVerse Mobile"
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalog.json")

KV = '''
#:import dp kivy.metrics.dp

<AnimeListScreen>:
    name: "list"
    BoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(8)

        Label:
            text: app.title
            size_hint_y: None
            height: dp(42)
            bold: True
            color: 0.95, 0.97, 1, 1

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(6)

            TextInput:
                id: query
                hint_text: "Search title"
                multiline: False
                on_text_validate: root.apply_filters()

            Spinner:
                id: genre
                text: "all genres"
                values: root.genre_values

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(6)

            Spinner:
                id: min_rating
                text: "any rating"
                values: ["any rating", "7+", "8+", "9+"]

            Spinner:
                id: episodes
                text: "all episodes"
                values: ["all episodes", "under 24", "24+"]

            Button:
                text: "Search"
                on_release: root.apply_filters()

        Label:
            id: count_label
            text: "0 results"
            size_hint_y: None
            height: dp(26)
            color: 0.7, 0.78, 0.9, 1

        ScrollView:
            do_scroll_x: False
            GridLayout:
                id: list_box
                cols: 1
                spacing: dp(6)
                size_hint_y: None
                height: self.minimum_height

<AnimeDetailScreen>:
    name: "detail"
    BoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(8)

        BoxLayout:
            size_hint_y: None
            height: dp(42)
            spacing: dp(8)

            Button:
                text: "Back"
                size_hint_x: None
                width: dp(90)
                on_release: root.go_back()

            Label:
                text: root.title_text
                bold: True
                halign: "left"
                valign: "middle"
                text_size: self.size

        Label:
            text: root.meta_text
            size_hint_y: None
            height: dp(70)
            halign: "left"
            valign: "top"
            text_size: self.size

        Label:
            text: root.synopsis_text
            halign: "left"
            valign: "top"
            text_size: self.size
'''


class AnimeListScreen(Screen):
    all_items = ListProperty([])
    filtered_items = ListProperty([])
    genre_values = ListProperty(["all genres"])

    def on_pre_enter(self):
        if not self.all_items:
            app = App.get_running_app()
            self.all_items = app.catalog
            genres = sorted({g for item in self.all_items for g in item.get("genres", []) if g})
            self.genre_values = ["all genres"] + genres
            self.apply_filters()

    def apply_filters(self):
        query = self.ids.query.text.strip().casefold()
        genre = self.ids.genre.text.strip().casefold()
        min_rating_token = self.ids.min_rating.text.strip().lower()
        episodes_token = self.ids.episodes.text.strip().lower()

        min_rating = 0.0
        if min_rating_token.startswith("7"):
            min_rating = 7.0
        elif min_rating_token.startswith("8"):
            min_rating = 8.0
        elif min_rating_token.startswith("9"):
            min_rating = 9.0

        output = []
        for item in self.all_items:
            title = (item.get("title") or "").casefold()
            original = (item.get("original_title") or "").casefold()
            genres = [g.casefold() for g in item.get("genres", [])]
            rating = float(item.get("rating") or 0.0)
            episodes = item.get("episodes")

            if query and query not in title and query not in original:
                continue
            if genre != "all genres" and genre not in genres:
                continue
            if rating < min_rating:
                continue
            if episodes_token == "under 24":
                if episodes is None or episodes >= 24:
                    continue
            elif episodes_token == "24+":
                if episodes is None or episodes < 24:
                    continue
            output.append(item)

        output.sort(key=lambda it: ((it.get("rating") or 0), (it.get("year") or 0)), reverse=True)
        self.filtered_items = output[:250]
        self.ids.count_label.text = f"{len(output)} results ({len(self.filtered_items)} shown)"
        self._render_list()

    def _render_list(self):
        box = self.ids.list_box
        box.clear_widgets()

        for item in self.filtered_items:
            title = item.get("title") or "Unknown"
            rating = item.get("rating")
            year = item.get("year")
            episodes = item.get("episodes")
            subtitle = f"rating {rating or '-'} | year {year or '-'} | eps {episodes if episodes is not None else '-'}"

            btn = Button(
                text=f"{title}\n{subtitle}",
                size_hint_y=None,
                height=84,
                halign="left",
                valign="middle"
            )
            btn.text_size = (btn.width - 24, None)
            btn.bind(size=lambda instance, _: setattr(instance, "text_size", (instance.width - 24, None)))
            btn.bind(on_release=partial(self._open_detail, item))
            box.add_widget(btn)

    def _open_detail(self, item, *_):
        detail = self.manager.get_screen("detail")
        detail.set_item(item)
        self.manager.current = "detail"


class AnimeDetailScreen(Screen):
    title_text = StringProperty("")
    meta_text = StringProperty("")
    synopsis_text = StringProperty("")
    item = DictProperty({})

    def set_item(self, item):
        self.item = item
        self.title_text = item.get("title") or "Unknown"

        genres = ", ".join(item.get("genres", [])) or "-"
        rating = item.get("rating") if item.get("rating") is not None else "-"
        year = item.get("year") if item.get("year") is not None else "-"
        episodes = item.get("episodes") if item.get("episodes") is not None else "-"
        status = item.get("status") or "-"

        self.meta_text = (
            f"Rating: {rating}\n"
            f"Year: {year} | Episodes: {episodes}\n"
            f"Status: {status} | Genres: {genres}"
        )
        self.synopsis_text = item.get("synopsis") or "No synopsis available in local catalog."

    def go_back(self):
        self.manager.current = "list"


class AniVerseMobileApp(App):
    title = APP_TITLE

    def build(self):
        Builder.load_string(KV)
        self.catalog = self._load_catalog()
        manager = ScreenManager()
        manager.add_widget(AnimeListScreen())
        manager.add_widget(AnimeDetailScreen())
        return manager

    def _load_catalog(self):
        if not os.path.exists(DATA_FILE):
            return []
        with open(DATA_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            return []
        return data


if __name__ == "__main__":
    AniVerseMobileApp().run()
