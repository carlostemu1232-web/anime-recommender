# AniVerse UI Interface Specification

## Purpose

This document describes the current AniVerse desktop interface and its interaction model. It is intended as implementation context for future maintenance, debugging and UI improvements.

AniVerse is a Python desktop application built with PySide6 and SQLite. The interface is local-first: the catalog, search, recommendations, favorites and lists work without Internet access. AniList is optional and is used asynchronously for additional media such as posters, synopsis, trailers and streaming metadata. Streaming metadata is currently not displayed in the visible detail interface.

## Entry Point

The application starts from:

```text
main.py
```

Startup responsibilities:

1. Create the local anime database if it does not exist.
2. Import the master catalog if SQLite is empty.
3. Create the favorites and lists databases.
4. Load local fonts and the application theme.
5. Display the AniVerse splash screen.
6. Create the main PySide6 window.

The main window is implemented in:

```text
ui/main_window.py
```

## Window Shell

The main shell is divided into two areas:

```text
Main window
├── Left sidebar
└── Main content area
    ├── Top status/header row
    └── QStackedWidget pages
```

The window is resizable and has a minimum size suitable for desktop use. The current default size is approximately 980 x 850 pixels.

### Left Sidebar

The sidebar contains the AniVerse brand and the primary navigation buttons:

- Home
- Explore
- Random
- Favorites
- Lists
- Settings

Each navigation item uses a transparent SVG icon from:

```text
assets/icons/
```

The sidebar is persistent while the application is open. Selecting a navigation item changes the page inside the central `QStackedWidget`.

### Top Header

The current header contains:

- Local/online connection status.
- A small AV avatar indicator.

Search is intentionally not placed in the global header. Search is available only inside the Explore page.

## Pages

The current stack contains seven pages:

1. Home
2. Explore/Search
3. Random discovery
4. Favorites
5. Lists
6. Settings
7. Anime/Franchise Details

## Home Page

Home is a long vertical page.

It uses one main vertical `QScrollArea`. The page contains several persistent sections; sections are not replaced when the user scrolls.

Current Home structure:

```text
Home
├── Featured
├── Action
├── Fantasy
├── Comedy
├── Drama
├── School
├── Adventure
├── Romance
└── Isekai
```

Each section is a dark surface containing:

- Section title.
- A limited initial number of anime franchise cards.
- A `See more` button.
- A `Show less` state after expansion.

The first five cards are shown initially. More cards can be expanded in the same section. The data is prepared from the local SQLite catalog and grouped through `database/franchises.py` before reaching the UI.

Each genre section uses official genre relationships from SQLite. Genres are not detected by title keywords.

## Explore / Search Page

Explore is the normal local search page.

The search field is located inside this page, not in the global header.

Interaction:

1. Type a title or original title.
2. Press the search button with the magnifying glass icon.
3. Results are rendered from the local SQLite catalog.

Search supports:

- Display title.
- Original title.
- Titles of grouped franchise parts.

Search does not query AniList and does not require Internet access.

Search results are limited to a manageable visible amount to avoid creating hundreds of widgets at once. The search field uses debounce and local in-memory franchise data to reduce lag while typing.

## Random Discovery Page

Random is a separate page in the sidebar.

It contains:

- One selected genre.
- Episode filter buttons:
  - All episodes
  - Under 24 episodes
  - 24+ episodes
- A `Search randomly` button with the wand icon.
- Up to five random franchise results.

The genre selector uses rectangular buttons with exclusive selection. Only one genre can be active at once.

The random result history is stored in memory during the session. A franchise is not selected again until the available pool has been exhausted, after which the cycle resets.

Random works with franchise groups, not individual seasons.

For numeric episode filters:

- Unknown episode counts appear only under `All episodes`.
- Unknown episode counts do not appear under `Under 24 episodes`.
- Unknown episode counts do not appear under `24+ episodes`.

## Anime Cards

The main visual component is `AnimeCard`.

Cards are rectangular and fixed-size so that their clickable surfaces are consistent across Home, Search, Random and Favorites.

Current approximate card size:

```text
184 x 350 pixels
```

Card contents:

- Poster frame.
- Anime or franchise title.
- Rating.
- Year.
- Episode metadata.
- Favorite icon button.

The poster frame has a stable aspect ratio and uses `QPixmap.scaled()` with `KeepAspectRatio`. Images are never intentionally stretched or cropped.

Cards are clickable. Clicking the card body opens Details. Clicking the heart button toggles the favorite state without opening Details.

The favorite button:

- Uses `heart.svg` when not saved.
- Uses `heart_filled.svg` when saved.
- Has a tooltip.
- Updates immediately after clicking.
- Stores the state persistently through `database/favorites.py`.

## Part Cards

`PartCard` is used inside franchise Details for seasons, OVAs, specials and movies.

Part cards are smaller than main cards and have their own fixed dimensions so they do not inherit the larger Home card layout.

Part card contents:

- Smaller poster.
- Part title.
- Episode count.
- Year.

Part cards are arranged in a fixed grid/list inside the long Details page. They do not use the old horizontal carousel layout.

Clicking a part opens the associated franchise detail context while preserving the correct Back destination.

## Details Page

