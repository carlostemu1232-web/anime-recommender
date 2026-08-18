# 🎌 AniVerse

AniVerse is a Python desktop anime application focused on discovering, searching and organizing anime through a modern visual interface.

The application uses a local SQLite catalog and optionally uses AniList to enrich anime details with images, synopsis, trailers and streaming information.

The core application can work offline.

---

## 🚀 Version

**Current version: v0.7**

v0.7 is a major evolution of the previous v0.6.1 version, focused on improving the visual experience, anime discovery and personal organization.

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

- Anime recommendations
- Top-rated anime
- Genre-based recommendations
- Visual anime cards

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

### 🌐 AniList enrichment

AniList is an optional enrichment source.

It can provide:

- Synopsis
- Cover images
- Trailers
- Streaming information

Data is cached locally to reduce repeated requests.

The application continues working when AniList or the Internet is unavailable.

### 🖼️ Image system

v0.7 improves anime image loading.

Images can be loaded directly in:

- Home
- Search
- Favorites
- Lists
- Anime cards
- Anime details

Images are loaded asynchronously and cached locally when possible.

If an image is unavailable, AniVerse displays a placeholder instead of an error.

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