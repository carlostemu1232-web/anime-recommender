# 🎌 Anime Recommender

Anime Recommender is a Python desktop application that recommends anime from a local SQLite database using genres, ratings, years and episode filters.

The project includes a local master catalog of **200 anime**, so the application does not depend on external APIs or an internet connection during execution.

## 🚀 Version

**Current version: v0.6.1**

v0.6.1 is a stabilization and catalog-improvement release following v0.6.

This version focuses on completing and validating the local catalog, improving SQLite synchronization, and keeping the recommendation system fully local and independent from external APIs.

## ✨ Features

* 🎌 Local anime recommendation system
* 🎭 Search and filter by genre
* 🎭 Select up to 3 genres
* ⭐ Rating-based recommendation ranking
* 📅 Year information
* 🎬 Episode filtering
* 📺 Under 50 episodes
* 📺 50+ episodes
* 💾 Local SQLite database
* 📊 Recommendation ranking by matching genres, rating and release year
* 🔄 Automatic catalog import and synchronization
* 🖥️ Tkinter graphical interface
* 📦 Local master catalog containing 200 anime
* 🔌 No external APIs required during execution

## 🧠 Recommendation System

The recommendation system uses the genres selected by the user to determine the most relevant anime.

Recommendations are ranked using:

1. Number of matching genres
2. Anime rating
3. Release year

Anime matching more of the selected genres receives a higher recommendation priority.

### Episode Filtering

Episode count is used as a **filter**, rather than as a ranking criterion.

Available options:

* `All episodes`
* `Under 50 episodes`
* `50+ episodes`

Anime entries with unknown episode counts are only included when `All episodes` is selected.

The application displays a maximum of **10 recommendations**.

## 💾 Local Database

The application uses SQLite as its local database.

The database contains three main tables:

* `animes`
* `genres`
* `anime_genres`

The local master catalog is stored in:

```text
database/catalog.py
```

The SQLite database is stored in:

```text
database/anime.db
```

The master catalog is the source of truth used to synchronize the SQLite database.

## 📊 Catalog Status

The v0.6.1 catalog has been validated with:

* **200 anime** in the master catalog
* **200 anime** in SQLite
* **200 unique franchises**
* **0 NULL values** in rating
* **0 NULL values** in year
* **0 NULL values** in episodes
* **0 NULL values** in status

The catalog contains the following visible recommendation genres:

* `action`
* `fantasy`
* `comedy`
* `drama`
* `school`
* `adventure`
* `romance`
* `isekai`

## 📝 Metadata

Some metadata fields are intentionally left empty in the current version.

The following fields are currently not populated:

* `synopsis`
* `image_url`
* `trailer_url`

No information is automatically invented for these fields.

They may be completed in a future version using a reliable source or manually reviewed data.

## 🔄 Catalog Import

The catalog can be imported or synchronized manually with:

```bash
python database/importer.py
```

The importer uses `franchise` as the logical identifier of an anime.

For each anime it:

1. Inserts or updates the anime record.
2. Removes previous genre relationships.
3. Adds the current genres.
4. Recreates the corresponding `anime_genres` relationships.

When the application starts, it also checks whether the database is empty and automatically imports the master catalog if necessary.

## ▶️ Run the Application

From the project directory:

```bash
python main.py
```

Example on Windows:

```bash
python main.py
```

## 🔧 Requirements

* Python 3.13+
* Tkinter
* SQLite3

SQLite and Tkinter are included with standard Python installations on most Windows Python distributions.

No external Python packages or internet connection are required to run the application.

## 📁 Project Structure

```text
anime-app/
│
├── main.py
│   └── Tkinter graphical interface
│
├── database/
│   ├── __init__.py
│   │
│   ├── anime.db
│   │   └── Local SQLite database
│   │
│   ├── catalog.py
│   │   └── Master catalog of 200 anime
│   │
│   ├── database.py
│   │   └── SQLite schema, queries and recommendation filtering
│   │
│   ├── importer.py
│   │   └── Catalog importer and synchronization
│   │
│   └── test_database.py
│       └── Database checks
│
├── user_data/
│   └── Local user data
│
├── README.md
│   └── Project documentation
│
└── PROJECT_CONTEXT.md
    └── Development context and architecture notes
```

## 🧪 Testing

The v0.6.1 version has been validated with:

* Python compilation checks
* SQLite database creation
* Catalog import
* Catalog/database synchronization
* Genre filtering
* Multiple genre selection
* Episode filtering
* Recommendation ranking
* Isekai recommendations
* Action recommendations with fewer than 50 episodes

Compilation can be checked with:

```bash
python -m py_compile main.py database/database.py database/catalog.py database/importer.py database/test_database.py
```

The catalog importer can be tested with:

```bash
python database/importer.py
```

The application can be started with:

```bash
python main.py
```

## ⚠️ Current Limitations

The following metadata is intentionally not available yet:

* Anime synopsis
* Anime images
* Trailer links

These fields will not be populated with invented information.

The current recommendation system is also limited to the genres available in the local catalog and the filters implemented in the Tkinter interface.

## 🛣️ Roadmap

Possible future improvements:

* 🔎 Search anime by title
* ⭐ Rating filter
* 📅 Year filter
* 📺 Status filter
* 🧠 Improved recommendation scoring
* 🎯 Greater recommendation variety
* 🖥️ Improved result interface
* 🗂️ Result cards or `Treeview`
* 📝 Reliable anime synopsis data
* 🖼️ Anime images from a reliable source
* 🎬 Trailer links from a reliable source
* 🧪 Formal `pytest` test suite
* 🧱 Further separation of the Tkinter interface into classes and components

## 📜 Version History

### v0.6.1

* Completed and validated the local catalog metadata
* Maintained a 200-anime master catalog
* Validated 200 unique franchises
* Improved SQLite catalog synchronization
* Added and validated core metadata for the catalog
* Maintained local genre filtering
* Maintained multiple genre selection
* Maintained episode filtering
* Maintained recommendation ranking
* Removed reliance on external APIs
* Kept synopsis, image and trailer fields intentionally empty
* Validated the active project modules

### v0.6

* Added local SQLite anime system
* Added 200-anime master catalog
* Added genre filtering
* Added multiple genre selection
* Added episode filtering
* Improved recommendation ranking
* Stabilized the graphical interface

---

Made with Python 🐍, Tkinter 🎌 and SQLite 💾

