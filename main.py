import os
import sys

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from database.database import create_database, get_all_animes
from database.favorites import create_favorites_database
from database.importer import import_catalog
from database.lists import create_lists_database
from ui.main_window import AnimeWindow


APP_NAME = 'AniVerse'

THEME = '''
QWidget {
    background: #0f1726;
    color: #d7deea;
    font-family: Arial;
    font-size: 13px;
}
QLabel {
    background: transparent;
}
QMainWindow {
    background: #0f1726;
}
#Shell {
    background: #0f1726;
}
#Sidebar {
    background: #111111;
    border-right: 1px solid #333333;
}
#Brand {
    color: #a9c7ef;
    font-size: 24px;
    font-weight: 800;
}
#TopSearch {
    background: #202020;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 10px 14px;
    color: #ffffff;
}
#TopSearch:focus {
    border: 1px solid #555555;
}
#Avatar {
    background: #282828;
    border: 1px solid #555555;
    border-radius: 17px;
    color: #ff6a00;
    font-family: Outfit;
    font-weight: 800;
}
#SideNavButton {
    background: transparent;
    border: none;
    border-radius: 7px;
    color: #bdbdbd;
    padding: 10px 4px;
    font-size: 11px;
}
#SideNavButton:hover, #SideNavButton:pressed {
    background: #282828;
    color: #ffffff;
}
#GenreChoice {
    background: #172235;
    border: 1px solid #344c6a;
    border-radius: 8px;
    color: #d7deea;
    min-height: 42px;
}
#GenreChoice:hover {
    background: #263c59;
}
#GenreChoice:checked {
    background: #355b89;
    border: 1px solid #9fc5f8;
    color: #ffffff;
}
#RandomPanel {
    background: rgba(23, 34, 53, 165);
    border: 1px solid rgba(52, 76, 106, 120);
    border-radius: 10px;
}
#RandomResults {
    background: transparent;
    border: none;
}
#PageTitle {
    font-family: Outfit;
    color: #d7deea;
    font-size: 24px;
    font-weight: 700;
}
#PrincipalTitle {
    font-family: Outfit;
    color: #e5ebf5;
    font-size: 40px;
    font-weight: 800;
}
#SectionTitle {
    font-family: Outfit;
    color: #f4f7fb;
    font-size: 20px;
    font-weight: 700;
}
#SeeMoreButton {
    background: transparent;
    border: none;
    color: #9fc5f8;
    padding: 4px 8px;
    font-size: 12px;
}
#SeeMoreButton:hover {
    color: #ffffff;
}
#Hero {
    background: #172235;
    border: 1px solid #263750;
    border-radius: 14px;
}
#HomeSection {
    background: rgba(23, 34, 53, 150);
    border: 1px solid rgba(52, 76, 106, 110);
    border-radius: 10px;
}
#DetailProfile {
    background: #202020;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 6px;
}
#DetailHero {
    min-height: 330px;
    background: #172235;
    border: 1px solid #263750;
    border-radius: 14px;
    overflow: hidden;
}
#PartsPanel {
    background: #202020;
    border: 1px solid #333333;
    border-radius: 12px;
}
#DetailBackdrop {
    background: #202020;
    opacity: 0.42;
}
#DetailOverlay {
    background: rgba(7, 12, 20, 225);
}
#DetailStats, #BiographyPanel {
    background: rgba(23, 34, 53, 190);
    border: 1px solid rgba(52, 76, 106, 120);
    border-radius: 10px;
    padding: 8px;
}
#DetailOverlay QLabel {
    color: #d7deea;
    background: transparent;
}
#HeroTitle {
    font-family: Outfit;
    color: #ffffff;
    font-size: 32px;
    font-weight: 800;
}
#BottomNav {
    background: #202020;
    border: 1px solid #333333;
    border-radius: 14px;
}
#NavButton {
    background: transparent;
    border: none;
    color: #bdbdbd;
    padding: 8px 4px;
    border-radius: 10px;
}
#NavButton:hover {
    background: #282828;
    color: #ffffff;
}
#AnimeCard, #ListRow {
    background: transparent;
    border: none;
    border-radius: 8px;
}
#AnimeCard:hover {
    background: rgba(35, 52, 78, 130);
}
#CardPoster, #DetailPoster {
    background: #21314a;
    border: 1px solid #333333;
    border-radius: 8px;
    color: #aebbd0;
}
#PartCard {
    background: rgba(23, 34, 53, 160);
    border: none;
    border-radius: 8px;
}
#PartCard:hover {
    background: rgba(45, 67, 98, 180);
}
#PartPoster {
    background: #21314a;
    border-radius: 6px;
    color: #aebbd0;
}
#PartTitle {
    color: #d7deea;
    font-family: Outfit;
    font-size: 12px;
    font-weight: 600;
}
#CardTitle, #ListButton {
    font-family: Outfit;
    background: transparent;
    border: none;
    color: #e5ebf5;
    font-size: 15px;
    font-weight: 700;
}
#CardTitle:hover, #ListButton:hover {
    color: #a9c7ef;
}
#Muted, #Status {
    color: #aebbd0;
}
#FavoriteButton {
    background: #21314a;
    border: 1px solid #49627f;
    border-radius: 8px;
    color: #a9c7ef;
    font-size: 20px;
}
QPushButton {
    background: #1b2a40;
    border: 1px solid #354c6a;
    border-radius: 8px;
    padding: 9px 14px;
}
QPushButton:hover {
    background: #263c59;
}
QComboBox, QLineEdit, QTextBrowser, QListWidget {
    background: #172235;
    border: 1px solid #354c6a;
    border-radius: 8px;
    padding: 8px;
    color: #f4f7fb;
}
QComboBox QAbstractItemView {
    background: #202020;
    color: #f4f7fb;
}
QScrollArea {
    background: transparent;
    border: none;
}
'''


