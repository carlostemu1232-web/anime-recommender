# Contexto del proyecto Anime App

## Objetivo

Anime App es una aplicación de escritorio hecha con Python y PySide6. La versión visual actual se llama AniVerse y permite buscar, recomendar, guardar favoritos y gestionar listas usando una base de datos SQLite local. La aplicación tiene modo offline y un enriquecimiento online opcional con AniList al abrir una ficha.

## Estructura actual

```text
anime-app/
├── main.py
├── README.md
├── PROJECT_CONTEXT.md
├── ui/
│   ├── __init__.py
│   └── main_window.py
├── user_data/
└── database/
    ├── __init__.py
    ├── anime.db
    ├── favorites.py
    ├── anilist.py
    ├── enrich_metadata.py
    ├── catalog.py
    ├── database.py
    ├── importer.py
    └── test_database.py
```

Los antiguos módulos de APIs y la carpeta `genres/` ya no forman parte del proyecto y fueron eliminados porque no tienen usos activos.

## Base de datos

La base de datos está en `database/anime.db` y usa SQLite.

Tablas principales:

- `animes`: información de cada anime.
- `genres`: catálogo de géneros.
- `anime_genres`: relación muchos-a-muchos entre animes y géneros.

Cada anime tiene estos campos:

- `franchise`: identificador único.
- `title`: título mostrado.
- `original_title`: título original cuando está disponible.
- `synopsis`: actualmente vacío intencionadamente.
- `rating`: valoración numérica.
- `year`: año de estreno.
- `episodes`: número de episodios.
- `status`: estado, por ejemplo `finished` u `ongoing`.
- `image_url`: actualmente vacío intencionadamente.
- `trailer_url`: actualmente vacío intencionadamente.

La ficha puede obtener online desde AniList una sinopsis, portada, tráiler y enlaces de visualización. Esos datos se guardan en `database/anilist_cache.json` y las portadas en `database/anilist_images/`.

Estado actual validado:

- 200 animes en el catálogo.
- 200 animes en SQLite.
- 200 franquicias únicas.
- 0 valores NULL en `rating`, `year`, `episodes` y `status`.
- `synopsis`, `image_url` y `trailer_url` se mantienen sin completar por decisión del proyecto.

## Archivos importantes

### `main.py`

Es la interfaz gráfica principal.

Responsabilidades:

1. Crear la base si no existe.
2. Importar el catálogo automáticamente si la base está vacía.
3. Mostrar tres selectores de género.
4. Permitir elegir hasta tres géneros.
5. Permitir filtrar por episodios:
   - `All episodes`
   - `Under 50 episodes`
   - `50+ episodes`
6. Cargar los animes desde SQLite.
7. Ejecutar el filtrado local.
8. Mostrar como máximo diez recomendaciones.
9. Permitir abrir una ficha al pulsar el título.
10. Mostrar Buscar, Favoritos y Detalle dentro de la misma ventana.
11. Permitir añadir o quitar favoritos.

Los géneros visibles actualmente son:

- `action`
- `fantasy`
- `comedy`
- `drama`
- `school`
- `adventure`
- `romance`
- `isekai`

### `database/catalog.py`

Contiene `ANIME_CATALOG`, una lista de 200 diccionarios de anime.

También contiene `COMPLETED_METADATA`, que completa los datos básicos de los 39 animes iniciales que estaban incompletos. Al cargar el módulo, esos valores se aplican al catálogo.

Funciones principales:

- `get_all_catalog_animes()` devuelve el catálogo.
- `get_catalog_size()` devuelve el número de animes.

### `database/importer.py`

Importa `ANIME_CATALOG` en SQLite.

Para cada anime:

1. Inserta o actualiza el registro usando `franchise` como clave lógica.
2. Limpia sus géneros anteriores.
3. Inserta los géneros actuales.
4. Crea las relaciones en `anime_genres`.

Se puede ejecutar manualmente con:

```bash
python database/importer.py
```

### `database/database.py`

Contiene la conexión, creación del esquema, operaciones de escritura y consultas.

Funciones importantes:

- `create_database()` crea las tablas.
- `get_connection()` devuelve una conexión SQLite con claves foráneas activadas.
- `add_anime(anime)` inserta o actualiza un anime.
- `add_genre(name)` crea un género si no existe.
- `add_anime_genre(anime_id, genre_name)` crea una relación.
- `clear_anime_genres(anime_id)` elimina relaciones anteriores.
- `get_all_animes()` devuelve todos los animes sin géneros.
- `get_all_animes_with_genres()` devuelve todos los animes con una lista `genres`.
- `get_anime_with_genres(anime_id)` devuelve una ficha completa.
- `get_recommendations(animes, selected_genres, episode_filter)` filtra y ordena recomendaciones.

El orden de recomendación es:

1. Número de géneros coincidentes.
2. Valoración.
3. Año más reciente.

### `database/test_database.py`

Contiene comprobaciones sencillas de consulta por género. No es todavía una suite formal de `pytest`.

### `database/favorites.py`

Gestiona los favoritos del usuario en una base SQLite separada del catálogo.

