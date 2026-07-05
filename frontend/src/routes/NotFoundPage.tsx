import { Compass, Home } from "lucide-react";
import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex min-h-[70vh] flex-col items-center justify-center gap-4 px-6 text-center">
      <span className="font-[var(--font-display)] text-7xl font-semibold text-[var(--color-marquee)]">
        404
      </span>
      <h1 className="font-[var(--font-display)] text-2xl font-semibold text-[var(--color-bone)]">
        This page doesn't exist.
      </h1>
      <p className="max-w-sm text-sm text-[var(--color-bone-dim)]">
        The link might be broken, or the page may have moved. Let's get you back on track.
      </p>

      <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
        <Link
          to="/"
          className="glass flex items-center gap-2 rounded-full px-5 py-2.5 text-sm text-[var(--color-bone)] transition-colors hover:border-[var(--color-marquee)]"
        >
          <Home size={16} />
          Back home
        </Link>
        <Link
          to="/search"
          className="glass flex items-center gap-2 rounded-full px-5 py-2.5 text-sm text-[var(--color-bone)] transition-colors hover:border-[var(--color-marquee)]"
        >
          <Compass size={16} />
          Search movies
        </Link>
      </div>
    </div>
  );
}
