import os
import threading
from pathlib import Path

from database.anilist import get_cached_media, get_media_async


class ImageManager:

    def __init__(self, on_ready=None, on_failed=None):

        self.on_ready = on_ready
        self.on_failed = on_failed
        self._lock = threading.Lock()
        self._memory_cache = {}
        self._active = set()

    def get_local_path(self, anime):

        franchise = anime['franchise']

        with self._lock:

            cached = self._memory_cache.get(franchise)

        if cached and self._valid_path(cached):

            return cached

        media = get_cached_media(franchise) or {}
        path = media.get('local_image')

        if self._valid_path(path):

            with self._lock:

                self._memory_cache[franchise] = path

            return path

        return None

    def request(self, anime):

        franchise = anime['franchise']
        local_path = self.get_local_path(anime)

        if local_path:

            self._notify_ready(anime, local_path)
            return

        with self._lock:

            if franchise in self._active:

                return

            self._active.add(franchise)

        get_media_async(
            anime['title'],
            franchise,
            lambda media: self._finished(anime, media),
            lambda error: self._failed(anime, error),
            anime.get('original_title')
        )

    def _finished(self, anime, media):

        path = media.get('local_image') if media else None

        with self._lock:

            self._active.discard(anime['franchise'])

            if self._valid_path(path):

                self._memory_cache[anime['franchise']] = path

        if self._valid_path(path):

            self._notify_ready(anime, path)

        else:

            self._failed(anime, None)

    def _failed(self, anime, error):

        with self._lock:

            self._active.discard(anime['franchise'])

        if self.on_failed:

            self.on_failed(anime, error)

    def _notify_ready(self, anime, path):

        if self.on_ready:

            self.on_ready(anime, path)

    @staticmethod
    def _valid_path(path):

        return bool(
            path
            and os.path.isfile(path)
            and Path(path).stat().st_size > 0
        )
