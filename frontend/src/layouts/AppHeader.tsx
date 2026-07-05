import { Search } from "lucide-react";
import { Link } from "react-router-dom";

export function AppHeader() {
  return (
    <header className="glass sticky top-0 z-50 flex items-center justify-between px-6 py-4 md:px-10">
      <Link
        to="/"
        className="font-[var(--font-display)] text-xl font-semibold tracking-tight text-[var(--color-bone)]"
      >
        Cine<span className="text-[var(--color-marquee)]">Match</span>
      </Link>

      <nav className="hidden items-center gap-6 font-[var(--font-body)] text-sm text-[var(--color-bone-dim)] md:flex">
        <Link to="/" className="transition-colors hover:text-[var(--color-bone)]">
          Home
        </Link>
        <Link to="/genres" className="transition-colors hover:text-[var(--color-bone)]">
          Genres
        </Link>
        <Link to="/favorites" className="transition-colors hover:text-[var(--color-bone)]">
          Favorites
        </Link>
      </nav>

      <Link
        to="/search"
        aria-label="Search movies"
        className="flex items-center gap-2 rounded-full border border-[var(--color-panel-border)] px-3 py-1.5 text-sm text-[var(--color-bone-dim)] transition-colors hover:border-[var(--color-marquee)] hover:text-[var(--color-bone)]"
      >
        <Search size={16} />
        <span className="hidden sm:inline">Search</span>
      </Link>
    </header>
  );
}
