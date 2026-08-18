import html
import os

from PySide6.QtCore import QObject, QSize, Qt, Signal
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
    QInputDialog
)

from database.anilist import get_cached_media, get_media_async
from database.database import (
    get_all_animes_with_genres,
    get_anime_with_genres,
    get_recommendations,
    search_animes
)
from database.favorites import (
    get_favorite_ids,
    is_favorite,
    toggle_favorite
)
from database.lists import (
    add_anime_to_list,
    create_list,
    delete_list,
    get_anime_lists,
    get_list_anime_ids,
    get_lists,
    rename_list
)

GENRES = [
    '',
    'action',
    'fantasy',
    'comedy',
    'drama',
    'school',
    'adventure',
    'romance',
    'isekai'
]

ASSET_FOLDER = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    'assets'
)

ICON_FOLDER = os.path.join(
    ASSET_FOLDER,
    'icons'
)


def icon_path(name):

    return os.path.join(
        ICON_FOLDER,
        f'{name}.svg'
    )


def make_icon(name):

    path = icon_path(name)

    if os.path.exists(path):

        return QIcon(path)

    return QIcon()


class MediaBridge(QObject):

    ready = Signal(int, object)
    failed = Signal(int, object)
    image_ready = Signal(int, object)


class AnimeCard(QFrame):

    opened = Signal(int)
    favorite_changed = Signal(int)

    def __init__(self, anime, image_lookup):

        super().__init__()
        self.anime = anime
        self.poster = None
        self.setObjectName('AnimeCard')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(7)

        poster = QLabel()
        poster.setObjectName('CardPoster')
        poster.setFixedHeight(210)
        poster.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.poster = poster
        self.set_poster(
            image_lookup(anime),
            loading=image_lookup(anime) is None
        )

        layout.addWidget(poster)

        title = QLabel(anime['title'])
        title.setObjectName('CardTitle')
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        rating = anime.get('rating')
        rating_text = 'N/A' if rating is None else f'{rating:.1f}'
        metadata = QLabel(
            f'★ {rating_text}  ·  {anime.get("year", "N/A")}  ·  '
            f'{anime.get("episodes", "N/A")} eps'
        )
        metadata.setObjectName('Muted')
        metadata.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(metadata)

        actions = QHBoxLayout()
        actions.addStretch()
        favorite = QPushButton()
        favorite.setIcon(
            make_icon(
                'heart_filled' if is_favorite(anime['id']) else 'heart'
            )
        )
        favorite.setObjectName('FavoriteButton')
        favorite.setToolTip('Add or remove from favorites')
        favorite.setFixedSize(38, 32)
        favorite.clicked.connect(self.change_favorite)
        actions.addWidget(favorite)
        actions.addStretch()
        layout.addLayout(actions)

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.opened.emit(self.anime['id'])

        super().mousePressEvent(event)

    def change_favorite(self):

        toggle_favorite(self.anime['id'])
        self.favorite_changed.emit(self.anime['id'])

    def set_poster(self, path, loading=False):

        if path and os.path.exists(path):

            pixmap = QPixmap(path)

            if not pixmap.isNull():

                self.poster.setPixmap(
                    pixmap.scaled(
                        140,
                        205,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
                self.poster.setText('')
                return

        self.poster.setPixmap(QPixmap())
        self.poster.setText('Loading...' if loading else 'Not available')


class AnimeWindow(QMainWindow):

    def __init__(self):

        super().__init__()
        self.setWindowTitle('AniVerse')
        self.resize(980, 850)
        self.setMinimumSize(700, 650)
        self.animes = get_all_animes_with_genres()
        self.online_media = {}
        self.online_attempts = set()
        self.visible_cards = {}
        self.current_anime_id = None
        self.media_bridge = MediaBridge()
        self.media_bridge.ready.connect(self.apply_online_media)
        self.media_bridge.failed.connect(self.online_error)
        self.media_bridge.image_ready.connect(self.apply_image_to_cards)
        self.build_ui()
        self.show_home()

    def build_ui(self):

        central = QWidget()
        central.setObjectName('Shell')
        self.setCentralWidget(central)
        shell = QVBoxLayout(central)
        shell.setContentsMargins(22, 18, 22, 12)
        shell.setSpacing(12)

        header = QHBoxLayout()
        brand = QLabel('AniVerse')
        brand.setObjectName('Brand')
        header.addWidget(brand)
        header.addStretch()
        menu_button = QPushButton()
        menu_button.setIcon(make_icon('menu'))
        menu_button.setIconSize(QSize(22, 22))
        menu_button.setFixedSize(40, 36)
        menu_button.setToolTip('Open menu')
        menu_button.clicked.connect(self.show_settings)
        header.addWidget(menu_button)
        self.connection_label = QLabel('● Local catalog')
        self.connection_label.setObjectName('Muted')
        header.addWidget(self.connection_label)
        shell.addLayout(header)

        self.pages = QStackedWidget()
        shell.addWidget(self.pages, 1)

        self.home_page = self.build_home_page()
        self.search_page = self.build_search_page()
        self.favorites_page = QWidget()
        self.lists_page = QWidget()
        self.settings_page = self.build_settings_page()
        self.detail_page = QWidget()

        for page in (
            self.home_page,
            self.search_page,
            self.favorites_page,
            self.lists_page,
            self.settings_page,
            self.detail_page
        ):

            self.pages.addWidget(page)

        navigation = QFrame()
        navigation.setObjectName('BottomNav')
        nav_layout = QHBoxLayout(navigation)
        nav_layout.setContentsMargins(4, 4, 4, 4)

        items = [
            ('🏠', 'Home', self.show_home),
            ('🔎', 'Search', self.show_search),
            ('♥', 'Favorites', self.show_favorites),
            ('📚', 'Lists', self.show_lists),
            ('⚙', 'Settings', self.show_settings)
        ]

        for icon, label, handler in items:

            icon_name = {
                'Home': 'home',
                'Search': 'search',
                'Favorites': 'favorites',
                'Lists': 'lists',
                'Settings': 'settings'
            }[label]
            button = QPushButton(label)
            button.setIcon(make_icon(icon_name))
            button.setIconSize(QSize(22, 22))
            button.setObjectName('NavButton')
            button.setToolTip(label)
            button.clicked.connect(handler)
            nav_layout.addWidget(button, 1)

        shell.addWidget(navigation)

    def build_home_page(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        heading = QLabel('Principal')
        heading.setObjectName('PrincipalTitle')
        heading.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(heading)

        recommendations_title = QLabel('Recommendations')
        recommendations_title.setObjectName('SectionTitle')
        layout.addWidget(recommendations_title)

        self.home_scroll = QScrollArea()
        self.home_scroll.setWidgetResizable(True)
        self.home_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.home_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.home_scroll.setFrameShape(QFrame.Shape.NoFrame)

        home_content = QWidget()
        self.home_row = QHBoxLayout(home_content)
        self.home_row.setContentsMargins(4, 4, 10, 10)
        self.home_row.setSpacing(14)
        self.home_scroll.setWidget(home_content)
        layout.addWidget(self.home_scroll)
        layout.addStretch()

        self.render_home_recommendations()
        return page

    def render_home_recommendations(self):

        self.clear_layout(self.home_row)
        self.visible_cards = {}

        recommendations = sorted(
            self.animes,
            key=lambda anime: (
                anime.get('rating') or 0,
                anime.get('year') or 0
            ),
            reverse=True
        )[:12]

        for anime in recommendations:

            card = AnimeCard(anime, self.image_lookup)
            card.setFixedWidth(190)
            self.visible_cards.setdefault(
                anime['id'],
                []
            ).append(card)
            card.opened.connect(self.show_detail)
            card.favorite_changed.connect(self.refresh_visible_cards)
            self.home_row.addWidget(card)

        self.home_row.addStretch()
        self.prefetch_media(recommendations)

    def build_search_page(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel('Search anime')
        heading.setObjectName('PageTitle')
        layout.addWidget(heading)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search by title or original title...')
        self.search_input.textChanged.connect(self.render_search_results)
        layout.addWidget(self.search_input)

        self.search_scroll = self.create_scroll()
        layout.addWidget(self.search_scroll, 1)
        self.search_grid = self.search_scroll.widget().layout()
        return page

    def build_settings_page(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel('⚙ Settings')
        title.setObjectName('PageTitle')
        layout.addWidget(title)
        layout.addWidget(QLabel('AniVerse uses the local catalog first.'))
        layout.addWidget(QLabel('AniList is queried only when opening a detail page and results are cached.'))
        layout.addStretch()
        return page

    def create_scroll(self):

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        grid = QGridLayout(content)
        grid.setContentsMargins(4, 4, 10, 4)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(14)
        scroll.setWidget(content)
        return scroll

    @staticmethod
    def clear_layout(layout):

        while layout.count():

            item = layout.takeAt(0)
            widget = item.widget()

            if widget:

                widget.deleteLater()

    def image_lookup(self, anime):

        media = self.online_media.get(anime['id'], {})
        if not media:

            media = get_cached_media(anime['franchise']) or {}

        return media.get('local_image')

    def render_grid(self, layout, animes, list_id=None):

        self.clear_layout(layout)
        self.visible_cards = {}

        if not animes:

            layout.addWidget(QLabel('No results yet.'), 0, 0)
            return

        columns = 4

        for index, anime in enumerate(animes):

            card = AnimeCard(anime, self.image_lookup)
            self.visible_cards.setdefault(
                anime['id'],
                []
            ).append(card)
            card.opened.connect(self.show_detail)
            card.favorite_changed.connect(self.refresh_visible_cards)

            if list_id is not None:

                remove_button = QPushButton('Remove from list')
                remove_button.setIcon(make_icon('remove'))
                remove_button.setToolTip('Remove this anime from the list')
                remove_button.clicked.connect(
                    lambda checked=False, anime_id=anime['id']: self.remove_from_list(
                        list_id,
                        anime_id
                    )
                )
                card.layout().addWidget(remove_button)

            layout.addWidget(card, index // columns, index % columns)

    def render_search_results(self):

        results = search_animes(self.search_input.text())
        self.render_grid(self.search_grid, results)
        self.prefetch_media(results[:12])

    def prefetch_media(self, animes):

        for anime in animes:

            if anime['id'] in self.online_attempts:

                continue

            if self.image_lookup(anime):

                continue

            self.online_attempts.add(anime['id'])
            get_media_async(
                anime['title'],
                anime['franchise'],
                lambda media, anime_id=anime['id']: self.media_bridge.image_ready.emit(
                    anime_id,
                    media
                ),
                lambda error, anime_id=anime['id']: self.media_bridge.image_ready.emit(
                    anime_id,
                    None
                ),
                anime.get('original_title')
            )

    def apply_image_to_cards(self, anime_id, media):

        if not media:

            for card in self.visible_cards.get(anime_id, []):

                card.set_poster(
                    None,
                    loading=False
                )

            return

        self.online_media[anime_id] = media

        for card in self.visible_cards.get(anime_id, []):

            card.set_poster(
                media.get('local_image'),
                loading=False
            )

    def render_favorites(self):

        page_layout = self.favorites_page.layout()

        if page_layout is None:

            page_layout = QVBoxLayout(self.favorites_page)
            page_layout.setContentsMargins(0, 0, 0, 0)

        self.clear_layout(page_layout)
        title = QLabel('Favorites')
        title.setObjectName('PageTitle')
        page_layout.addWidget(title)
        favorite_ids = set(get_favorite_ids())
        favorites = [anime for anime in self.animes if anime['id'] in favorite_ids]
        scroll = self.create_scroll()
        page_layout.addWidget(scroll, 1)
        self.render_grid(scroll.widget().layout(), favorites)
        self.prefetch_media(favorites[:12])

    def render_lists(self):

        page_layout = self.lists_page.layout()

        if page_layout is None:

            page_layout = QVBoxLayout(self.lists_page)
            page_layout.setContentsMargins(0, 0, 0, 0)

        self.clear_layout(page_layout)
        header = QHBoxLayout()
        title = QLabel('My lists')
        title.setObjectName('PageTitle')
        header.addWidget(title)
        header.addStretch()
        create_button = QPushButton('Create list')
        create_button.setIcon(make_icon('add'))
        create_button.clicked.connect(self.create_user_list)
        header.addWidget(create_button)
        page_layout.addLayout(header)

        for user_list in get_lists():

            row = QFrame()
            row.setObjectName('ListRow')
            row_layout = QHBoxLayout(row)
            label = QPushButton(
                f"{user_list['name']}   ·   {user_list['count']}"
            )
            label.setObjectName('ListButton')
            label.clicked.connect(
                lambda checked=False, list_id=user_list['id']: self.open_list(list_id)
            )
            row_layout.addWidget(label, 1)
            rename = QPushButton()
            rename.setIcon(make_icon('settings'))
            rename.setToolTip('Rename list')
            rename.clicked.connect(
                lambda checked=False, item=user_list: self.rename_user_list(item)
            )
            row_layout.addWidget(rename)
            remove = QPushButton()
            remove.setIcon(make_icon('remove'))
            remove.setToolTip('Delete list')
            remove.clicked.connect(
                lambda checked=False, list_id=user_list['id']: self.delete_user_list(list_id)
            )
            row_layout.addWidget(remove)
            page_layout.addWidget(row)

        page_layout.addStretch()

    def open_list(self, list_id):

        ids = set(get_list_anime_ids(list_id))
        animes = [anime for anime in self.animes if anime['id'] in ids]
        page_layout = self.lists_page.layout()
        self.clear_layout(page_layout)
        back = QPushButton('Back to lists')
        back.setIcon(make_icon('back'))
        back.clicked.connect(self.render_lists)
        page_layout.addWidget(back)
        title = next((item['name'] for item in get_lists() if item['id'] == list_id), 'List')
        heading = QLabel(f'📚 {title}')
        heading.setObjectName('PageTitle')
        page_layout.addWidget(heading)
        scroll = self.create_scroll()
        page_layout.addWidget(scroll, 1)
        self.render_grid(scroll.widget().layout(), animes, list_id)
        self.prefetch_media(animes[:12])

    def remove_from_list(self, list_id, anime_id):

        from database.lists import remove_anime_from_list

        remove_anime_from_list(list_id, anime_id)
        self.open_list(list_id)

    def create_user_list(self):

        name, accepted = QInputDialog.getText(self, 'Create list', 'Name:')

        if accepted and create_list(name):

            self.render_lists()

    def rename_user_list(self, user_list):

        name, accepted = QInputDialog.getText(
            self,
            'Rename list',
            'New name:',
            text=user_list['name']
        )

        if accepted and rename_list(user_list['id'], name):

            self.render_lists()

    def delete_user_list(self, list_id):

        answer = QMessageBox.question(
            self,
            'Delete list',
            'Do you want to delete this list?'
        )

        if answer == QMessageBox.StandardButton.Yes:

            delete_list(list_id)
            self.render_lists()

    def show_home(self):

        self.pages.setCurrentWidget(self.home_page)
        self.connection_label.setText('● Local catalog')

    def show_search(self):

        self.pages.setCurrentWidget(self.search_page)
        self.connection_label.setText('● Local search')

    def show_favorites(self):

        self.render_favorites()
        self.pages.setCurrentWidget(self.favorites_page)

    def show_lists(self):

        self.render_lists()
        self.pages.setCurrentWidget(self.lists_page)

    def show_settings(self):

        self.pages.setCurrentWidget(self.settings_page)

    def show_detail(self, anime_id, return_page=None):

        anime = get_anime_with_genres(anime_id)

        if not anime:

            return

        self.current_anime_id = anime_id
        self.detail_return_page = return_page or self.pages.currentWidget()
        self.render_detail(
            anime,
            self.online_media.get(anime_id)
            or get_cached_media(anime['franchise'])
            or {}
        )
        self.pages.setCurrentWidget(self.detail_page)

        if anime_id in self.online_attempts:

            return

        self.online_attempts.add(anime_id)
        self.connection_label.setText('◌ Loading AniList')
        get_media_async(
            anime['title'],
            anime['franchise'],
            lambda media: self.media_bridge.ready.emit(anime_id, media),
            lambda error: self.media_bridge.failed.emit(anime_id, error),
            anime.get('original_title')
        )

    def render_detail(self, anime, online):

        page_layout = self.detail_page.layout()

        if page_layout is None:

            page_layout = QVBoxLayout(self.detail_page)
            page_layout.setContentsMargins(0, 0, 0, 0)

        self.clear_layout(page_layout)
        back = QPushButton('Back')
        back.setIcon(make_icon('back'))
        back.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.detail_return_page)
        )
        page_layout.addWidget(back, alignment=Qt.AlignmentFlag.AlignLeft)

        profile = QFrame()
        profile_layout = QHBoxLayout(profile)
        poster = QLabel()
        poster.setObjectName('DetailPoster')
        poster.setFixedSize(220, 300)
        poster.setAlignment(Qt.AlignmentFlag.AlignCenter)
        path = online.get('local_image')

        if path:

            pixmap = QPixmap(path)

            if not pixmap.isNull():

                poster.setPixmap(
                    pixmap.scaled(
                        210,
                        290,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )

        if poster.pixmap() is None or poster.pixmap().isNull():

            poster.setText('No image available')

        profile_layout.addWidget(poster)
        info = QVBoxLayout()
        title = QLabel(anime['title'])
        title.setObjectName('DetailTitle')
        title.setWordWrap(True)
        info.addWidget(title)
        fields = [
            ('Original', anime.get('original_title')),
            ('Rating', anime.get('rating')),
            ('Year', anime.get('year')),
            ('Episodes', anime.get('episodes')),
            ('Status', anime.get('status')),
            ('Genres', ', '.join(anime.get('genres', [])))
        ]

        for label, value in fields:

            info.addWidget(QLabel(f'{label}: {self.value(value)}'))

        favorite = QPushButton(
            'Remove favorite' if is_favorite(anime['id'])
            else 'Add to favorites'
        )
        favorite.setIcon(make_icon(
            'heart_filled' if is_favorite(anime['id']) else 'heart'
        ))
        favorite.clicked.connect(
            lambda: self.toggle_detail_favorite(anime['id'])
        )
        info.addWidget(favorite)

        list_row = QHBoxLayout()
        list_box = QComboBox()
        list_box.addItem('Add to a list...', None)

        for item in get_lists():

            list_box.addItem(item['name'], item['id'])

        list_button = QPushButton('Add')
        list_button.setIcon(make_icon('add'))
        list_button.clicked.connect(
            lambda: self.add_detail_to_list(anime['id'], list_box)
        )
        list_row.addWidget(list_box, 1)
        list_row.addWidget(list_button)
        info.addLayout(list_row)

        current_lists = get_anime_lists(anime['id'])
        info.addWidget(QLabel(
            'Lists: ' + (', '.join(item['name'] for item in current_lists) or 'None')
        ))
        info.addStretch()
        profile_layout.addLayout(info, 1)
        page_layout.addWidget(profile)

        description = online.get('synopsis') or anime.get('synopsis')
        synopsis = QTextBrowser()
        synopsis.setOpenExternalLinks(True)
        synopsis.setHtml(
            f'<h2>Synopsis</h2><p>{html.escape(self.value(description))}</p>'
        )
        page_layout.addWidget(synopsis, 1)

        watch = QTextBrowser()
        watch.setOpenExternalLinks(True)
        watch.setMaximumHeight(130)
        links = online.get('watch_links', [])
        content = '<h2>Where to watch</h2>'
        content += ''.join(
            f'<p><a href="{link["url"]}">{html.escape(link["site"])}</a></p>'
            for link in links[:8]
        ) or '<p>Not available</p>'
        if online.get('trailer_url'):
            content += f'<p><a href="{online["trailer_url"]}">▶ Watch trailer</a></p>'
        watch.setHtml(content)
        page_layout.addWidget(watch)

    def add_detail_to_list(self, anime_id, list_box):

        list_id = list_box.currentData()

        if list_id is not None:

            add_anime_to_list(list_id, anime_id)
            self.show_detail(anime_id, self.detail_return_page)

    def toggle_detail_favorite(self, anime_id):

        toggle_favorite(anime_id)
        self.show_detail(anime_id, self.detail_return_page)

    def apply_online_media(self, anime_id, media):

        if media:

            self.online_media[anime_id] = media
            self.connection_label.setText('● AniList connected')

            if self.current_anime_id == anime_id:

                self.render_detail(
                    get_anime_with_genres(anime_id),
                    media
                )

            elif self.pages.currentWidget() is self.search_page:

                self.render_search_results()

    def online_error(self, anime_id, error):

        if self.current_anime_id == anime_id:

            self.connection_label.setText('● Offline mode')

    def refresh_visible_cards(self):

        current = self.pages.currentWidget()

        if current is self.search_page:

            self.render_search_results()
        elif current is self.favorites_page:

            self.render_favorites()

    @staticmethod
    def value(value):

        return 'Not available' if value is None or value == '' else str(value)
