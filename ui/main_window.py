import html
import os
import random

from PySide6.QtCore import (
    QEasingCurve,
    QObject,
    QPropertyAnimation,
    QTimer,
    QSize,
    Qt,
    Signal
)
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QButtonGroup,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGraphicsBlurEffect,
    QGridLayout,
    QGraphicsOpacityEffect,
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
    QStackedLayout,
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
from database.image_manager import ImageManager
from database.franchises import build_franchise_groups
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


class AnimatedButton(QPushButton):

    def __init__(self, text='', parent=None):

        super().__init__(text, parent)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.9)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_animation = QPropertyAnimation(
            self.opacity_effect,
            b'opacity',
            self
        )
        self.opacity_animation.setDuration(140)
        self.opacity_animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

    def animate_opacity(self, value):

        self.opacity_animation.stop()
        self.opacity_animation.setStartValue(
            self.opacity_effect.opacity()
        )
        self.opacity_animation.setEndValue(value)
        self.opacity_animation.start()

    def enterEvent(self, event):

        self.animate_opacity(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):

        self.animate_opacity(0.9)
        super().leaveEvent(event)


PLACEHOLDER_PATH = os.path.join(
    ASSET_FOLDER,
    'images',
    'poster_placeholder.svg'
)


class MediaBridge(QObject):

    ready = Signal(int, object)
    failed = Signal(int, object)
    image_ready = Signal(int, object)
    image_loaded = Signal(int, str)
    image_failed = Signal(int)


