import { useNavigate } from "react-router-dom";
import type { RecommendationOut } from "../../../types/api";
import { MovieCard } from "../../../components/MovieCard";
import { MovieCardSkeleton } from "../../../components/MovieCardSkeleton";

interface SimilarMoviesRailProps {
  recommendations: RecommendationOut[] | undefined;
  isLoading: boolean;
  isError: boolean;
}

export function SimilarMoviesRail({ recommendations, isLoading, isError }: SimilarMoviesRailProps) {
  const navigate = useNavigate();

  return (
    <section className="px-6 py-8 md:px-10">
      <h2 className="mb-4 font-[var(--font-display)] text-2xl font-semibold text-[var(--color-bone)]">
        Similar Movies
      </h2>

      {isError && (
        <p className="text-sm text-[var(--color-bone-dim)]">
          Couldn't load recommendations right now.
        </p>
      )}

      <div className="grid grid-cols-2 gap-x-4 gap-y-6 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
        {isLoading &&
          Array.from({ length: 6 }).map((_, i) => <MovieCardSkeleton key={i} />)}

        {!isLoading &&
          !isError &&
          recommendations?.map((rec) => (
            <div key={rec.movie.movie_id} className="group relative">
              <MovieCard
                movie={rec.movie}
                onClick={(m) => navigate(`/movies/${m.movie_id}`)}
              />
              {/* Explanation surfaces on hover/focus rather than always-on —
                  keeps the grid visually calm, per the glassmorphism/premium
                  brief, while still making the "why" discoverable. */}
              <p className="pointer-events-none absolute inset-x-0 -bottom-1 translate-y-full px-1 text-xs text-[var(--color-bone-dim)] opacity-0 transition-all duration-200 group-hover:translate-y-2 group-hover:opacity-100">
                {rec.explanation}
              </p>
            </div>
          ))}

        {!isLoading && !isError && recommendations?.length === 0 && (
          <p className="text-sm text-[var(--color-bone-dim)]">
            No similar movies found yet.
          </p>
        )}
      </div>
    </section>
  );
}
