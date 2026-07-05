import { Star, Clock } from "lucide-react";
import type { MovieDetailOut } from "../../../types/api";

interface MovieHeroProps {
  movie: MovieDetailOut;
}

export function MovieHero({ movie }: MovieHeroProps) {
  return (
    <section className="relative overflow-hidden border-b border-[var(--color-panel-border)]">
      {movie.backdrop_url && (
        <div className="absolute inset-0">
          <img
            src={movie.backdrop_url}
            alt=""
            aria-hidden
            className="h-full w-full object-cover opacity-30"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-ink)] via-[var(--color-ink)]/70 to-transparent" />
        </div>
      )}

      <div className="relative z-10 flex flex-col gap-8 px-6 py-12 md:flex-row md:px-10 md:py-16">
        <div className="glass mx-auto h-72 w-48 shrink-0 overflow-hidden rounded-xl md:mx-0">
          {movie.poster_url ? (
            <img
              src={movie.poster_url}
              alt={`${movie.title} poster`}
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="flex h-full items-center justify-center px-3 text-center font-[var(--font-display)] text-sm text-[var(--color-bone-dim)]">
              {movie.title}
            </div>
          )}
        </div>

        <div className="flex-1">
          <h1 className="font-[var(--font-display)] text-4xl font-semibold text-[var(--color-bone)] md:text-5xl">
            {movie.title}
          </h1>

          <div className="mt-3 flex flex-wrap items-center gap-3 font-[var(--font-mono)] text-sm text-[var(--color-bone-dim)]">
            {movie.year && <span>{movie.year}</span>}
            {movie.runtime && (
              <span className="flex items-center gap-1">
                <Clock size={14} />
                {movie.runtime} min
              </span>
            )}
            {movie.avg_rating > 0 && (
              <span className="flex items-center gap-1 text-[var(--color-marquee)]">
                <Star size={14} fill="currentColor" strokeWidth={0} />
                {movie.avg_rating.toFixed(1)} ({movie.rating_count.toLocaleString()} ratings)
              </span>
            )}
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {movie.genres.map((genre) => (
              <span
                key={genre}
                className="glass rounded-full px-3 py-1 text-xs text-[var(--color-bone-dim)]"
              >
                {genre}
              </span>
            ))}
          </div>

          {movie.overview && (
            <p className="mt-6 max-w-2xl leading-relaxed text-[var(--color-bone)]">
              {movie.overview}
            </p>
          )}

          <dl className="mt-6 flex flex-wrap gap-x-8 gap-y-3 text-sm">
            {movie.director && (
              <div>
                <dt className="text-[var(--color-bone-dim)]">Director</dt>
                <dd className="mt-0.5 text-[var(--color-bone)]">{movie.director}</dd>
              </div>
            )}
            {movie.cast.length > 0 && (
              <div>
                <dt className="text-[var(--color-bone-dim)]">Cast</dt>
                <dd className="mt-0.5 max-w-md text-[var(--color-bone)]">
                  {movie.cast.join(", ")}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>
    </section>
  );
}
