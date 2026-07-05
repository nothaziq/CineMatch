import { useQuery } from "@tanstack/react-query";
import { fetchMovies } from "../../movie/services/movieApi";

export function useTrendingMovies() {
  return useQuery({
    queryKey: ["movies", "trending"],
    queryFn: () => fetchMovies({ sort: "popularity", page_size: 12 }),
  });
}

export function useTopRatedMovies() {
  return useQuery({
    queryKey: ["movies", "top-rated"],
    queryFn: () => fetchMovies({ sort: "top_rated", page_size: 12 }),
  });
}

export function useRecentMovies() {
  return useQuery({
    queryKey: ["movies", "recent"],
    queryFn: () => fetchMovies({ sort: "recent", page_size: 12 }),
  });
}
