import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useDebounce } from "../../../hooks/useDebounce";
import { searchMovies } from "../../movie/services/movieApi";

const PAGE_SIZE = 20;
const MAX_LIMIT = 50; // backend hard cap on /movies/search

export function useSearch() {
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(PAGE_SIZE);
  const debouncedQuery = useDebounce(query, 300);

  const result = useQuery({
    queryKey: ["search", debouncedQuery, limit],
    queryFn: () => searchMovies(debouncedQuery, limit),
    enabled: debouncedQuery.trim().length > 0,
    placeholderData: (previous) => previous,
  });

  // Reset paging whenever the (debounced) search term actually changes.
  function updateQuery(next: string) {
    setQuery(next);
    setLimit(PAGE_SIZE);
  }

  const canLoadMore =
    debouncedQuery.trim().length > 0 &&
    limit < MAX_LIMIT &&
    (result.data?.length ?? 0) >= limit;

  function loadMore() {
    setLimit((prev) => Math.min(prev + PAGE_SIZE, MAX_LIMIT));
  }

  return {
    query,
    setQuery: updateQuery,
    isSearching: debouncedQuery.trim().length > 0,
    results: result.data,
    isLoading: result.isLoading,
    isFetching: result.isFetching,
    isError: result.isError,
    canLoadMore,
    loadMore,
  };
}
