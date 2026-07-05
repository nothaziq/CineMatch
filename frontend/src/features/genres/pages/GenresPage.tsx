import { GenreTile } from "../components/GenreTile";
import { useGenres } from "../hooks/useGenres";

export function GenresPage() {
  const { data: genres, isLoading, isError } = useGenres();

  return (
    <div className="px-6 py-10 md:px-10">
      <h1 className="mb-8 font-[var(--font-display)] text-3xl font-semibold text-[var(--color-bone)]">
        Genres
      </h1>

      {isError && (
        <p className="text-sm text-[var(--color-bone-dim)]">
          Couldn't load genres right now. Try refreshing.
        </p>
      )}

      {isLoading && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="glass h-24 animate-pulse rounded-xl bg-[var(--color-panel)]" />
          ))}
        </div>
      )}

      {!isLoading && !isError && genres && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {genres.map((genre) => (
            <GenreTile key={genre.genre} genre={genre} />
          ))}
        </div>
      )}
    </div>
  );
}
