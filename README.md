# 🎌 AniVerse

AniVerse is a Python desktop anime application focused on discovering, searching and organizing anime through a modern visual interface.

The application uses a local SQLite catalog and optionally uses AniList to enrich anime details with images, synopsis, trailers and streaming information.

The core application can work offline.

---

## 🚀 Version

**Current version: v0.8**

v0.8 consolidates the 1000-anime local catalog, franchise grouping, visual Home, Random discovery and asynchronous image loading.

---

## ✨ Features

### 🎨 Modern interface

- Modern dark anime-inspired design
- Mobile-inspired layout
- Visual anime cards
- Large anime artwork
- Rounded components
- Improved spacing and hierarchy
- Bottom navigation
- Custom icons with transparent backgrounds
- AniVerse branding

### 🔤 Typography

The interface uses:

- **Outfit** for titles, headings and important UI elements
- **DM Sans** for normal text, metadata and navigation

### 🏠 Home

The home page provides:

- A Principal heading
- Horizontal recommendations
- A single vertical scroll containing all sections
- Featured anime
- Persistent horizontal rows for Action, Fantasy, Comedy, Drama, School, Adventure, Romance and Isekai
- One visual franchise card per section
- Visual anime cards with poster and title below
- One vertical page with persistent genre sections
- Five initial cards per section with `See more`
- Featured, Action, Fantasy, Comedy, Drama, School, Adventure, Romance and Isekai rows

### 🔥 Recommendations

Recommendations use the local SQLite catalog and are ranked by:

1. Matching genres
2. Rating
3. Release year

Users can filter anime by genre and episode count.

### ⭐ Top anime by genre

Users can select a genre and browse the highest-rated anime within that genre.

Genres are obtained directly from SQLite.

### 🔎 Search

A dedicated search section allows users to search the complete local anime catalog.

Search supports:

- Anime title
- Original title when available

Search does not require an Internet connection.

### 🪄 Random discovery

Random discovery is a separate navigation section. It uses one selected genre, a popularity category and five random franchise results.

Available categories:

- Any popularity
- Very popular
- Popular
- Hidden gems

Popularity categories are mutually exclusive. A franchise can only belong to one category in a Random search. The local classification uses average rating, confirmed franchise parts and known episodes.

### ❤️ Favorites

Users can add or remove anime from favorites directly from cards or anime detail pages.

Favorites are persistent and stored separately from the main anime catalog.

### 📚 Custom lists

Users can create personalized anime lists such as:

- Watching
- Watched
- On Hold
- Plan to Watch
- Favorites

Users can also create completely custom lists.

List management includes:

- Create
- Rename
- Delete
- Add anime
- Remove anime

User data is stored separately from the main catalog.

### 🎬 Anime details

Anime detail pages can display:

- Poster
- Title
- Original title
- Rating
- Year
- Episodes
- Status
- Genres
- Synopsis
- Streaming information
- Trailer
- Favorite status
- Lists
- Compact synopsis
- Related seasons, OVAs, specials and movies when explicitly grouped

The detail page does not display a streaming or "Where to watch" section.

Franchise details keep individual seasons, OVAs, specials and movies internally while presenting the franchise as one visual entity. Known episode totals are summed without converting unknown values into zero.

### 🌐 AniList enrichment

AniList is an optional enrichment source.

It can provide:

- Synopsis
- Cover images
- Trailers
- Streaming information

Data is cached locally to reduce repeated requests.

The application continues working when AniList or the Internet is unavailable.

The 1000-anime catalog and factual offline descriptions are stored locally. Internet access is only needed for optional poster enrichment and other AniList media.

### 🖼️ Image system

v0.7 uses a shared asynchronous image manager.

Images can be loaded directly in:

- Home
- Search
- Favorites
- Lists
- Anime cards
- Anime details

Images are loaded asynchronously and cached locally when possible.

The shared image manager provides:

- In-memory path reuse
- Disk cache reuse from `database/anilist_images/`
- Deduplicated in-flight requests by franchise
- Loading and unavailable placeholders
- Automatic card updates through Qt signals

If an image is unavailable, AniVerse displays a placeholder instead of an error.

