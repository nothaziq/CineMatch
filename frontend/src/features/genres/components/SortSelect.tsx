import type { SortOption } from "../../movie/services/movieApi";

interface SortSelectProps {
  value: SortOption;
  onChange: (value: SortOption) => void;
}

const OPTIONS: { value: SortOption; label: string }[] = [
  { value: "popularity", label: "Most Popular" },
  { value: "trending", label: "Trending Now" },
  { value: "top_rated", label: "Top Rated" },
  { value: "recent", label: "Recently Added" },
  { value: "title", label: "Title (A–Z)" },
];

export function SortSelect({ value, onChange }: SortSelectProps) {
  return (
    <>
      <label htmlFor="movie-sort-select" className="sr-only">
        Sort movies by
      </label>
      <select
        id="movie-sort-select"
        value={value}
        onChange={(e) => onChange(e.target.value as SortOption)}
        className="glass rounded-full px-4 py-2 font-[var(--font-body)] text-sm text-[var(--color-bone)] outline-none"
      >
        {OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value} className="bg-[var(--color-panel)]">
            {opt.label}
          </option>
        ))}
      </select>
    </>
  );
}
