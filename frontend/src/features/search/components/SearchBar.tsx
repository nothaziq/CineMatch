import { Search, X } from "lucide-react";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  autoFocus?: boolean;
}

export function SearchBar({ value, onChange, autoFocus }: SearchBarProps) {
  return (
    <div className="glass flex w-full items-center gap-3 rounded-full px-5 py-3.5">
      <Search size={20} aria-hidden className="shrink-0 text-[var(--color-bone-dim)]" />
      <label htmlFor="movie-search-input" className="sr-only">
        Search movies by title
      </label>
      <input
        id="movie-search-input"
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search movies by title..."
        autoFocus={autoFocus}
        className="w-full bg-transparent font-[var(--font-body)] text-base text-[var(--color-bone)] outline-none placeholder:text-[var(--color-bone-dim)]"
      />
      {value && (
        <button
          onClick={() => onChange("")}
          aria-label="Clear search"
          className="shrink-0 text-[var(--color-bone-dim)] transition-colors hover:text-[var(--color-bone)]"
        >
          <X size={18} aria-hidden />
        </button>
      )}
    </div>
  );
}
