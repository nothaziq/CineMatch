import { useEffect, useRef, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
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
  const scrollerRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const updateScrollState = () => {
    const el = scrollerRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 8);
    // 8px tolerance for sub-pixel rounding at the end of the scroll range.
    setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 8);
  };

  useEffect(() => {
    updateScrollState();
    // Re-check once card data actually renders (widths aren't known before that).
  }, [movies]);

  const scrollByPage = (direction: "left" | "right") => {
    const el = scrollerRef.current;
    if (!el) return;
    // Scroll by ~85% of the visible width so the next card peeking in at the
    // edge gives a visual continuity cue, rather than a jarring full-page jump.
    const amount = el.clientWidth * 0.85 * (direction === "left" ? -1 : 1);
    el.scrollBy({ left: amount, behavior: "smooth" });
  };

  const showNav = !isLoading && !isError && (movies?.length ?? 0) > 0;

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

      <div className="group/rail relative">
        {/* Arrow buttons: desktop/pointer-input only — on touch devices the
            native horizontal swipe already works, and overlaying buttons
            there just eats thumb space without adding capability. */}
        {showNav && (
          <>
            <button
              type="button"
              onClick={() => scrollByPage("left")}
              aria-label={`Scroll ${title} left`}
              disabled={!canScrollLeft}
              className="glass absolute left-2 top-1/2 z-10 hidden -translate-y-1/2 items-center justify-center rounded-full p-2 text-[var(--color-bone)] opacity-0 transition-opacity duration-200 group-hover/rail:opacity-100 hover:bg-[var(--color-panel)] focus-visible:opacity-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-signal)] disabled:pointer-events-none disabled:opacity-0 md:flex"
            >
              <ChevronLeft size={20} aria-hidden />
            </button>
            <button
              type="button"
              onClick={() => scrollByPage("right")}
              aria-label={`Scroll ${title} right`}
              disabled={!canScrollRight}
              className="glass absolute right-2 top-1/2 z-10 hidden -translate-y-1/2 items-center justify-center rounded-full p-2 text-[var(--color-bone)] opacity-0 transition-opacity duration-200 group-hover/rail:opacity-100 hover:bg-[var(--color-panel)] focus-visible:opacity-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-signal)] disabled:pointer-events-none disabled:opacity-0 md:flex"
            >
              <ChevronRight size={20} aria-hidden />
            </button>
          </>
        )}

        <div
          ref={scrollerRef}
          onScroll={updateScrollState}
          className="scrollbar-rail flex gap-4 overflow-x-auto px-6 pb-2 md:px-10"
        >
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
      </div>
    </section>
  );
}
