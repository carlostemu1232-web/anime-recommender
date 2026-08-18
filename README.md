# 🎌 Anime Recommender

Anime Recommender is a Python desktop application that recommends anime from a local SQLite database using genres, ratings, years and episode counts.

The project includes a local catalog of 200 anime, so it does not depend on external APIs or an internet connection.

## 🚀 Version

**Current version: v0.6**

The v0.6 release is considered a stable version of the project before starting development of v0.6.1v.

## ✨ Features

* 🎌 Anime recommendation system
* 🎭 Search by genre
* 🎭 Select up to 3 genres
* ⭐ Rating-based recommendations
* 📅 Year information
* 🎬 Episode filtering
* 📺 Under 50 episodes
* 📺 50+ episodes
* 💾 Local SQLite catalog
* 📊 Ranking by matching genres, rating and release year
* 🔄 Catalog import and update from the local master catalog
* 🖥️ Simple Tkinter graphical interface

## 🧠 Recommendation System

The recommendation system considers:

1. Selected genres
2. Number of matching genres
3. Anime rating
4. Anime release year
5. Episode count

Anime matching more selected genres receives a higher recommendation priority.

## 🔧 Requirements

* Python 3.13+
* Tkinter

Tkinter is included with standard Python installations on Windows.

## ▶️ Run the application

From the project directory:

```bash
python main.py
```

Example on Windows:

```bash
python main.py
```

## 📁 Project Structure

```text
anime-app/
│
├── main.py
│   └── Graphical user interface
│
├── database/
│   ├── database.py
│   │   └── SQLite schema, queries and filtering logic
│   ├── catalog.py
│   │   └── Local catalog of 200 anime
│   ├── importer.py
│   │   └── Catalog importer
│   └── test_database.py
│       └── Database checks
│
├── README.md
│   └── Project documentation
│
└── .gitignore
    └── Files ignored by Git
```

## 🧪 v0.6 Testing

The v0.6 version has been tested with:

* Action
* Romance
* Isekai
* Fantasy
* Drama
* Comedy
* Horror
* Mystery
* Psychological
* School
* Multiple genres
* Under 50 episodes
* 50+ episodes

The application was tested with the local SQLite catalog and its genre and episode filters.

## ⚠️ Current Limitations

Some catalog entries still need complete episode and rating metadata.

These fields can be completed directly in the local catalog.

## 🛣️ Roadmap

### Future versions

Possible future improvements:

* Better anime season detection
* Better duplicate detection
* Improved recommendation scoring
* More recommendation variety
* Complete missing episode and rating metadata
* Improved user interface

## 📜 Version History

### v0.6

* Added local SQLite anime system
* Added 200-anime master catalog
* Added genre filtering
* Added multiple genre selection
* Added episode filtering
* Improved recommendation ranking
* Stabilized the graphical interface

---

Made with Python 🐍 and Tkinter 🎌
