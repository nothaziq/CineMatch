import { useSyncExternalStore } from "react";
import type { MovieOut } from "../../../types/api";
import { localStorageAdapter } from "../services/localStorageAdapter";

// Swap this one import to point useFavorites at a different
// FavoritesStorageAdapter implementation (e.g. a backend-backed one) later.
const adapter = localStorageAdapter;

export function useFavorites() {
  const favorites = useSyncExternalStore(adapter.subscribe, adapter.getSnapshot);

  function isFavorite(movieId: number): boolean {
    return favorites.some((m) => m.movie_id === movieId);
  }

  function toggleFavorite(movie: MovieOut): void {
    if (isFavorite(movie.movie_id)) {
      adapter.remove(movie.movie_id);
    } else {
      adapter.add(movie);
    }
  }

  return {
    favorites,
    isFavorite,
    toggleFavorite,
    addFavorite: adapter.add,
    removeFavorite: adapter.remove,
  };
}
