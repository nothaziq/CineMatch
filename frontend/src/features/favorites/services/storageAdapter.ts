import type { MovieOut } from "../../../types/api";

/**
 * Abstraction over "where favorites live." Swapping to a real backend later
 * (e.g. a `/favorites` API tied to a logged-in user) means writing one new
 * adapter that implements this interface and pointing useFavorites.ts at it
 * — no component that reads/writes favorites has to change.
 */
export interface FavoritesStorageAdapter {
  /** Current favorites, read synchronously (used as the useSyncExternalStore snapshot). */
  getSnapshot(): MovieOut[];
  /** Register a listener that fires whenever favorites change; returns an unsubscribe fn. */
  subscribe(listener: () => void): () => void;
  add(movie: MovieOut): void;
  remove(movieId: number): void;
}
