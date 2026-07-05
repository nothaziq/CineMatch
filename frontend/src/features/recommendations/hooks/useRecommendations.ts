import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useDebounce } from "../../../hooks/useDebounce";
import { fetchBatchRecommendations } from "../../movie/services/movieApi";
import type { MovieOut } from "../../../types/api";

const MIN_SEEDS = 1;
const MAX_SEEDS = 10; // keep the "favorites" picker focused, not a full catalog dump
const RESULT_COUNT = 20;

export function useRecommendations() {
  const [selected, setSelected] = useState<MovieOut[]>([]);

  // Memoized so this only gets a new reference when `selected` actually
  // changes (add/remove/clear) — not on every unrelated re-render, which
  // would otherwise keep resetting the debounce timer below.
  const seedIds = useMemo(() => selected.map((m) => m.movie_id), [selected]);
  const debouncedSeedIds = useDebounce(seedIds, 400);
  const debouncedKey = JSON.stringify([...debouncedSeedIds].sort((a, b) => a - b));

  const canRecommend = debouncedSeedIds.length >= MIN_SEEDS;

  const result = useQuery({
    queryKey: ["recommendations", "batch", debouncedKey],
    queryFn: () => fetchBatchRecommendations(debouncedSeedIds, RESULT_COUNT),
    enabled: canRecommend,
    placeholderData: (previous) => previous,
  });

  function addMovie(movie: MovieOut) {
    setSelected((prev) => {
      if (prev.some((m) => m.movie_id === movie.movie_id)) return prev;
      if (prev.length >= MAX_SEEDS) return prev;
      return [...prev, movie];
    });
  }

  function removeMovie(movieId: number) {
    setSelected((prev) => prev.filter((m) => m.movie_id !== movieId));
  }

  function clearAll() {
    setSelected([]);
  }

  return {
    selected,
    addMovie,
    removeMovie,
    clearAll,
    atMaxSeeds: selected.length >= MAX_SEEDS,
    maxSeeds: MAX_SEEDS,
    hasEnoughSeeds: canRecommend,
    // isFetching (not isLoading) so the grid can show a subtle "updating"
    // state on re-blend without flashing a full skeleton every time a
    // seed is added/removed — placeholderData keeps stale results visible.
    recommendations: result.data?.recommendations,
    isLoading: result.isLoading,
    isFetching: result.isFetching,
    isError: result.isError,
  };
}