class AnimeCard(QFrame):

    opened = Signal(int)
    favorite_changed = Signal(int)

    def __init__(self, anime, image_lookup):

        super().__init__()
        self.anime = anime
        self.poster = None
        self.setObjectName('AnimeCard')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(184, 350)
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 8, 6, 8)
        layout.setSpacing(7)

        poster = QLabel()
        poster.setObjectName('CardPoster')
        poster.setFixedSize(160, 226)
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
        self.favorite_button = favorite
        favorite.setIcon(
            make_icon(
                'heart_filled' if is_favorite(anime['id']) else 'heart'
            )
        )
        favorite.setObjectName('FavoriteButton')
        favorite.setToolTip('Add or remove from favorites')
        favorite.setFixedSize(38, 32)
        favorite.setCursor(Qt.CursorShape.PointingHandCursor)
        favorite.clicked.connect(self.change_favorite)
        actions.addWidget(favorite)
        actions.addStretch()
        layout.addLayout(actions)

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.opened.emit(self.anime['id'])

        super().mousePressEvent(event)

    def change_favorite(self):

        saved = toggle_favorite(self.anime['id'])
        self.favorite_button.setIcon(
            make_icon(
                'heart_filled' if saved else 'heart'
            )
        )
        self.favorite_button.setToolTip(
            'Remove from favorites' if saved
            else 'Add to favorites'
        )
        self.favorite_changed.emit(self.anime['id'])

    def set_poster(self, path, loading=False):

        if path and os.path.exists(path):

            pixmap = QPixmap(path)

            if not pixmap.isNull():

                self.poster.setPixmap(
                    pixmap.scaled(
                        154,
                        220,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
                self.poster.setText('')
                return

        placeholder = QPixmap(PLACEHOLDER_PATH)

        if not placeholder.isNull():

            self.poster.setPixmap(
                placeholder.scaled(
                    154,
                    220,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

        self.poster.setText('')


class PartCard(QFrame):

    opened = Signal(int)

    def __init__(self, anime, image_lookup):

        super().__init__()
        self.anime = anime
        self.setObjectName('PartCard')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(168, 286)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(7, 7, 7, 7)
        layout.setSpacing(5)

        self.poster = QLabel()
        self.poster.setObjectName('PartPoster')
        self.poster.setFixedSize(154, 196)
        self.poster.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_poster(image_lookup(anime))
        layout.addWidget(self.poster)

        title = QLabel(anime['title'])
        title.setObjectName('PartTitle')
        title.setWordWrap(True)
        title.setMaximumHeight(38)
        layout.addWidget(title)

        episodes = anime.get('episodes')
        year = anime.get('year')
        layout.addWidget(QLabel(
            f"{episodes if episodes is not None else 'N/A'} episodes  ·  "
            f"{year if year is not None else 'N/A'}"
        ))

    def set_poster(self, path):

        if path and os.path.exists(path):

            pixmap = QPixmap(path)

            if not pixmap.isNull():

                self.poster.setPixmap(
                    pixmap.scaled(
                        150,
                        192,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
                return

        placeholder = QPixmap(PLACEHOLDER_PATH)
        self.poster.setPixmap(
            placeholder.scaled(
                150,
                192,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.opened.emit(self.anime['id'])

        super().mousePressEvent(event)


class AnimeWindow(QMainWindow):

    def __init__(self):

        super().__init__()
        self.setWindowTitle('AniVerse')
        self.resize(980, 850)
        self.setMinimumSize(700, 650)
        self.anime_parts = get_all_animes_with_genres()
        self.animes = build_franchise_groups(
            self.anime_parts
        )
        self.online_media = {}
        self.online_attempts = set()
        self.visible_cards = {}
        self.home_section_expanded = {}
        self.random_history = set()
        self.is_mobile = False
        self._responsive_mode = False
        self.current_anime_id = None
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(350)
        self.search_timer.timeout.connect(self.render_search_results)
        self.media_bridge = MediaBridge()
        self.media_bridge.ready.connect(self.apply_online_media)
        self.media_bridge.failed.connect(self.online_error)
        self.media_bridge.image_ready.connect(self.apply_image_to_cards)
        self.media_bridge.image_loaded.connect(self.apply_image_path)
        self.media_bridge.image_failed.connect(self.apply_image_failure)
        self.image_manager = ImageManager(
            on_ready=lambda anime, path: self.media_bridge.image_loaded.emit(
                anime['id'],
                path
            ),
            on_failed=lambda anime, error: self.media_bridge.image_failed.emit(
                anime['id']
            )
        )
        self.build_ui()
        self.show_home()

    def build_ui(self):

        central = QWidget()
        central.setObjectName('Shell')
        self.setCentralWidget(central)
        shell = QVBoxLayout(central)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName('Sidebar')
        sidebar.setFixedWidth(150)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 18, 10, 14)
        sidebar_layout.setSpacing(8)

        brand = QLabel('AniVerse')
        brand.setObjectName('Brand')
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(brand)
        sidebar_layout.addSpacing(18)

        nav_items = [
            ('home', 'Home', self.show_home),
            ('search', 'Explore', self.show_search),
            ('wand', 'Random', self.show_random),
            ('favorites', 'Favorites', self.show_favorites),
            ('lists', 'Lists', self.show_lists),
            ('settings', 'Settings', self.show_settings)
        ]

        for icon_name, label, handler in nav_items:

            button = AnimatedButton(label)
            button.setObjectName('SideNavButton')
            button.setIcon(make_icon(icon_name))
            button.setIconSize(QSize(20, 20))
            button.setToolTip(label)
            button.clicked.connect(handler)
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()
        body_layout.addWidget(sidebar)

        content_shell = QVBoxLayout()
        content_shell.setContentsMargins(22, 14, 22, 14)
        content_shell.setSpacing(12)

        header = QHBoxLayout()
        header.addStretch()
        self.connection_label = QLabel('● Local catalog')
        self.connection_label.setObjectName('Muted')
        header.addWidget(self.connection_label)
        avatar = QLabel('AV')
        avatar.setObjectName('Avatar')
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(34, 34)
        header.addWidget(avatar)
        content_shell.addLayout(header)

        self.pages = QStackedWidget()
        content_shell.addWidget(self.pages, 1)

        self.home_page = self.build_home_page()
        self.search_page = self.build_search_page()
        self.random_page = self.build_random_page()
        self.favorites_page = QWidget()
        self.lists_page = QWidget()
        self.settings_page = self.build_settings_page()
        self.detail_page = QWidget()

        for page in (
            self.home_page,
            self.search_page,
            self.random_page,
            self.favorites_page,
            self.lists_page,
            self.settings_page,
            self.detail_page
        ):

            self.pages.addWidget(page)

        body_layout.addLayout(content_shell, 1)
        shell.addWidget(body, 1)

        self.sidebar = sidebar
        self.mobile_nav = self.build_mobile_navigation()
        shell.addWidget(self.mobile_nav)
        self.mobile_nav.setVisible(False)

    def build_mobile_navigation(self):

        navigation = QFrame()
        navigation.setObjectName('MobileNav')
        layout = QHBoxLayout(navigation)
        layout.setContentsMargins(6, 5, 6, 5)
        layout.setSpacing(3)

        for icon_name, label, handler in (
            ('home', 'Home', self.show_home),
            ('search', 'Explore', self.show_search),
            ('wand', 'Random', self.show_random),
            ('favorites', 'Favorites', self.show_favorites),
            ('lists', 'Lists', self.show_lists)
        ):

            button = AnimatedButton(label)
            button.setObjectName('MobileNavButton')
            button.setIcon(make_icon(icon_name))
            button.setIconSize(QSize(21, 21))
            button.setToolTip(label)
            button.clicked.connect(handler)
            layout.addWidget(button, 1)

        return navigation

    def resizeEvent(self, event):

        mobile = self.width() < 700

        if mobile != self._responsive_mode:

            self.is_mobile = mobile
            self._responsive_mode = mobile
            self.sidebar.setVisible(not mobile)
            self.mobile_nav.setVisible(mobile)
            self.render_home_sections()

        super().resizeEvent(event)

    def build_home_page(self):

        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        self.home_scroll = QScrollArea()
        self.home_scroll.setWidgetResizable(True)
        self.home_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.home_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        home_content = QWidget()
        self.home_content_layout = QVBoxLayout(home_content)
        self.home_content_layout.setContentsMargins(4, 4, 10, 16)
        self.home_content_layout.setSpacing(22)
        self.home_scroll.setWidget(home_content)
        page_layout.addWidget(self.home_scroll)

        self.render_home_sections()
        return page

    def render_home_sections(self):

        self.clear_layout(self.home_content_layout)
        self.visible_cards = {}
        self.home_section_expanded = {}

        recommendations = sorted(
            self.animes,
            key=lambda anime: (
                anime.get('rating') or 0,
                anime.get('year') or 0
            ),
            reverse=True
        )[:12]

        self.add_home_section(
            'Featured',
            recommendations
        )

        for genre in GENRES[1:]:

            genre_animes = [
                anime
                for anime in self.animes
                if genre in anime.get('genres', [])
            ]
            genre_animes.sort(
                key=lambda anime: (
                    anime.get('rating') or 0,
                    anime.get('year') or 0
                ),
                reverse=True
            )
            self.add_home_section(
                genre.title(),
                genre_animes[:12]
            )

        self.home_content_layout.addStretch()

    def add_home_section(self, title, animes):

        section = QFrame()
        section.setObjectName('HomeSection')
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(12, 12, 12, 12)
        section_layout.setSpacing(12)

        header = QHBoxLayout()
        section_icons = {
            'Featured': '✦',
            'Action': '⚔',
            'Fantasy': '✧',
            'Comedy': '☻',
            'Drama': '◈',
            'School': '⌘',
            'Adventure': '➜',
            'Romance': '♡',
            'Isekai': '◉'
        }
        heading = QLabel(
            f"{section_icons.get(title, '•')}  {title}"
        )
        heading.setObjectName('SectionTitle')
        header.addWidget(heading)
        header.addStretch()

        more_button = QPushButton('See more')
        more_button.setObjectName('SeeMoreButton')
        more_button.clicked.connect(
            lambda: self.expand_home_section(title, animes, section)
        )
        header.addWidget(more_button)
        section_layout.addLayout(header)

        section.setProperty('homeTitle', title)
        section.setProperty('homeAnimeCount', len(animes))
        section._more_button = more_button

        if self.is_mobile:

            row_scroll = QScrollArea()
            row_scroll.setWidgetResizable(True)
            row_scroll.setFrameShape(QFrame.Shape.NoFrame)
            row_scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            row_scroll.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            row_content = QWidget()
            row_layout = QHBoxLayout(row_content)
            row_layout.setContentsMargins(2, 2, 2, 6)
            row_layout.setSpacing(10)
            row_scroll.setWidget(row_content)
            section_layout.addWidget(row_scroll)
            section._cards_grid = None
            section._cards_layout = row_layout
            section._row_scroll = row_scroll
            self.populate_home_row(row_layout, animes[:3])

        else:

            cards_grid = QGridLayout()
            cards_grid.setContentsMargins(2, 2, 2, 2)
            cards_grid.setHorizontalSpacing(12)
            cards_grid.setVerticalSpacing(12)
            section_layout.addLayout(cards_grid)
            section._cards_grid = cards_grid
            section._cards_layout = None
            self.populate_home_grid(cards_grid, animes[:5])

        self.home_content_layout.addWidget(section)
        self.prefetch_media(animes[:3] if self.is_mobile else animes[:5])

    def populate_home_row(self, layout, animes):

        for anime in animes:

            card = AnimeCard(anime, self.image_lookup)
            card.setFixedWidth(184)
            self.visible_cards.setdefault(anime['id'], []).append(card)
            card.opened.connect(self.show_detail)
            card.favorite_changed.connect(self.refresh_visible_cards)
            layout.addWidget(card)

        layout.addStretch()

    def populate_home_grid(self, grid, animes):

        for index, anime in enumerate(animes):

            card = AnimeCard(anime, self.image_lookup)
            card.setFixedWidth(178)
            self.visible_cards.setdefault(
                anime['id'],
                []
            ).append(card)
            card.opened.connect(self.show_detail)
            card.favorite_changed.connect(self.refresh_visible_cards)
            grid.addWidget(
                card,
                0,
                index,
                Qt.AlignmentFlag.AlignTop
            )

    def expand_home_section(self, title, animes, section):

        expanded = self.home_section_expanded.get(title, False)
        self.home_section_expanded[title] = not expanded
        grid = section._cards_grid

        if self.is_mobile and section._cards_layout is not None:

            self.clear_layout(section._cards_layout)
            visible_animes = animes if not expanded else animes[:3]
            section._more_button.setText(
                'Show less' if not expanded else 'See more'
            )
            self.populate_home_row(
                section._cards_layout,
                visible_animes
            )
            self.prefetch_media(visible_animes)
            return

        while grid.count():

            item = grid.takeAt(0)

            if item.widget():

                item.widget().deleteLater()

        visible_animes = animes if not expanded else animes[:5]
        section._more_button.setText(
            'Show less' if not expanded else 'See more'
        )

        for index, anime in enumerate(visible_animes):

            card = AnimeCard(anime, self.image_lookup)
            card.setFixedWidth(178)
            self.visible_cards.setdefault(
                anime['id'],
                []
            ).append(card)
            card.opened.connect(self.show_detail)
            card.favorite_changed.connect(self.refresh_visible_cards)
            grid.addWidget(
                card,
                index // 5,
                index % 5,
                Qt.AlignmentFlag.AlignTop
            )

        self.prefetch_media(visible_animes)

    def build_search_page(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel('Search anime')
        heading.setObjectName('PageTitle')
        layout.addWidget(heading)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search by title or original title...')
        self.search_input.setVisible(True)

        search_row = QHBoxLayout()
        search_row.addWidget(self.search_input, 1)
        search_button = QPushButton()
        search_button.setIcon(make_icon('search'))
        search_button.setIconSize(QSize(22, 22))
        search_button.setFixedSize(46, 42)
        search_button.setToolTip('Search')
        search_button.clicked.connect(self.render_search_results)
        search_row.addWidget(search_button)
        layout.addLayout(search_row)

        self.search_scroll = self.create_scroll()
        layout.addWidget(self.search_scroll, 1)
        self.search_grid = self.search_scroll.widget().layout()
        return page

    def build_random_page(self):

        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        page_scroll = QScrollArea()
        page_scroll.setWidgetResizable(True)
        page_scroll.setFrameShape(QFrame.Shape.NoFrame)
        page_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(4, 4, 10, 18)
        layout.setSpacing(18)

        heading = QLabel('Random discovery')
        heading.setObjectName('PageTitle')
        layout.addWidget(heading)

        intro = QLabel('Choose one genre and let AniVerse surprise you.')
        intro.setObjectName('Muted')
        layout.addWidget(intro)

        genre_panel = QFrame()
        genre_panel.setObjectName('RandomPanel')
        genre_layout = QGridLayout(genre_panel)
        genre_layout.setContentsMargins(14, 14, 14, 14)
        genre_layout.setHorizontalSpacing(10)
        genre_layout.setVerticalSpacing(10)
        self.random_group = QButtonGroup(self)
        self.random_group.setExclusive(True)
        self.random_genre_buttons = []

        for index, genre in enumerate(GENRES[1:]):

            button = AnimatedButton(genre.title())
            button.setCheckable(True)
            button.setObjectName('GenreChoice')
            self.random_group.addButton(button)
            self.random_genre_buttons.append(button)
            genre_layout.addWidget(button, index // 3, index % 3)

        self.random_genre_buttons[0].setChecked(True)
        layout.addWidget(genre_panel)

        episodes_label = QLabel('Episode filter')
        episodes_label.setObjectName('SectionTitle')
        layout.addWidget(episodes_label)
        popularity_panel = QFrame()
        popularity_panel.setObjectName('RandomPanel')
        popularity_layout = QGridLayout(popularity_panel)
        popularity_layout.setContentsMargins(12, 12, 12, 12)
        popularity_layout.setHorizontalSpacing(10)
        self.random_episode_group = QButtonGroup(self)
        self.random_episode_group.setExclusive(True)

        for index, option in enumerate((
            ('All episodes', 'all'),
            ('Under 24 episodes', 'under_24'),
            ('24+ episodes', 'over_24')
        )):

            button = AnimatedButton(option[0])
            button.setCheckable(True)
            button.setObjectName('GenreChoice')
            button.setProperty('episodeFilter', option[1])
            self.random_episode_group.addButton(button)
            popularity_layout.addWidget(button, 0, index)

            if index == 0:

                button.setChecked(True)

        layout.addWidget(popularity_panel)

        search_button = AnimatedButton('Search randomly')
        search_button.setObjectName('PrimaryButton')
        search_button.setIcon(make_icon('wand'))
        search_button.clicked.connect(self.random_discovery)
        layout.addWidget(search_button, alignment=Qt.AlignmentFlag.AlignLeft)

        results_title = QLabel('Random results')
        results_title.setObjectName('SectionTitle')
        layout.addWidget(results_title)
        random_results = QFrame()
        random_results.setObjectName('RandomResults')
        self.random_grid = QGridLayout(random_results)
        self.random_grid.setContentsMargins(4, 4, 4, 4)
        self.random_grid.setHorizontalSpacing(12)
        self.random_grid.setVerticalSpacing(12)
        layout.addWidget(random_results)
        layout.addStretch()
        page_scroll.setWidget(content)
        page_layout.addWidget(page_scroll)
        self.random_discovery()
        return page

    def random_discovery(self):

        selected_button = self.random_group.checkedButton()
        selected = selected_button.text().casefold() if selected_button else 'action'
        primary_pool = [
            anime
            for anime in self.animes
            if anime.get('primary_genre') == selected
        ]
        secondary_pool = [
            anime
            for anime in self.animes
            if selected in anime.get('genres', [])
            and anime not in primary_pool
        ]
        episode_button = self.random_episode_group.checkedButton()
        episode_filter = (
            episode_button.property('episodeFilter')
            if episode_button
            else 'all'
        )

        pool = primary_pool + secondary_pool

        if episode_filter == 'under_24':

            pool = [
                anime
                for anime in pool
                if anime.get('episodes_complete')
                and anime.get('known_episodes') is not None
                and anime['known_episodes'] < 24
            ]

        elif episode_filter == 'over_24':

            pool = [
                anime
                for anime in pool
                if anime.get('episodes_complete')
                and anime.get('known_episodes') is not None
                and anime['known_episodes'] >= 24
            ]

        random.shuffle(pool)
        unseen = [
            anime
            for anime in pool
            if anime['franchise_key'] not in self.random_history
        ]

        if not unseen:

            self.random_history.clear()
            unseen = pool

        selected_results = unseen[:5]
        self.random_history.update(
            anime['franchise_key']
            for anime in selected_results
        )
        self.render_grid(
            self.random_grid,
            selected_results
        )
        self.prefetch_media(selected_results)

    def build_settings_page(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel('⚙ Settings')
        title.setObjectName('PageTitle')
        layout.addWidget(title)
        layout.addWidget(QLabel('AniVerse uses the local catalog first.'))
        layout.addWidget(QLabel('The catalog and descriptions work offline. Images are enriched online when available.'))
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

        path = self.image_manager.get_local_path(anime)

        if path:

            return path

        for part in anime.get('parts', []):

            path = self.image_manager.get_local_path(part)

            if path:

                return path

        return media.get('local_image')

    def render_grid(self, layout, animes, list_id=None):

        self.clear_layout(layout)
        self.visible_cards = {}

        if not animes:

            layout.addWidget(QLabel('No results yet.'), 0, 0)
            return

        columns = 2 if self.is_mobile else 4

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

            layout.addWidget(
                card,
                index // columns,
                index % columns,
                Qt.AlignmentFlag.AlignTop
            )

    def render_search_results(self):

        query = self.search_input.text().strip().casefold()

        if len(query) < 2:

            self.clear_layout(self.search_grid)
            self.search_grid.addWidget(
                QLabel('Type at least two characters to search.'),
                0,
                0
            )
            return

        results = [
            anime
            for anime in self.animes
            if query in anime.get('title', '').casefold()
            or query in (anime.get('original_title') or '').casefold()
            or any(
                query in part.get('title', '').casefold()
                for part in anime.get('parts', [])
            )
        ]
        visible_results = results[:60]
        self.render_grid(self.search_grid, visible_results)
        self.prefetch_media(visible_results[:12])

    def prefetch_media(self, animes):

        for anime in animes:

            self.image_manager.request(anime)

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

    def apply_image_path(self, anime_id, path):

        self.online_media.setdefault(
            anime_id,
            {}
        )['local_image'] = path

        for card in self.visible_cards.get(anime_id, []):

            if isinstance(card, PartCard):
                card.set_poster(path)
            else:
                card.set_poster(path, loading=False)

    def apply_image_failure(self, anime_id):

        for card in self.visible_cards.get(anime_id, []):

            if isinstance(card, PartCard):
                card.set_poster(None)
            else:
                card.set_poster(None, loading=False)

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
        favorites = [
            anime
            for anime in self.animes
            if anime['id'] in favorite_ids
            or any(part['id'] in favorite_ids for part in anime.get('parts', []))
        ]
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
        animes = [
            anime
            for anime in self.animes
            if anime['id'] in ids
            or any(part['id'] in ids for part in anime.get('parts', []))
        ]
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

    def show_random(self):

        self.pages.setCurrentWidget(self.random_page)
        self.connection_label.setText('● Local random discovery')

    def show_favorites(self):

        self.render_favorites()
        self.pages.setCurrentWidget(self.favorites_page)

    def show_lists(self):

        self.render_lists()
        self.pages.setCurrentWidget(self.lists_page)

    def show_settings(self):

        self.pages.setCurrentWidget(self.settings_page)

    def show_detail(self, anime_id, return_page=None):

        anime = next(
            (
                item
                for item in self.animes
                if item['id'] == anime_id
                or any(
                    part['id'] == anime_id
                    for part in item.get('parts', [])
                )
            ),
            None
        )

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

    def render_detail_legacy_reference(self, anime, online):

        """

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
        profile.setObjectName('DetailProfile')
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
            (
                'Episodes',
                f"{anime.get('known_episodes')}+"
                if not anime.get('episodes_complete')
                else anime.get('known_episodes')
            ),
            ('Status', anime.get('status')),
            ('Genres', ', '.join(anime.get('genres', []))),
            ('Parts', anime.get('part_count'))
        ]

        for label, value in fields:

            info.addWidget(QLabel(f'{label}: {self.value(value)}'))

        favorite = QPushButton(
            'Remove favorite' if is_favorite(anime['id'])
            else 'Add to favorites'
        )
        favorite.setIcon(make_icon(
            self.clear_layout(page_layout)

            back = QPushButton('Back')
            back.setIcon(make_icon('back'))
            back.clicked.connect(
                lambda: self.pages.setCurrentWidget(self.detail_return_page)
            )
            page_layout.addWidget(back, alignment=Qt.AlignmentFlag.AlignLeft)

            hero = QFrame()
            hero.setObjectName('DetailHero')
            hero_stack = QStackedLayout(hero)
            hero_stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

            background = QLabel()
            background.setObjectName('DetailBackdrop')
            background.setScaledContents(True)
            background_path = self.image_lookup(anime)

            if background_path:

                background.setPixmap(QPixmap(background_path))
                blur = QGraphicsBlurEffect(background)
                blur.setBlurRadius(28)
                background.setGraphicsEffect(blur)

            hero_stack.addWidget(background)

            overlay = QFrame()
            overlay.setObjectName('DetailOverlay')
            hero_stack.addWidget(overlay)

            hero_content = QHBoxLayout(overlay)
            hero_content.setContentsMargins(20, 18, 20, 18)
            hero_content.setSpacing(18)

            poster = QLabel()
            poster.setObjectName('DetailPoster')
            poster.setFixedSize(220, 300)
            poster.setAlignment(Qt.AlignmentFlag.AlignCenter)
            poster_path = self.image_lookup(anime)

            if poster_path:

                pixmap = QPixmap(poster_path)

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

            hero_content.addWidget(poster)

            info = QVBoxLayout()
            info.setSpacing(8)
            title = QLabel(anime['title'])
            title.setObjectName('DetailTitle')
            title.setWordWrap(True)
            info.addWidget(title)

            rating = self.value(anime.get('rating'))
            year = self.value(anime.get('year'))
            status = self.value(anime.get('status'))
            info.addWidget(QLabel(f'★ {rating}   ·   {year}   ·   {status}'))
            info.addWidget(QLabel(', '.join(anime.get('genres', []))))

            episode_value = (
                f"{anime.get('known_episodes')}+"
                if not anime.get('episodes_complete')
                else anime.get('known_episodes')
            )
            info.addWidget(QLabel(
                f"{anime.get('part_count', 1)} parts   ·   "
                f"{self.value(episode_value)} episodes"
            ))

            actions = QHBoxLayout()
            favorite = QPushButton()
            favorite.setIcon(make_icon(
                'heart_filled' if is_favorite(anime['id']) else 'heart'
            ))
            favorite.setObjectName('FavoriteButton')
            favorite.setToolTip(
                'Remove from favorites' if is_favorite(anime['id'])
                else 'Add to favorites'
            )
            favorite.setFixedSize(46, 42)
            favorite.clicked.connect(
                lambda: self.toggle_detail_favorite(anime['id'])
            )
            actions.addWidget(favorite)

            list_button = QPushButton('Add to lists')
            list_button.setIcon(make_icon('add'))
            list_button.clicked.connect(
                lambda: self.open_list_selector(anime['id'])
            )
            actions.addWidget(list_button)
            actions.addStretch()
            info.addLayout(actions)
            info.addStretch()
            hero_content.addLayout(info, 1)
            page_layout.addWidget(hero)

            lower = QHBoxLayout()
            lower.setSpacing(14)

            stats = QFrame()
            stats.setObjectName('DetailStats')
            stats_layout = QVBoxLayout(stats)
            stats_layout.addWidget(QLabel('Franchise overview'))
            stats_layout.addWidget(QLabel(f"Parts: {anime.get('part_count', 1)}"))
            stats_layout.addWidget(QLabel(f"Known episodes: {self.value(episode_value)}"))
            stats_layout.addWidget(QLabel(f"Start year: {year}"))
            stats_layout.addWidget(QLabel(f"Status: {status}"))
            stats_layout.addStretch()
            lower.addWidget(stats, 0)

            biography = QFrame()
            biography.setObjectName('BiographyPanel')
            bio_layout = QVBoxLayout(biography)
            bio_layout.addWidget(QLabel('Biography'))
            description = QLabel(self.value(self.offline_description(anime)))
            description.setWordWrap(True)
            description.setMaximumHeight(118)
            bio_layout.addWidget(description)
            bio_layout.addStretch()
            lower.addWidget(biography, 1)
            page_layout.addLayout(lower)

            parts_title = QLabel('Seasons, OVAs and Movies')
            parts_title.setObjectName('SectionTitle')
            page_layout.addWidget(parts_title)
            parts_scroll = QScrollArea()
            parts_scroll.setWidgetResizable(True)
            parts_scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            parts_scroll.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            parts_scroll.setFrameShape(QFrame.Shape.NoFrame)
            parts_content = QWidget()
            parts_row = QHBoxLayout(parts_content)
            parts_row.setContentsMargins(2, 2, 2, 8)
            parts_row.setSpacing(10)

            for part in anime.get('parts', []):

                part_card = AnimeCard(part, self.image_lookup)
                part_card.setFixedWidth(150)
                part_card.opened.connect(
                    lambda part_id: self.show_detail(
                        part_id,
                        self.detail_page
                    )
                )
                part_card.favorite_changed.connect(self.refresh_visible_cards)
                self.visible_cards.setdefault(part['id'], []).append(part_card)
                parts_row.addWidget(part_card)
                self.image_manager.request(part)

            parts_row.addStretch()
            parts_scroll.setWidget(parts_content)
            parts_scroll.setMaximumHeight(300)
            page_layout.addWidget(parts_scroll)

        if dialog.exec() != QDialog.DialogCode.Accepted:

            return

        selected = {
            list_id
            for list_id, check in checks
            if check.isChecked()
        }
        existing = current_ids

        for list_id in selected - existing:

            add_anime_to_list(list_id, anime_id)

        from database.lists import remove_anime_from_list

        for list_id in existing - selected:

            remove_anime_from_list(list_id, anime_id)

        self.show_detail(anime_id, self.detail_return_page)

    def create_list_from_selector(self, dialog, anime_id):

        name, accepted = QInputDialog.getText(
            dialog,
            'Create list',
            'Name:'
        )

        if accepted and create_list(name):

            dialog.done(QDialog.DialogCode.Accepted)
            self.open_list_selector(anime_id)

        """

    def render_detail(self, anime, online):

        root_layout = self.detail_page.layout()

        if root_layout is None:

            root_layout = QVBoxLayout(self.detail_page)
            root_layout.setContentsMargins(0, 0, 0, 0)
            self.detail_scroll = QScrollArea()
            self.detail_scroll.setWidgetResizable(True)
            self.detail_scroll.setFrameShape(QFrame.Shape.NoFrame)
            self.detail_scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            detail_content = QWidget()
            self.detail_content_layout = QVBoxLayout(detail_content)
            self.detail_content_layout.setContentsMargins(4, 4, 10, 18)
            self.detail_content_layout.setSpacing(14)
            self.detail_scroll.setWidget(detail_content)
            root_layout.addWidget(self.detail_scroll)

        page_layout = self.detail_content_layout

        self.clear_layout(page_layout)

        back = QPushButton('Back')
        back.setIcon(make_icon('back'))
        back.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.detail_return_page)
        )
        page_layout.addWidget(back, alignment=Qt.AlignmentFlag.AlignLeft)

        hero = QFrame()
        hero.setObjectName('DetailHero')
        stack = QStackedLayout(hero)
        stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        backdrop = QLabel()
        backdrop.setObjectName('DetailBackdrop')
        backdrop.setScaledContents(True)
        path = self.image_lookup(anime)

        if path:

            backdrop.setPixmap(QPixmap(path))
            blur = QGraphicsBlurEffect(backdrop)
            blur.setBlurRadius(28)
            backdrop.setGraphicsEffect(blur)

        stack.addWidget(backdrop)

        overlay = QFrame()
        overlay.setObjectName('DetailOverlay')
        overlay.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            True
        )
        stack.addWidget(overlay)
        backdrop.lower()
        overlay.raise_()
        hero_layout = (
            QVBoxLayout(overlay)
            if self.is_mobile
            else QHBoxLayout(overlay)
        )
        hero_layout.setContentsMargins(20, 18, 20, 18)
        hero_layout.setSpacing(18)

        poster = QLabel()
        poster.setObjectName('DetailPoster')
        poster.setFixedSize(220, 300)
        poster.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

        if self.is_mobile:

            hero_layout.setAlignment(
                poster,
                Qt.AlignmentFlag.AlignHCenter
            )

        hero_layout.addWidget(poster)

        info = QVBoxLayout()
        title = QLabel(anime['title'])
        title.setObjectName('DetailTitle')
        title.setWordWrap(True)
        info.addWidget(title)

        rating = self.value(anime.get('rating'))
        year = self.value(anime.get('year'))
        status = self.value(anime.get('status'))
        info.addWidget(QLabel(f'★ {rating}   ·   {year}   ·   {status}'))
        info.addWidget(QLabel(', '.join(anime.get('genres', []))))

        episode_value = anime.get('known_episodes', anime.get('episodes'))
        if not anime.get('episodes_complete', True):
            episode_value = f'{episode_value}+'

        info.addWidget(QLabel(
            f"{anime.get('part_count', 1)} parts   ·   "
            f"{self.value(episode_value)} episodes"
        ))

        actions = QHBoxLayout()
        favorite = QPushButton()
        favorite.setIcon(make_icon(
            'heart_filled' if is_favorite(anime['id']) else 'heart'
        ))
        favorite.setObjectName('FavoriteButton')
        favorite.setToolTip(
            'Remove from favorites' if is_favorite(anime['id'])
            else 'Add to favorites'
        )
        favorite.setFixedSize(46, 42)
        favorite.clicked.connect(
            lambda: self.toggle_detail_favorite(anime['id'])
        )
        actions.addWidget(favorite)

        list_button = QPushButton('Add to lists')
        list_button.setIcon(make_icon('add'))
        list_button.clicked.connect(
            lambda: self.open_list_selector(anime['id'])
        )
        actions.addWidget(list_button)
        actions.addStretch()
        info.addLayout(actions)
        info.addStretch()
        hero_layout.addLayout(info, 1)
        page_layout.addWidget(hero)

        lower = (
            QVBoxLayout()
            if self.is_mobile
            else QHBoxLayout()
        )
        stats = QFrame()
        stats.setObjectName('DetailStats')
        stats_layout = QVBoxLayout(stats)
        stats_layout.addWidget(QLabel('Franchise overview'))
        stats_layout.addWidget(QLabel(f"Parts: {anime.get('part_count', 1)}"))
        stats_layout.addWidget(QLabel(f"Known episodes: {self.value(episode_value)}"))
        stats_layout.addWidget(QLabel(f'Start year: {year}'))
        stats_layout.addWidget(QLabel(f'Status: {status}'))
        stats_layout.addStretch()
        lower.addWidget(stats)

        biography = QFrame()
        biography.setObjectName('BiographyPanel')
        bio_layout = QVBoxLayout(biography)
        bio_layout.addWidget(QLabel('Biography'))
        description = QLabel(self.value(self.offline_description(anime)))
        description.setWordWrap(True)
        description.setMaximumHeight(118)
        bio_layout.addWidget(description)
        bio_layout.addStretch()
        lower.addWidget(biography, 1)
        page_layout.addLayout(lower)

        parts_title = QLabel('Seasons, OVAs and Movies')
        parts_title.setObjectName('SectionTitle')
        page_layout.addWidget(parts_title)
        parts_panel = QFrame()
        parts_panel.setObjectName('PartsPanel')
        parts_grid = QGridLayout(parts_panel)
        parts_grid.setContentsMargins(10, 10, 10, 10)
        parts_grid.setHorizontalSpacing(10)
        parts_grid.setVerticalSpacing(12)

        part_columns = 2 if self.is_mobile else 6

        for index, part in enumerate(anime.get('parts', [])):

            part_card = PartCard(part, self.image_lookup)
            part_card.opened.connect(
                lambda part_id: self.show_detail(
                    part_id,
                    self.detail_return_page
                )
            )
            parts_grid.addWidget(
                part_card,
                index // part_columns,
                index % part_columns
            )
            self.image_manager.request(part)

        page_layout.addWidget(parts_panel)

    def open_list_selector(self, anime_id):

        dialog = QDialog(self)
        dialog.setWindowTitle('Add to lists')
        dialog.setMinimumWidth(320)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel('Select lists for this anime.'))
        current_ids = {item['id'] for item in get_anime_lists(anime_id)}
        checks = []

        for item in get_lists():

            check = QCheckBox(item['name'])
            check.setChecked(item['id'] in current_ids)
            checks.append((item['id'], check))
            layout.addWidget(check)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:

            return

        selected = {list_id for list_id, check in checks if check.isChecked()}
        from database.lists import remove_anime_from_list

        for list_id in selected - current_ids:

            add_anime_to_list(list_id, anime_id)

        for list_id in current_ids - selected:

            remove_anime_from_list(list_id, anime_id)

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
                    next(
                        item
                        for item in self.animes
                        if item['id'] == anime_id
                    ),
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

    @staticmethod
    def offline_description(anime):

        if anime.get('synopsis'):

            return anime['synopsis']

        genres = ', '.join(anime.get('genres', [])) or 'multiple genres'
        year = anime.get('year') or 'an unknown year'
        episodes = anime.get('episodes')
        status = anime.get('status') or 'status not specified'

        if episodes:

            format_text = f'{episodes} episodes'

        else:

            format_text = 'episode count not specified'

        return (
            f"{anime['title']} is a {genres} anime from {year}. "
            f"The local catalog lists {format_text} and a status of {status}. "
            'A full plot synopsis is available when online AniList data is cached.'
        )
