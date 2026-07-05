import { useNavigate } from "react-router-dom";
import type { MovieOut } from "../../../types/api";
import { ResultsGrid } from "../components/ResultsGrid";
import { SearchBar } from "../components/SearchBar";
import { useSearch } from "../hooks/useSearch";

export function SearchPage() {
  const navigate = useNavigate();
  const {
    query,
    setQuery,
    isSearching,
    results,
    isLoading,
    isFetching,
    isError,
    canLoadMore,
    loadMore,
  } = useSearch();

  const goToMovie = (movie: MovieOut) => navigate(`/movies/${movie.movie_id}`);

  return (
    <div>
      <div className="px-6 pb-2 pt-10 md:px-10">
        <h1 className="mb-6 font-[var(--font-display)] text-3xl font-semibold text-[var(--color-bone)]">
          Search
        </h1>
        <SearchBar value={query} onChange={setQuery} autoFocus />
      </div>

      <ResultsGrid
        results={results}
        isLoading={isLoading}
        isFetching={isFetching}
        isError={isError}
        isSearching={isSearching}
        canLoadMore={canLoadMore}
        onLoadMore={loadMore}
        onSelectMovie={goToMovie}
      />
    </div>
  );
}
