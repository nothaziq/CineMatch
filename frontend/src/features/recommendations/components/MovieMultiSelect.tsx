import { useQuery } from "@tanstack/react-query";
import { Plus, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useDebounce } from "../../../hooks/useDebounce";
import { searchMovies } from "../../movie/services/movieApi";
import type { MovieOut } from "../../../types/api";

interface MovieMultiSelectProps {
  selected: MovieOut[];
  onAdd: (movie: MovieOut) => void;
  onRemove: (movieId: number) => void;
  atMax: boolean;
  maxSeeds: number;
}

const LISTBOX_ID = "recommendation-seed-listbox";
const optionId = (movieId: number) => `recommendation-seed-option-${movieId}`;

export function MovieMultiSelect({ selected, onAdd, onRemove, atMax, maxSeeds }: MovieMultiSelectProps) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const debouncedQuery = useDebounce(query, 300);
  const selectedIds = new Set(selected.map((m) => m.movie_id));
  const containerRef = useRef<HTMLDivElement>(null);

  const search = useQuery({
    queryKey: ["search", "picker", debouncedQuery],
    queryFn: () => searchMovies(debouncedQuery, 8),
    enabled: debouncedQuery.trim().length > 0,
  });

  const showDropdown = isOpen && debouncedQuery.trim().length > 0;
  const options = (search.data ?? []).filter((m) => !selectedIds.has(m.movie_id));

  // Keep the highlighted option in range whenever the option list changes
  // (new search results, filtering out already-selected movies, etc).
  useEffect(() => {
    if (highlightedIndex >= options.length) {
      setHighlightedIndex(options.length > 0 ? 0 : -1);
    }
  }, [options.length, highlightedIndex]);

  // Close the popup on outside click/focus, per the ARIA combobox pattern.
  useEffect(() => {
    if (!showDropdown) return;
    const handlePointerDown = (event: PointerEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, [showDropdown]);

  const selectMovie = (movie: MovieOut) => {
    onAdd(movie);
    setQuery("");
    setIsOpen(false);
    setHighlightedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showDropdown) {
      if (e.key === "ArrowDown" && query.trim().length > 0) {
        setIsOpen(true);
      }
      return;
    }

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setHighlightedIndex((i) => (options.length === 0 ? -1 : (i + 1) % options.length));
        break;
      case "ArrowUp":
        e.preventDefault();
        setHighlightedIndex((i) => (options.length === 0 ? -1 : (i - 1 + options.length) % options.length));
        break;
      case "Enter":
        if (highlightedIndex >= 0 && options[highlightedIndex]) {
          e.preventDefault();
          selectMovie(options[highlightedIndex]);
        }
        break;
      case "Escape":
        e.preventDefault();
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
      case "Tab":
        setIsOpen(false);
        break;
    }
  };

  return (
    <div ref={containerRef}>
      <div className="relative">
        <label htmlFor="recommendation-seed-search" className="sr-only">
          Search for a movie to add to your favorites
        </label>
        <input
          id="recommendation-seed-search"
          type="text"
          role="combobox"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
            setHighlightedIndex(-1);
          }}
          onFocus={() => {
            if (query.trim().length > 0) setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
          placeholder={
            atMax ? `Max ${maxSeeds} favorites picked` : "Search for a movie to add..."
          }
          disabled={atMax}
          autoComplete="off"
          aria-autocomplete="list"
          aria-expanded={showDropdown}
          aria-controls={LISTBOX_ID}
          aria-activedescendant={
            showDropdown && highlightedIndex >= 0 && options[highlightedIndex]
              ? optionId(options[highlightedIndex].movie_id)
              : undefined
          }
          aria-describedby="recommendation-seed-search-status"
          className="glass w-full rounded-full px-5 py-3.5 font-[var(--font-body)] text-base text-[var(--color-bone)] outline-none placeholder:text-[var(--color-bone-dim)] disabled:opacity-50"
        />

        {/* Visually-hidden live region: announces result counts to screen
            reader users, who otherwise get no feedback when the dropdown
            below updates after they stop typing. */}
        <p id="recommendation-seed-search-status" role="status" className="sr-only">
          {showDropdown && !search.isLoading
            ? `${options.length} result${options.length === 1 ? "" : "s"} found`
            : ""}
        </p>

        {showDropdown && (
          <div
            id={LISTBOX_ID}
            role="listbox"
            aria-label="Movie search results"
            className="glass absolute z-10 mt-2 w-full overflow-hidden rounded-xl"
          >
            {search.isLoading && (
              <p className="px-5 py-3 text-sm text-[var(--color-bone-dim)]">Searching...</p>
            )}

            {!search.isLoading && search.isError && (
              <p className="px-5 py-3 text-sm text-[var(--color-bone-dim)]">
                Couldn't search right now.
              </p>
            )}

            {!search.isLoading && !search.isError && options.length === 0 && (
              <p className="px-5 py-3 text-sm text-[var(--color-bone-dim)]">
                No matches{selectedIds.size > 0 ? " (or already added)" : ""}.
              </p>
            )}

            {!search.isLoading &&
              options.map((movie, index) => (
                <button
                  key={movie.movie_id}
                  id={optionId(movie.movie_id)}
                  role="option"
                  aria-selected={index === highlightedIndex}
                  tabIndex={-1}
                  onMouseEnter={() => setHighlightedIndex(index)}
                  onMouseDown={(e) => {
                    // Prevent input blur from firing (and closing the popup)
                    // before the click's onAdd runs.
                    e.preventDefault();
                  }}
                  onClick={() => selectMovie(movie)}
                  className={`flex w-full items-center justify-between gap-3 px-5 py-3 text-left transition-colors ${
                    index === highlightedIndex
                      ? "bg-[var(--color-panel-border)]"
                      : "hover:bg-[var(--color-panel-border)]"
                  }`}
                >
                  <span className="truncate text-sm text-[var(--color-bone)]">
                    {movie.title}
                    {movie.year && (
                      <span className="ml-2 font-[var(--font-mono)] text-xs text-[var(--color-bone-dim)]">
                        {movie.year}
                      </span>
                    )}
                  </span>
                  <Plus size={16} aria-hidden className="shrink-0 text-[var(--color-marquee)]" />
                </button>
              ))}
          </div>
        )}
      </div>

      {selected.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {selected.map((movie) => (
            <span
              key={movie.movie_id}
              className="glass flex items-center gap-2 rounded-full py-1.5 pl-4 pr-2 text-sm text-[var(--color-bone)]"
            >
              {movie.title}
              <button
                onClick={() => onRemove(movie.movie_id)}
                aria-label={`Remove ${movie.title}`}
                className="rounded-full p-0.5 text-[var(--color-bone-dim)] transition-colors hover:text-[var(--color-bone)]"
              >
                <X size={14} />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
