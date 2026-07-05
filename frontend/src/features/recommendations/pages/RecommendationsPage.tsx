import { MovieCardSkeleton } from "../../../components/MovieCardSkeleton";
import { MovieMultiSelect } from "../components/MovieMultiSelect";
import { RecommendationCard } from "../components/RecommendationCard";
import { useRecommendations } from "../hooks/useRecommendations";

export function RecommendationsPage() {
  const {
    selected,
    addMovie,
    removeMovie,
    clearAll,
    atMaxSeeds,
    maxSeeds,
    hasEnoughSeeds,
    recommendations,
    isLoading,
    isFetching,
    isError,
  } = useRecommendations();

  return (
    <div className="px-6 pb-16 pt-10 md:px-10">
      <div className="mx-auto max-w-2xl text-center">
        <h1 className="font-[var(--font-display)] text-3xl font-semibold text-[var(--color-bone)]">
          Pick your favorites
        </h1>
        <p className="mt-2 text-sm text-[var(--color-bone-dim)]">
          Add a few movies you love and we'll blend them into one set of recommendations.
        </p>
      </div>

      <div className="mx-auto mt-8 max-w-xl">
        <MovieMultiSelect
          selected={selected}
          onAdd={addMovie}
          onRemove={removeMovie}
          atMax={atMaxSeeds}
          maxSeeds={maxSeeds}
        />

        {selected.length > 0 && (
          <button
            onClick={clearAll}
            className="mt-4 text-xs text-[var(--color-bone-dim)] underline decoration-dotted transition-colors hover:text-[var(--color-bone)]"
          >
            Clear all
          </button>
        )}
      </div>

      <div className="mx-auto mt-12 max-w-6xl">
        {!hasEnoughSeeds && (
          <p className="text-center text-sm text-[var(--color-bone-dim)]">
            Add at least one movie above to get recommendations.
          </p>
        )}

        {hasEnoughSeeds && isError && (
          <p className="text-center text-sm text-[var(--color-bone-dim)]">
            Something went wrong blending recommendations. Try again.
          </p>
        )}

        {hasEnoughSeeds && isLoading && (
          <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {Array.from({ length: 10 }).map((_, i) => (
              <MovieCardSkeleton key={i} />
            ))}
          </div>
        )}

        {hasEnoughSeeds && !isLoading && !isError && (
          <>
            {isFetching && (
              <p className="mb-4 text-center text-xs text-[var(--color-bone-dim)]">
                Re-blending with your latest picks...
              </p>
            )}

            {recommendations && recommendations.length > 0 ? (
              <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                {recommendations.map((rec) => (
                  <RecommendationCard key={rec.movie.movie_id} recommendation={rec} />
                ))}
              </div>
            ) : (
              <p className="mx-auto max-w-sm text-center text-sm text-[var(--color-bone-dim)]">
                No blended recommendations found for this combination yet — try adding a
                different movie.
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
