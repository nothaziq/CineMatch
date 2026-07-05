import { useQuery } from "@tanstack/react-query";
import { fetchMovieDetail, fetchRecommendations } from "../services/movieApi";

export function useMovieDetail(movieId: number | undefined) {
  return useQuery({
    queryKey: ["movie", movieId],
    queryFn: () => fetchMovieDetail(movieId!),
    enabled: movieId !== undefined,
  });
}

export function useSimilarMovies(movieId: number | undefined, k = 12) {
  return useQuery({
    queryKey: ["recommendations", movieId, k],
    queryFn: () => fetchRecommendations(movieId!, k),
    enabled: movieId !== undefined,
  });
}