- Si `user_data/` es una carpeta, usa `user_data/favorites.db`.
- En el entorno actual `user_data` era un archivo vacío, así que usa `database/favorites.db` como alternativa.
- `create_favorites_database()` crea la tabla.
- `is_favorite(anime_id)` comprueba el estado.
- `toggle_favorite(anime_id)` añade o quita un anime.
- `get_favorite_ids()` devuelve los favoritos persistentes.

### `database/anilist.py`

Consulta AniList de forma opcional y asíncrona al abrir una ficha. Si no hay conexión, se conserva la información local y la ficha sigue funcionando. La caché evita repetir consultas ya realizadas.

### `database/lists.py`

Gestiona listas personalizadas persistentes en una base de usuario separada. Permite crear, renombrar y eliminar listas, añadir y quitar referencias a animes y consultar las listas de un anime.

### `ui/main_window.py`

Contiene la interfaz PySide6 de AniVerse: Home visual, buscador local, Favoritos, Listas, Ajustes, ficha individual, tarjetas y navegación inferior.

### `database/enrich_metadata.py`

Es un importador opcional de una sola ejecución. Consulta una fuente pública, verifica la coincidencia del título y guarda sinopsis e imagen en SQLite. No se ejecuta al iniciar la app y no convierte la aplicación en dependiente de internet.

Se ejecuta con:

```bash
python database/enrich_metadata.py
```

Para guardar también los pósteres localmente en `database/images/`:

```bash
python database/enrich_metadata.py --download-images
```

Si la fuente no responde o la coincidencia no es suficientemente fiable, el anime se omite y no se inventan datos.

## Flujo de ejecución

Al ejecutar:

```bash
python main.py
```

ocurre lo siguiente:

1. Se crea la base SQLite si no existe.
2. Se comprueba si hay animes.
3. Si está vacía, se importa el catálogo de 200 títulos.
4. Se abre la ventana PySide6.
5. El usuario selecciona géneros y filtro de episodios.
6. `main.py` llama a `get_all_animes_with_genres()`.
7. `database.py` filtra localmente.
8. La interfaz muestra los diez primeros resultados.
9. El usuario puede pulsar un título para abrir su ficha.
10. La ficha muestra los datos disponibles y permite gestionar el favorito.
11. La vista Favoritos recupera los IDs desde la base de usuario y los datos desde el catálogo.

## Decisiones actuales

- AniList solo se usa de forma opcional al abrir fichas; la app puede funcionar offline.
- No se deben volver a introducir `api_sources.py` ni `api_practice.py`.
- No se deben usar palabras clave para detectar géneros si el género oficial ya existe en SQLite.
- Los registros con episodios desconocidos solo aparecen cuando se selecciona `All episodes`.
- No se deben inventar sinopsis, imágenes ni enlaces de tráiler.
- El catálogo maestro es la fuente de verdad para sincronizar SQLite.
- Los favoritos nunca modifican `database/anime.db`.
- Las imágenes, sinopsis, plataformas y tráilers vacíos se muestran como `No disponible`.
- El enriquecimiento de sinopsis e imágenes es opcional y se realiza con `database/enrich_metadata.py`.
- Las consultas online no deben ejecutarse en el hilo principal de PySide6.
- La interfaz principal usa PySide6, no Tkinter.
- La identidad visual de la app es AniVerse.
- La interfaz visible está en inglés.
- La paleta visual usa negro, superficies oscuras y naranja como acento.
- Home y Search precargan portadas visibles de AniList en segundo plano.
- `assets/fonts/` contiene Outfit y DM Sans como fuentes locales.
- `assets/icons/` contiene los iconos SVG consistentes de la interfaz.
- El cargador de AniList deduplica peticiones simultáneas por `franchise`.
- Las tarjetas muestran `Loading...` mientras esperan y `Not available` si no hay imagen.
- AniList prueba también `original_title` cuando el título mostrado no obtiene coincidencia.
- `database/anime.db` nunca debe almacenar listas personales.

## Validaciones realizadas

Estos comandos deben funcionar desde `anime-app`:

```bash
python -m py_compile main.py database/database.py database/catalog.py database/importer.py database/test_database.py
python database/importer.py
python main.py
```

Pruebas funcionales verificadas:

- Catálogo: 200.
- Base SQLite: 200.
- Isekai con todos los episodios: 36 resultados.
- Acción con menos de 50 episodios: resultados disponibles.
- Sin errores de diagnóstico en los módulos activos.
- Favoritos verificados con añadir, consultar, persistir y quitar.
- Listas verificadas con crear, renombrar, añadir anime, consultar y eliminar.

## Próximos pasos recomendados

1. Crear una suite real de pruebas para filtros, fichas, favoritos y listas.
2. Añadir filtros de valoración, año y estado en la interfaz.
3. Mejorar el flujo para editar listas desde la ficha.
4. Añadir sinopsis, imágenes, plataformas y tráilers solo usando una fuente fiable o datos revisados manualmente.

## Cómo pedir ayuda a otro ChatGPT

Puedes pegar este archivo y decir:

> Este es el contexto de mi proyecto Anime App. Quiero que analices los archivos actuales respetando esta arquitectura local SQLite. No reintroduzcas APIs externas, no borres el catálogo y no inventes datos. Antes de editar, revisa el archivo concreto y después valida los cambios con Python.
