import { Star } from "lucide-react";
import type { MovieOut } from "../types/api";

interface MovieCardProps {
  movie: MovieOut;
  onClick?: (movie: MovieOut) => void;
}

export function MovieCard({ movie, onClick }: MovieCardProps) {
  return (
    <button
      onClick={() => onClick?.(movie)}
      className="light-leak group relative w-full shrink-0 rounded-xl text-left transition-transform duration-300 ease-out hover:-translate-y-1 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-signal)]"
    >
      <div className="glass aspect-[2/3] w-full overflow-hidden rounded-xl">
        {movie.poster_url ? (
          <img
            src={movie.poster_url}
            alt={`${movie.title} poster`}
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center px-3 text-center">
            <span className="font-[var(--font-display)] text-sm text-[var(--color-bone-dim)]">
              {movie.title}
            </span>
          </div>
        )}
      </div>

      <div className="mt-2 space-y-0.5">
        <p className="truncate font-[var(--font-body)] text-sm font-medium text-[var(--color-bone)]">
          {movie.title}
        </p>
        <div className="flex items-center gap-2 font-[var(--font-mono)] text-xs text-[var(--color-bone-dim)]">
          {movie.year && <span>{movie.year}</span>}
          {movie.avg_rating > 0 && (
            <span className="flex items-center gap-1 text-[var(--color-marquee)]">
              <Star size={12} fill="currentColor" strokeWidth={0} />
              {movie.avg_rating.toFixed(1)}
            </span>
          )}
        </div>
      </div>
    </button>
  );
}