The Details page represents either an anime franchise or one of its internal parts.

It uses one main vertical scroll area.

The visual hierarchy is:

```text
Back
↓
Hero
↓
Franchise overview and Biography
↓
Seasons, OVAs and Movies
```

### Hero

The hero contains:

- Large sharp poster on the left.
- Blurred background image behind the content.
- Dark overlay for readable text.
- Title on the right.
- Rating.
- Year.
- Status.
- Genres.
- Part count.
- Known episode total.
- Favorite icon button.
- Add to lists button.

The poster stays sharp and uses `KeepAspectRatio`. The background uses the same anime image with a blur effect and a dark overlay.

### Franchise Overview

The overview panel displays:

- Number of parts.
- Known episode total.
- Starting year.
- Status.

Unknown episodes are not treated as zero. When only a partial total is known, the UI uses a known-total representation such as `24+`.

### Biography

The biography area is compact and word-wrapped. It does not use a large independent biography scrollbar.

If AniList synopsis data is not available, the UI can display a factual offline description built from local data such as:

- Title.
- Genres.
- Year.
- Episode count.
- Status.

This fallback does not invent a plot summary.

### Related Parts

Details retains individual records internally and displays their grouped parts:

- Seasons.
- OVAs.
- Specials.
- Movies.
- Other explicitly grouped parts.

The visible detail interface does not show the `Where to watch` or streaming section.

## Franchise Grouping

Franchise grouping is implemented in:

```text
database/franchises.py
```

The catalog keeps all individual SQLite records. Grouping is a presentation layer.

Explicit relationships are stored in `FRANCHISE_GROUPS`. Examples include:

- Attack on Titan.
- Naruto.
- Dragon Ball.
- JoJo's Bizarre Adventure.
- Re:ZERO.
- Mushoku Tensei.
- Frieren.
- Monogatari.
- My Hero Academia.
- Gintama.
- Kaguya-sama.
- Food Wars.
- Jujutsu Kaisen.
- SPY x FAMILY.
- One-Punch Man.
- Violet Evergarden.
- Vinland Saga.

A franchise card represents one group. Internal parts remain available inside Details.

The grouping layer also calculates:

- Combined genres.
- Primary genre.
- Best rating.
- Average rating.
- Known episode total.
- Whether all part episode counts are known.
- Number of parts.
- Local popularity score.

## Image System

The central image service is:

```text
database/image_manager.py
```

The image priority is:

1. In-memory image path.
2. Valid local path from `database/anilist_images/`.
3. Cached AniList metadata.
4. Asynchronous AniList request.
5. Local placeholder.

The system prevents duplicate in-flight requests by franchise. Cards show a placeholder while an image is unavailable and update through Qt signals when a real local image arrives.

Images are requested when cards are created or when a visible section needs them. Details does not need to be opened to activate image loading.

## AniList

AniList is optional.

It is used asynchronously for:

- Poster URLs.
- Local poster downloads.
- Synopsis data.
- Trailers.
- External links.

AniList responses are cached in:

```text
database/anilist_cache.json
```

Poster files are stored in:

```text
database/anilist_images/
```

If AniList is unavailable, SQLite data, cache data and placeholders keep the application usable.

## Favorites

Favorites are stored separately from the anime catalog through:

```text
database/favorites.py
```

Favorites use the anime ID reference. The UI resolves old individual-part favorites into their containing visual franchise where possible.

The catalog database is never modified by favorite actions.

## Lists

Custom lists are stored separately through:

```text
database/lists.py
```

Supported operations:

- Create list.
- Rename list.
- Delete list.
- Add an anime reference.
- Remove an anime reference.
- Add an anime to multiple lists.
- Avoid duplicate relationships through a composite primary key.

The catalog remains independent from user lists.

## Data State

Current local database state:

```text
Individual SQLite anime records: 1000
Internal unique franchise IDs: 1000
Visual franchise groups: 818
Exact visual duplicate titles: 0
```

The local database supports offline:

- Search.
- Recommendations.
- Genre filtering.
- Episode filtering.
- Franchise grouping.
- Favorites.
- Lists.
- Details.

## Testing Commands

Use the workspace virtual environment when possible:

```powershell
cd "C:\Users\carlo\Documents\python-projects\anime-app"
C:/Users/carlo/Documents/python-projects/.venv/Scripts/python.exe -m py_compile main.py ui/main_window.py database/database.py database/franchises.py database/image_manager.py database/anilist.py database/favorites.py database/lists.py
```

Run the desktop app:

```powershell
C:/Users/carlo/Documents/python-projects/.venv/Scripts/python.exe main.py
```

For packaging, see:

```text
packaging/AniVerse.spec
packaging/build.ps1
packaging/AniVerse.iss
```

## Working Rules

- Do not delete catalog records to solve visual duplicates.
- Do not group anime using weak substring guesses when no reliable relationship exists.
- Do not invent ratings, episodes, genres, synopses or images.
- Keep AniList optional.
- Keep network work off the Qt UI thread.
- Keep user data separate from `database/anime.db`.
- Reuse `ImageManager` instead of adding per-view image download logic.
- Validate both SQLite data and visual franchise grouping after catalog changes.
