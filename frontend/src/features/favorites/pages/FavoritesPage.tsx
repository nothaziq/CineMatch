import { Link } from "react-router-dom";
import { FavoriteCard } from "../components/FavoriteCard";
import { useFavorites } from "../hooks/useFavorites";

export function FavoritesPage() {
  const { favorites, removeFavorite } = useFavorites();

  return (
    <div className="px-6 py-10 md:px-10">
      <h1 className="mb-1 font-[var(--font-display)] text-3xl font-semibold text-[var(--color-bone)]">
        Favorites
      </h1>
      <p className="mb-8 text-sm text-[var(--color-bone-dim)]">
        Saved on this device. {favorites.length > 0 && `${favorites.length} movie${favorites.length === 1 ? "" : "s"}.`}
      </p>

      {favorites.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <p className="text-[var(--color-bone-dim)]">You haven't favorited any movies yet.</p>
          <Link
            to="/search"
            className="glass rounded-full px-5 py-2 text-sm text-[var(--color-bone)] transition-colors hover:border-[var(--color-marquee)]"
          >
            Find something to favorite
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {favorites.map((movie) => (
            <FavoriteCard key={movie.movie_id} movie={movie} onRemove={removeFavorite} />
          ))}
        </div>
      )}
    </div>
  );
}
