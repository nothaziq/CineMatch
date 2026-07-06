import { Menu, Search, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";

const NAV_LINKS = [
  { to: "/", label: "Home" },
  { to: "/recommendations", label: "For You" },
  { to: "/genres", label: "Genres" },
  { to: "/favorites", label: "Favorites" },
];

export function AppHeader() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const menuButtonRef = useRef<HTMLButtonElement>(null);

  // Close the mobile menu whenever the route actually changes (a link inside
  // it was followed), not on every render.
  useEffect(() => {
    setIsMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!isMenuOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsMenuOpen(false);
        menuButtonRef.current?.focus();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isMenuOpen]);

  return (
    <header className="glass sticky top-0 z-50 px-6 py-4 md:px-10">
      <div className="flex items-center justify-between">
        <Link
          to="/"
          className="font-[var(--font-display)] text-xl font-semibold tracking-tight text-[var(--color-bone)]"
        >
          Cine<span className="text-[var(--color-marquee)]">Match</span>
        </Link>

        <nav className="hidden items-center gap-6 font-[var(--font-body)] text-sm text-[var(--color-bone-dim)] md:flex">
          {NAV_LINKS.map((link) => (
            <Link key={link.to} to={link.to} className="transition-colors hover:text-[var(--color-bone)]">
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Link
            to="/search"
            aria-label="Search movies"
            className="flex items-center gap-2 rounded-full border border-[var(--color-panel-border)] px-3 py-1.5 text-sm text-[var(--color-bone-dim)] transition-colors hover:border-[var(--color-marquee)] hover:text-[var(--color-bone)]"
          >
            <Search size={16} />
            <span className="hidden sm:inline">Search</span>
          </Link>

          <button
            ref={menuButtonRef}
            type="button"
            onClick={() => setIsMenuOpen((open) => !open)}
            aria-expanded={isMenuOpen}
            aria-controls="mobile-nav-panel"
            aria-label={isMenuOpen ? "Close menu" : "Open menu"}
            className="flex h-9 w-9 items-center justify-center rounded-full border border-[var(--color-panel-border)] text-[var(--color-bone-dim)] transition-colors hover:border-[var(--color-marquee)] hover:text-[var(--color-bone)] md:hidden"
          >
            {isMenuOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </div>

      {isMenuOpen && (
        <nav
          id="mobile-nav-panel"
          aria-label="Mobile navigation"
          className="glass mt-4 flex flex-col gap-1 rounded-xl p-2 md:hidden"
        >
          {NAV_LINKS.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="rounded-lg px-4 py-3 text-sm text-[var(--color-bone-dim)] transition-colors hover:bg-[var(--color-panel-border)] hover:text-[var(--color-bone)]"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
