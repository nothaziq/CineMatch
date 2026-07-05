import type { MovieOut } from "../types/api";
import { MovieCard } from "./MovieCard";
import { MovieCardSkeleton } from "./MovieCardSkeleton";

interface MovieRailProps {
  title: string;
  movies: MovieOut[] | undefined;
  isLoading: boolean;
  isError: boolean;
  onSelectMovie?: (movie: MovieOut) => void;
}

export function MovieRail({ title, movies, isLoading, isError, onSelectMovie }: MovieRailProps) {
  return (
    <section className="py-6">
      <h2 className="mb-4 px-6 font-[var(--font-display)] text-2xl font-semibold text-[var(--color-bone)] md:px-10">
        {title}
      </h2>

      {isError && (
        <p className="px-6 text-sm text-[var(--color-bone-dim)] md:px-10">
          Couldn't load this section right now. Try refreshing.
        </p>
      )}

      <div className="flex gap-4 overflow-x-auto px-6 pb-2 [scrollbar-width:thin] md:px-10">
        {isLoading &&
          Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="w-40 shrink-0 md:w-48">
              <MovieCardSkeleton />
            </div>
          ))}

        {!isLoading &&
          !isError &&
          movies?.map((movie) => (
            <div key={movie.movie_id} className="w-40 shrink-0 md:w-48">
              <MovieCard movie={movie} onClick={onSelectMovie} />
            </div>
          ))}

        {!isLoading && !isError && movies?.length === 0 && (
          <p className="text-sm text-[var(--color-bone-dim)]">Nothing here yet.</p>
        )}
      </div>
    </section>
  );
}
