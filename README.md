# 🎌 Anime Recommender

Anime Recommender is a Python desktop application that recommends anime based on genres, episode count and search type.

The project uses multiple anime APIs and combines their results to provide recommendations.

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
* 🔥 Trending anime
* 🆕 Recent anime
* 🏆 Top anime
* 🔄 Results from multiple APIs
* 🧩 Automatic API fallback
* 📊 Unified results from different sources
* 🛡️ Application continues working when one or more APIs fail
* 🖥️ Simple Tkinter graphical interface

## 🌐 APIs

The project currently uses:

* Jikan
* Kitsu
* AniList

AniList is currently the main source for obtaining a larger number of results, while Jikan and Kitsu are used as additional sources when available.

The application does not require all APIs to work simultaneously.

If an API fails, the application continues using the available sources.

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
* `requests`
* Tkinter

Install the Python dependency with:

```bash
pip install requests
```

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
├── api_sources.py
│   └── API connections and anime data processing
│
├── api_practice.py
│   └── Recommendation and filtering logic
│
├── requirements.txt
│   └── Python dependencies
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
* Trending
* Recent
* Top

The application was also tested with API failures to verify that it can continue operating with fewer available sources.

## ⚠️ Current Limitations

Some APIs can occasionally return errors or take longer to respond.

Genre-specific results can also have limited variety depending on the API and the current data available.

In particular, highly specific genres such as Isekai may return fewer results than broader genres such as Action or Romance.

These limitations are planned for future versions.

## 🛣️ Roadmap

### v0.6.1v — Genre Sources

The next version will investigate specialized sources for important genres.

Planned areas include:

* 🌀 Isekai
* 💕 Romance
* 🧙 Fantasy
* ⚔️ Action
* 🧠 Psychological
* 👻 Horror

The goal is to increase variety for specific genres while keeping the existing APIs as general sources.

### Future versions

Possible future improvements:

* Better anime season detection
* Better duplicate detection
* Improved recommendation scoring
* More recommendation variety
* Better handling of API failures
* More specialized genre sources
* Improved user interface

## 📜 Version History

### v0.6

* Added multi-API anime system
* Added Jikan, Kitsu and AniList integration
* Added API fallback system
* Added genre filtering
* Added multiple genre selection
* Added episode filtering
* Added Trending / Recent / Top modes
* Added unified anime results
* Added larger AniList result sets
* Improved API error handling
* Improved recommendation ranking
* Stabilized the graphical interface

---

Made with Python 🐍 and Tkinter 🎌