`database/image_manager.py` provides memory reuse, local disk cache reuse, background requests, duplicate-request prevention and Qt callbacks for updating cards without opening Details.

---

## 📴 Offline-first design

The core recommendation and search system uses the local SQLite database.

The application does not require Internet access for:

- Search
- Recommendations
- Genre filtering
- Episode filtering
- Ratings
- Years
- Favorites
- Custom lists

AniList is only used as optional enrichment.

---

## 🗃️ Database

Main database:

```text
database/anime.db
Main tables:

animes
genres
anime_genres

Current catalog:

1000 anime
1000 SQLite records
1000 unique internal franchise identifiers

Current visual franchise groups: 818 after the latest audit.

Exact visual duplicate titles: 0.

The master catalog is located in:

database/catalog.py

The additional AniList-verified records are stored in `database/catalog_extra.py` and imported by `database/catalog.py` as part of the master catalog.
📁 Project structure
anime-app/
├── main.py
├── README.md
├── PROJECT_CONTEXT.md
│
├── assets/
│   ├── fonts/
│   └── icons/
│
├── user_data/
│
└── database/
    ├── anime.db
    ├── favorites.py
    ├── anilist.py
    ├── anilist_cache.json
    ├── anilist_images/
    ├── image_manager.py
    ├── franchises.py
    ├── catalog_extra.py
    ├── enrich_metadata.py
    ├── catalog.py
    ├── database.py
    ├── importer.py
    └── test_database.py
🔧 Requirements
Python 3.13+
PySide6

Internet access is optional.

▶️ Run

From the project directory:

python main.py
🔄 Update the catalog
python database/importer.py

The importer preserves all 1000 individual SQLite records. Franchise grouping is a presentation layer and does not delete seasons or movies.
🧪 Validation

Compile the main modules:

python -m py_compile main.py database/database.py database/catalog.py database/importer.py database/test_database.py

The application should also be tested manually for:

Startup
Navigation
Recommendations
Search
Anime details
Image loading
Favorites
Custom lists
Persistence
Offline operation
AniList enrichment
Franchise grouping
Random category exclusivity
Home vertical scrolling
Image placeholders and cache reuse

Latest automated checks:

- SQLite records: 1000
- Unique internal franchise IDs: 1000
- Visual franchise groups: 818
- Visual duplicate titles: 0
- Primary genre present for every visual franchise
- Popularity score present for every visual franchise
- Home sections: 9
- Random results: maximum 5
- Random categories: mutually exclusive
📜 Version History
v0.8
Added 800 AniList-verified catalog records
Added deterministic franchise grouping
Added season, OVA, special and movie presentation inside Details
Added primary genre per franchise
Added exclusive Random discovery categories
Added five-result Random search
Added vertical Home with persistent genre sections
Added `See more` expansion per Home section
Added shared asynchronous image manager
Added local image placeholder and cache recovery
Added Outfit and DM Sans local fonts
Added consistent SVG icons
Improved detail layout with poster, blur hero and compact biography
Removed streaming information from the visible detail UI

v0.7
Complete visual redesign
Introduced AniVerse branding
Added modern dark interface
Added Outfit and DM Sans typography
Added visual anime cards
Added bottom navigation
Added improved image loading and caching
Added anime search
Added top-rated anime by genre
Expanded favorites
Added custom anime lists
Added persistent user data
Improved anime detail pages
Preserved offline functionality
Preserved local SQLite catalog
Preserved optional AniList enrichment
v0.6.1
Added anime detail pages
Added persistent favorites
Added optional AniList enrichment
Added metadata and image caching
Migrated the interface to PySide6
v0.6
Added local SQLite anime system
Added 200-anime master catalog
Added genre filtering
Added multiple genre selection
Added episode filtering
Improved recommendation ranking
Stabilized the graphical interface
🎌 Project philosophy

AniVerse follows a simple principle:

Local anime catalog first, optional online enrichment second.

The local catalog remains the source of truth.

User data remains separate from the catalog.

The application should remain useful without an Internet connection.

No data should be invented when reliable information is unavailable.

Made with 🐍 Python, Qt and 🎌 a love for anime.