def build_splash():

    pixmap = QPixmap(560, 340)
    pixmap.fill(QColor('#151515'))
    painter = QPainter(pixmap)
    painter.setPen(QColor('#f4f7fb'))
    painter.setFont(QFont('Outfit', 30, QFont.Weight.Bold))
    painter.drawText(
        pixmap.rect().adjusted(0, -30, 0, 0),
        Qt.AlignmentFlag.AlignCenter,
        APP_NAME
    )
    painter.setPen(QColor('#ff6a00'))
    painter.setFont(QFont('DM Sans', 14))
    painter.drawText(
        pixmap.rect().adjusted(0, 80, 0, 0),
        Qt.AlignmentFlag.AlignCenter,
        'Loading your local catalog...'
    )
    painter.end()
    return QSplashScreen(pixmap)


def load_fonts():

    font_folder = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        'assets',
        'fonts'
    )

    families = {}

    for filename, key in (
        ('Outfit.ttf', 'display'),
        ('DMSans.ttf', 'body')
    ):

        font_id = QFontDatabase.addApplicationFont(
            os.path.join(font_folder, filename)
        )

        if font_id != -1:

            loaded_families = QFontDatabase.applicationFontFamilies(
                font_id
            )

            if loaded_families:

                families[key] = loaded_families[0]

    return families


def prepare_data():

    create_database()

    if not get_all_animes():

        import_catalog()

    create_favorites_database()
    create_lists_database()


def main():

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    families = load_fonts()
    app.setProperty('displayFont', families.get('display', 'Outfit'))
    app.setProperty('bodyFont', families.get('body', 'DM Sans'))
    app.setFont(QFont(families.get('body', 'DM Sans'), 13))
    app.setStyleSheet(
        THEME.replace(
            'Arial',
            families.get('body', 'DM Sans')
        ).replace(
            'font-weight: 800;',
            f"font-family: '{families.get('display', 'Outfit')}'; font-weight: 800;"
        )
    )
    splash = build_splash()
    splash.show()
    app.processEvents()

    def launch():

        prepare_data()
        window = AnimeWindow()
        window.show()
        splash.finish(window)
        app.window = window

    QTimer.singleShot(450, launch)
    sys.exit(app.exec())


if __name__ == '__main__':

    main()
