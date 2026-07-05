import type { MovieOut } from "../../../types/api";
import type { FavoritesStorageAdapter } from "./storageAdapter";

const STORAGE_KEY = "cinematch:favorites";

function readFromDisk(): MovieOut[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as MovieOut[]) : [];
  } catch {
    // Corrupt JSON, or localStorage unavailable (private browsing, quota
    // exceeded, disabled entirely) — fail soft with an empty list rather
    // than crashing the app.
    return [];
  }
}

function writeToDisk(movies: MovieOut[]): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(movies));
  } catch {
    // Same as above — favorites just won't persist past this session.
  }
}

// Module-level cache + pub/sub so every component using useFavorites shares
// one source of truth without re-reading localStorage on every render, and
// all subscribers re-render when any one of them adds/removes a favorite.
let cache: MovieOut[] = readFromDisk();
const listeners = new Set<() => void>();

function notify(): void {
  listeners.forEach((listener) => listener());
}

// Keep multiple tabs/windows in sync — if the person favorites something in
// one tab, other open tabs pick it up too.
if (typeof window !== "undefined") {
  window.addEventListener("storage", (event) => {
    if (event.key !== STORAGE_KEY) return;
    cache = readFromDisk();
    notify();
  });
}

export const localStorageAdapter: FavoritesStorageAdapter = {
  getSnapshot() {
    return cache;
  },

  subscribe(listener) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },

  add(movie) {
    if (cache.some((m) => m.movie_id === movie.movie_id)) return;
    cache = [movie, ...cache];
    writeToDisk(cache);
    notify();
  },

  remove(movieId) {
    cache = cache.filter((m) => m.movie_id !== movieId);
    writeToDisk(cache);
    notify();
  },
};
