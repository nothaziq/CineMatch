import { useEffect, useRef } from "react";
import { MovieCard } from "../../../components/MovieCard";
import { MovieCardSkeleton } from "../../../components/MovieCardSkeleton";
import type { MovieOut } from "../../../types/api";

interface ResultsGridProps {
  results: MovieOut[] | undefined;
  isLoading: boolean;
  isFetching: boolean;
  isError: boolean;
  isSearching: boolean;
  canLoadMore: boolean;
  onLoadMore: () => void;
  onSelectMovie: (movie: MovieOut) => void;
}

export function ResultsGrid({
  results,
  isLoading,
  isFetching,
  isError,
  isSearching,
  canLoadMore,
  onLoadMore,
  onSelectMovie,
}: ResultsGridProps) {
  const sentinelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!canLoadMore || isFetching) return;
    const node = sentinelRef.current;
    if (!node) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) onLoadMore();
      },
      { rootMargin: "400px" }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [canLoadMore, isFetching, onLoadMore]);

  if (!isSearching) {
    return (
      <p className="px-6 py-10 text-center text-sm text-[var(--color-bone-dim)] md:px-10">
        Start typing to search the catalog.
      </p>
    );
  }

  if (isError) {
    return (
      <p className="px-6 py-10 text-center text-sm text-[var(--color-bone-dim)] md:px-10">
        Something went wrong searching. Try again.
      </p>
    );
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-4 px-6 py-6 sm:grid-cols-3 md:grid-cols-4 md:px-10 lg:grid-cols-5">
        {Array.from({ length: 10 }).map((_, i) => (
          <MovieCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <p className="px-6 py-10 text-center text-sm text-[var(--color-bone-dim)] md:px-10">
        No movies matched that search.
      </p>
    );
  }

  return (
    <div className="px-6 py-6 md:px-10">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {results.map((movie) => (
          <MovieCard key={movie.movie_id} movie={movie} onClick={onSelectMovie} />
        ))}
      </div>

      {canLoadMore && (
        <div ref={sentinelRef} className="flex justify-center py-8">
          <div className="flex gap-4">
            {isFetching &&
              Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="hidden w-40 sm:block">
                  <MovieCardSkeleton />
                </div>
              ))}
          </div>
        </div>
      )}

      {!canLoadMore && results.length > 0 && (
        <p className="pt-8 text-center text-xs text-[var(--color-bone-dim)]">
          That's everything — {results.length} match{results.length === 1 ? "" : "es"}.
        </p>
      )}
    </div>
  );
}
