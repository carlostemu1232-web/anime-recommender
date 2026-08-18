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
    background: #151515;
    color: #f4f7fb;
    font-family: Arial;
    font-size: 13px;
}
QMainWindow {
    background: #151515;
}
#Shell {
    background: #151515;
}
#Brand {
    color: #ff6a00;
    font-size: 30px;
    font-weight: 800;
}
#PageTitle {
    font-family: Outfit;
    color: #f4f7fb;
    font-size: 24px;
    font-weight: 700;
}
#PrincipalTitle {
    font-family: Outfit;
    color: #ffffff;
    font-size: 40px;
    font-weight: 800;
}
#SectionTitle {
    font-family: Outfit;
    color: #f4f7fb;
    font-size: 20px;
    font-weight: 700;
}
#Hero {
    background: #202020;
    border: 1px solid #333333;
    border-radius: 14px;
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
    background: #202020;
    border: 1px solid #333333;
    border-radius: 12px;
}
#AnimeCard:hover {
    border: 1px solid #ff6a00;
}
#CardPoster, #DetailPoster {
    background: #282828;
    border-radius: 8px;
    color: #bdbdbd;
}
#CardTitle, #ListButton {
    font-family: Outfit;
    background: transparent;
    border: none;
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
}
#CardTitle:hover, #ListButton:hover {
    color: #ff7a1a;
}
#Muted, #Status {
    color: #bdbdbd;
}
#FavoriteButton {
    background: #282828;
    border: 1px solid #555555;
    border-radius: 8px;
    color: #ff6a00;
    font-size: 20px;
}
QPushButton {
    background: #282828;
    border: 1px solid #444444;
    border-radius: 8px;
    padding: 9px 14px;
}
QPushButton:hover {
    background: #333333;
}
QComboBox, QLineEdit, QTextBrowser, QListWidget {
    background: #202020;
    border: 1px solid #444444;
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
